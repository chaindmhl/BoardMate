# tasks.py
import os
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from board_exam.models import Student, Result, AnswerKey

User = get_user_model()

# Colab Flask API endpoint (from ngrok)
COLAB_API_URL = "https://kasi-releasible-conscionably.ngrok-free.dev/process_answer"

def process_uploaded_answer(relative_image_path, exam_id, user_id):
    """
    Send uploaded answer image to Colab for YOLO processing,
    receive the results, and save them to the DB.
    """
    image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)
    if not os.path.exists(image_path):
        print("❌ IMAGE NOT FOUND:", image_path)
        return

    # Load user and related objects
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print("❌ User not found:", user_id)
        return

    student = get_object_or_404(Student, user=user)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    # Send image to Colab API
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"exam_id": exam_id, "user_id": user_id}
        try:
            response = requests.post(COLAB_API_URL, files=files, data=data, timeout=120)
            response.raise_for_status()
            result_data = response.json()
        except Exception as e:
            print("❌ Colab processing failed:", e)
            return

    # Example response: {"score": 12, "original_detections": [...], "cropped_detections": [...]}
    score = result_data.get("score", 0)
    original_detections = result_data.get("original_detections", [])
    cropped_detections = result_data.get("cropped_detections", [])

    # Save result in DB
    Result.objects.create(
        user=user,
        student_id=student.student_id,
        course=student.course,
        student_name=str(student),
        subject=answer_key.subject,
        exam_id=exam_id,
        score=score,
        is_submitted=True,
    )

    print(f"✅ Processed {relative_image_path}: score={score}, "
          f"original={original_detections}, cropped={cropped_detections}")
