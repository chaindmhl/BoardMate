# board_exam/tasks.py
import os
import json
import time
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from board_exam.models import Result, Student, AnswerKey

# settings.COLAB_URL must be like "https://xxxxx.ngrok-free.dev/process_answer"
COLAB_URL = settings.COLAB_URL

def process_uploaded_answer(user_id, exam_id, image_path, *args, **kwargs):
    start_time = time.time()
    print("[TASK] Started process_uploaded_answer")
    print(f"[TASK] user_id={user_id}, exam_id={exam_id}, image_path={image_path}")

    # validate file
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found: {image_path}")
        return {"error": "Image file does not exist"}

    student = get_object_or_404(Student, user_id=user_id)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)
    # prepare correct answers mapping str(seq) -> letter
    try:
        correct_answers = {str(k): v['letter'] for k, v in answer_key.answer_key.items()}
    except Exception:
        # fallback: if answer_key.answer_key is list
        if isinstance(answer_key.answer_key, list):
            correct_answers = {str(i+1): v for i, v in enumerate(answer_key.answer_key)}
        else:
            correct_answers = {}

    # send to Colab
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {
            "exam_id": exam_id,
            "user_id": user_id,
            "correct_answers": json.dumps(correct_answers)
        }

        try:
            response = requests.post(COLAB_URL, files=files, data=data, timeout=60)
            response.raise_for_status()
        except requests.RequestException as e:
            # try to print server response body if available
            if getattr(e, "response", None) is not None:
                try:
                    server_body = e.response.json()
                except Exception:
                    server_body = e.response.text
                print(f"[ERROR] Failed to send image to Colab: {str(e)} | Response: {server_body}")
            else:
                print(f"[ERROR] Failed to send image to Colab (no response): {str(e)}")
            return {"error": str(e)}

    # parse result
    try:
        result_data = response.json()
    except Exception as e:
        print("[ERROR] Colab returned non-JSON response:", response.text)
        return {"error": "Invalid response from Colab"}

    elapsed = round(time.time() - start_time, 2)

    # submitted answers: Colab returns dict seq -> {"letter": "X"}
    submitted_answers = []
    if "submitted_answers" in result_data:
        try:
            submitted_answers = [v["letter"] for k, v in sorted(result_data["submitted_answers"].items(), key=lambda x:int(x[0]))]
        except Exception:
            # fallback if values are not dicts
            try:
                submitted_answers = list(result_data["submitted_answers"].values())
            except Exception:
                submitted_answers = []

    score = result_data.get("score", 0)
    total_items = result_data.get("total_items", len(correct_answers))

    # save/update Result
    Result.objects.update_or_create(
        user_id=user_id,
        exam_id=exam_id,
        defaults={
            "student_id": student.student_id,
            "course": student.course,
            "student_name": f"{student.last_name}, {student.first_name} {student.middle_name or ''}".strip(),
            "subject": answer_key.subject,
            "answer": submitted_answers,
            "correct_answer": list(correct_answers.values()),
            "score": score,
            "is_submitted": True,
            "total_items": total_items,
            "elapsed_time": str(elapsed)
        }
    )

    print(f"[TASK] Finished processing user_id={user_id} exam_id={exam_id}, score={score}, elapsed_time={elapsed}s")
    return {"score": score, "submitted_answers": submitted_answers, "elapsed_time": elapsed}
