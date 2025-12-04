# board_exam/tasks.py
import os
import json
import time
import base64
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from board_exam.models import Result, Student, AnswerKey

# must be like: https://xxxxx.ngrok-free.app/process_answer
COLAB_URL = settings.COLAB_URL


def process_uploaded_answer(user_id, exam_id, image_path, *args, **kwargs):
    start_time = time.time()
    print("[TASK] Started process_uploaded_answer")
    print(f"[TASK] user_id={user_id}, exam_id={exam_id}, image_path={image_path}")

    # validate incoming file
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found: {image_path}")
        return {"error": "Image file does not exist"}

    student = get_object_or_404(Student, user_id=user_id)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    # correct answers mapping
    try:
        correct_answers = {str(k): v['letter'] for k, v in answer_key.answer_key.items()}
    except Exception:
        if isinstance(answer_key.answer_key, list):
            correct_answers = {str(i + 1): v for i, v in enumerate(answer_key.answer_key)}
        else:
            correct_answers = {}

    # send request to Colab
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
            if getattr(e, "response", None) is not None:
                try:
                    server_body = e.response.json()
                except Exception:
                    server_body = e.response.text
                print(f"[ERROR] Failed to send to Colab: {str(e)} | Body: {server_body}")
            else:
                print(f"[ERROR] Failed to send to Colab (no response): {str(e)}")
            return {"error": str(e)}

    # parse JSON
    try:
        result_data = response.json()
    except Exception:
        print("[ERROR] Non-JSON response from Colab:")
        print(response.text)
        return {"error": "Invalid response from Colab"}

    elapsed = round(time.time() - start_time, 2)

    # extract submitted answers
    submitted_answers = []
    if "submitted_answers" in result_data:
        try:
            submitted_answers = [
                v["letter"]
                for k, v in sorted(
                    result_data["submitted_answers"].items(),
                    key=lambda x: int(x[0])
                )
            ]
        except Exception:
            try:
                submitted_answers = list(result_data["submitted_answers"].values())
            except Exception:
                submitted_answers = []

    score = result_data.get("score", 0)
    total_items = result_data.get("total_items", len(correct_answers))

    # ------------------------------------------------------------
    #  SAVE ANNOTATED IMAGE FROM COLAB (NEW)
    # ------------------------------------------------------------
    annotated_path = None
    annotated_b64 = result_data.get("annotated_image_base64")

    if annotated_b64:
        try:
            img_bytes = base64.b64decode(annotated_b64)
            file_name = f"annotated_{user_id}_{exam_id}.png"
            annotated_path = f"annotated/{file_name}"

            # ensure directory exists
            full_path = os.path.join(settings.MEDIA_ROOT, annotated_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "wb") as img_file:
                img_file.write(img_bytes)

            print(f"[TASK] Annotated image saved: {annotated_path}")

        except Exception as e:
            print(f"[ERROR] Failed to decode/save annotated image: {str(e)}")
            annotated_path = None
    else:
        print("[TASK] No annotated image returned from Colab.")

    # ------------------------------------------------------------
    # SAVE RESULT TO DATABASE
    # ------------------------------------------------------------
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
            "elapsed_time": str(elapsed),
            "annotated_image": annotated_path,   # <-- added
        }
    )

    print(f"[TASK] Finished user_id={user_id}, exam_id={exam_id}, score={score}, time={elapsed}s")
    return {
        "score": score,
        "submitted_answers": submitted_answers,
        "annotated_image": annotated_path,
        "elapsed_time": elapsed
    }
