import os
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from board_exam.models import Result, Student, AnswerKey

COLAB_URL = getattr(settings, "COLAB_URL", None)
if not COLAB_URL:
    raise ValueError("COLAB_URL must be set in settings.py")

def process_uploaded_answer(user_id: int, exam_id: str, image_path: str):
    """
    Sends the uploaded answer image to Colab for processing,
    then stores the result in the database.
    """

    # Ensure the file exists
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}

    # Fetch student
    student = get_object_or_404(Student, user_id=user_id)

    # Fetch answer key
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    # Send image to Colab
    try:
        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"exam_id": exam_id, "user_id": user_id}
            response = requests.post(COLAB_URL, files=files, data=data)
            response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to process image: {str(e)}"}

    result_data = response.json()
    submitted_answers = result_data.get("submitted_answers", [])
    score = result_data.get("score", 0)

    # Correct answers
    correct_answers = answer_key.answer_key
    if isinstance(correct_answers, dict):
        correct_list = [v["letter"] for v in correct_answers.values()]
    elif isinstance(correct_answers, list):
        correct_list = correct_answers
    else:
        correct_list = []

    # Save or update result
    Result.objects.update_or_create(
        user_id=user_id,
        exam_id=exam_id,
        defaults={
            "student_id": student.student_id,
            "course": student.course,
            "student_name": f"{student.last_name}, {student.first_name} {student.middle_name or ''}".strip(),
            "subject": answer_key.subject,
            "answer": submitted_answers,
            "correct_answer": correct_list,
            "score": score,
            "is_submitted": True,
            "total_items": len(correct_list)
        }
    )

    return {"score": score, "submitted_answers": submitted_answers}
