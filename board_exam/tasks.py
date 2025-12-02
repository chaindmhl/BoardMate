# tasks.py
import cv2
import os
import time
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from board_exam.models import Student, Result, AnswerKey

User = get_user_model()

# Base directories for YOLO models inside the container
BASE_DIR = settings.BASE_DIR
MODEL1_DIR = os.path.join(BASE_DIR, "model1")
MODEL2_DIR = os.path.join(BASE_DIR, "model2")

# Confidence threshold for YOLO detection
CONF_THRESHOLD = 0.5

def load_yolo_model(model_dir):
    """Load YOLO model and class names"""
    net = cv2.dnn.readNet(
        os.path.join(model_dir, os.listdir(model_dir)[1]),  # .weights
        os.path.join(model_dir, os.listdir(model_dir)[0])   # .cfg
    )
    names_file = [f for f in os.listdir(model_dir) if f.endswith(".names")][0]
    with open(os.path.join(model_dir, names_file)) as f:
        classes = f.read().strip().split("\n")
    return net, classes

# Load YOLO models once
NET_ORIGINAL, CLASSES_ORIGINAL = load_yolo_model(MODEL1_DIR)
NET_CROPPED, CLASSES_CROPPED = load_yolo_model(MODEL2_DIR)

def run_yolo_inference(net, image):
    """Run YOLO detection and return detected classes"""
    height, width = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getUnconnectedOutLayersNames()
    outputs = net.forward(layer_names)

    detected_classes = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = int(scores.argmax())
            confidence = scores[class_id]
            if confidence > CONF_THRESHOLD:
                detected_classes.append(class_id)
    return detected_classes

def process_uploaded_answer(relative_image_path, exam_id, user_id):
    """
    Process an uploaded answer image:
    - Runs YOLO models
    - Computes score
    - Saves result to the DB
    """
    # Build absolute path for Railway
    image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)
    if not os.path.exists(image_path):
        print("❌ IMAGE NOT FOUND:", image_path)
        return

    image = cv2.imread(image_path)
    if image is None:
        print("❌ FAILED TO READ IMAGE:", image_path)
        return

    # Run YOLO inference
    original_detections = run_yolo_inference(NET_ORIGINAL, image)
    cropped_detections = run_yolo_inference(NET_CROPPED, image)

    # Compute a simple score: count matches vs AnswerKey
    # (replace with your actual scoring logic)
    score = len(cropped_detections)  # Example: number of cropped items detected

    # Load user and student
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print("❌ User not found:", user_id)
        return

    student = get_object_or_404(Student, user=user)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    # Save result
    Result.objects.create(
        user=user,  # must be user object
        student_id=student.student_id,
        course=student.course,
        student_name=str(student),
        subject=answer_key.subject,
        exam_id=exam_id,
        score=score,
        is_submitted=True,
    )

    print(f"✅ Processed {relative_image_path}: score={score}")
