# tasks.py
import cv2, os, time, uuid
from board_exam.models import Student, Result, AnswerKey
from django.shortcuts import get_object_or_404

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

    # Load image
    image = cv2.imread(image_path)

    # Convert to mask
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # TODO: Run your detect_objects / crop / scoring logic here
    # For brevity, assume you compute:
    score = 0

    # Save Result to DB
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
        is_submitted=True
    )
