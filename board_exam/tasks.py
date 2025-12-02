# tasks.py
import cv2, os, time, uuid
from board_exam.models import Student, Result, AnswerKey
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

def process_uploaded_answer(image_path, exam_id, user_id):
    # Load models (once if possible)
    MODEL1_DIR = "model1"
    MODEL2_DIR = "model2"
    net_original = cv2.dnn.readNet(os.path.join(MODEL1_DIR, "model1.weights"),
                                   os.path.join(MODEL1_DIR, "model1.cfg"))
    with open(os.path.join(MODEL1_DIR, "model1.names")) as f:
        classes_original = [line.strip() for line in f.readlines()]
    
    net_cropped = cv2.dnn.readNet(os.path.join(MODEL2_DIR, "model2.weights"),
                                  os.path.join(MODEL2_DIR, "model2.cfg"))
    with open(os.path.join(MODEL2_DIR, "model2.names")) as f:
        classes_cropped = [line.strip() for line in f.readlines()]

    # 1) Build absolute path (Railway needs this)
    image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)

    if not os.path.exists(image_path):
        print("❌ IMAGE NOT FOUND:", image_path)
        return

    image = cv2.imread(image_path)
    if image is None:
        print("❌ FAILED TO READ IMAGE:", image_path)
        return

    # 2) Convert to mask
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # TODO: Run your detect_objects / crop / scoring logic here
    # For brevity, assume you compute:
    score = 0

    # 3) Load DB objects
    user = User.objects.get(id=user_id)
    student = get_object_or_404(Student, user=user)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)
    Result.objects.create(
        user=user_id,
        student_id=student.student_id,
        course=student.course,
        student_name=student,
        subject=answer_key.subject,
        exam_id=exam_id,
        score=score,
        is_submitted=True
    )
