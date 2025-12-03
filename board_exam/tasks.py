# board_exam/tasks.py
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from board_exam.models import Result, Student, AnswerKey

def process_uploaded_answer(*args, **kwargs):
    """
    Background task to process an uploaded answer image via Colab.
    Accepts extra args sent by Django-Q.
    """
    user_id = args[0]
    exam_id = args[1]
    image_path = args[2]

    # Fetch student and answer key
    student = get_object_or_404(Student, user_id=user_id)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    # Send request to Colab for processing
    colab_url = settings.COLAB_URL + "/process_answer"  # Make sure COLAB_URL is set in settings.py
    files = {"image": open(image_path, "rb")}
    data = {"user_id": user_id, "exam_id": exam_id}
    
    try:
        response = requests.post(colab_url, files=files, data=data)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Colab request failed: {str(e)}"}

    result_data = response.json()
    
    # Extract results from Colab response
    submitted_answers = result_data.get("submitted_answers", [])
    score = result_data.get("score", 0)
    original_detections = result_data.get("original_detections", [])
    cropped_detections = result_data.get("cropped_detections", [])

    # Correct answers are stored as a list in AnswerKey
    correct_answers = answer_key.answer_key
    total_items = len(correct_answers)

    # Save or update Result in database
    Result.objects.update_or_create(
        user_id=user_id,
        exam_id=exam_id,
        defaults={
            "student_id": student.student_id,
            "course": student.course,
            "student_name": f"{student.last_name}, {student.first_name} {student.middle_name}",
            "subject": answer_key.subject,
            "answer": submitted_answers,
            "correct_answer": correct_answers,
            "score": score,
            "is_submitted": True,
            "total_items": total_items
        }
    )

    return {
        "score": score,
        "original_detections": original_detections,
        "cropped_detections": cropped_detections
    }
