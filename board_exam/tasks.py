import cv2, os, time, uuid
from board_exam.models import Student, Result, AnswerKey
from django.shortcuts import get_object_or_404
from django.conf import settings

BASE_DIR = settings.BASE_DIR  # /app inside the container

MODEL1_DIR = os.path.join(BASE_DIR, "model1")
MODEL2_DIR = os.path.join(BASE_DIR, "model2")

def process_uploaded_answer(image_path, exam_id, user_id):
    # Load YOLO model 1
    net_original = cv2.dnn.readNet(
        os.path.join(MODEL1_DIR, "model1.weights"),
        os.path.join(MODEL1_DIR, "model1.cfg")
    )
    with open(os.path.join(MODEL1_DIR, "model1.names")) as f:
        classes_original = f.read().strip().split("\n")

    # Load YOLO model 2
    net_cropped = cv2.dnn.readNet(
        os.path.join(MODEL2_DIR, "model2.weights"),
        os.path.join(MODEL2_DIR, "model2.cfg")
    )
    with open(os.path.join(MODEL2_DIR, "model2.names")) as f:
        classes_cropped = f.read().strip().split("\n")

    # Read uploaded image
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Could not read uploaded image:", image_path)
        return

    # Your processing here...
    score = 0  # Replace with real score

    # Save DB result
    student = get_object_or_404(Student, user_id=user_id)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    Result.objects.create(
        user=user_id,
        student_id=student.student_id,
        course=student.course,
        student_name=student,
        subject=answer_key.subject,
        exam_id=exam_id,
        score=score,
        is_submitted=True,
    )
