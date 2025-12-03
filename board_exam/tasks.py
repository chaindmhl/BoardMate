# tasks.py
import os
import time
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from board_exam.models import Result, Student, AnswerKey

COLAB_URL = settings.COLAB_URL  # Set to your ngrok public URL + "/process_answer"

def process_uploaded_answer(user_id, exam_id, image_path, *args, **kwargs):
    start_time = time.time()
    print("[TASK] Started process_uploaded_answer")
    print(f"[TASK] user_id={user_id}, exam_id={exam_id}, image_path={image_path}")

    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found: {image_path}")
        return {"error": "Image file does not exist"}

    student = get_object_or_404(Student, user_id=user_id)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)
    correct_answers = {str(k): v['letter'] for k, v in answer_key.answer_key.items()}

    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"exam_id": exam_id, "user_id": user_id, "correct_answers": correct_answers}
        try:
            response = requests.post(COLAB_URL, files=files, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to send image to Colab: {str(e)}")
            return {"error": f"Failed to process image: {str(e)}"}

    result_data = response.json()
    elapsed = round(time.time() - start_time, 2)

    submitted_answers = []
    if "submitted_answers" in result_data:
        submitted_answers = [v["letter"] for v in result_data["submitted_answers"].values()]

    score = result_data.get("score", 0)
    total_items = result_data.get("total_items", len(correct_answers))

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
