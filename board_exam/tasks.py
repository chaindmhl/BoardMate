# board_exam/tasks.py
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from board_exam.models import Result, Student, AnswerKey

def process_uploaded_answer(user_id, exam_id, image_path):
    """
    Background task to process uploaded answer image entirely via Colab.
    """
    # Fetch student and answer key
    student = get_object_or_404(Student, user_id=user_id)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    # Make sure COLAB_URL is defined
    if not hasattr(settings, "COLAB_URL") or not settings.COLAB_URL:
        return {"error": "COLAB_URL is not set in settings."}

    url = settings.COLAB_URL + "/process_answer"  # Colab endpoint
    files = {"image": open(image_path, "rb")}
    data = {"user_id": user_id, "exam_id": exam_id}

    try:
        # Send image to Colab for processing
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        result_data = response.json()
    except Exception as e:
        print("Colab processing failed:", e)
        return {"error": str(e)}

    # Save the result returned by Colab
    score = result_data.get("score")
    submitted_answers = result_data.get("submitted_answers", [])
    correct_answers = result_data.get("correct_answers", [])

    Result.objects.update_or_create(
        user_id=user_id,
        exam_id=exam_id,
        defaults={
            "student_id": student.student_id,
            "course": student.course,
            "student_name": f"{student.last_name}, {student.first_name} {student.middle_name}",
            "subject": answer_key.subject,
            "answer": submitted_answers,
            "correct_answer": list(correct_answers.values()),
            "score": score,
            "is_submitted": True,
            "total_items": len(correct_answers)
        }
    )

    return result_data
