# tasks.py
import os
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from board_exam.models import Student, Result, AnswerKey

User = get_user_model()

# 🔥 Your ngrok public API URL from Colab
COLAB_API_URL = "https://kasi-releasible-conscionably.ngrok-free.dev/predict"


def process_uploaded_answer(relative_image_path, exam_id, user_id):
    """Send image to Google Colab for YOLO processing"""

    image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)

    if not os.path.exists(image_path):
        print("❌ IMAGE NOT FOUND:", image_path)
        return

    # --------------------------
    # 1️⃣ SEND IMAGE TO COLAB API
    # --------------------------
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(COLAB_API_URL, files=files, timeout=60)

        if response.status_code != 200:
            print("❌ Colab returned error:", response.text)
            return

        result = response.json()
        print("🔎 RESULT FROM COLAB:", result)

    except Exception as e:
        print("❌ ERROR sending to Colab:", str(e))
        return

    # result = {"detections_original": [...], "detections_cropped": [...], "score": 5}
    score = result.get("score", 0)

    # --------------------------
    # 2️⃣ SAVE RESULTS TO DATABASE
    # --------------------------
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print("❌ User not found:", user_id)
        return

    student = get_object_or_404(Student, user=user)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

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

    print(f"✅ FINISHED PROCESSING {relative_image_path} — SCORE={score}")
