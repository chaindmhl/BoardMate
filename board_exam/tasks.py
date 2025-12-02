# tasks.py
import cv2
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from board_exam.models import Student, Result, AnswerKey

User = get_user_model()

MODEL1_DIR = "/models/model1"
MODEL2_DIR = "/models/model2"

CONF_THRESHOLD = 0.5


def load_yolo_model(model_dir, cfg_name, weights_name, names_name):
    """Load YOLO model and class names"""
    cfg_file = os.path.join(model_dir, cfg_name)
    weights_file = os.path.join(model_dir, weights_name)
    names_file = os.path.join(model_dir, names_name)

    for f in [cfg_file, weights_file, names_file]:
        if not os.path.exists(f):
            raise FileNotFoundError(f"YOLO model file missing: {f}")

    net = cv2.dnn.readNet(weights_file, cfg_file)
    with open(names_file) as f:
        classes = f.read().strip().split("\n")
    return net, classes


def run_yolo_inference(net, classes, image):
    """Run YOLO detection and return detected class names"""
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    detected_classes = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = int(scores.argmax())
            confidence = scores[class_id]
            if confidence > CONF_THRESHOLD:
                detected_classes.append(class_id)

    return [classes[cid] for cid in detected_classes if cid < len(classes)]


def process_uploaded_answer(relative_image_path, exam_id, user_id):
    """Process uploaded answer image, run YOLO, and save result"""

    image_path = os.path.join(settings.MEDIA_ROOT, relative_image_path)
    if not os.path.exists(image_path):
        print("❌ IMAGE NOT FOUND:", image_path)
        return

    image = cv2.imread(image_path)
    if image is None:
        print("❌ FAILED TO READ IMAGE:", image_path)
        return

    # Load YOLO models inside the task (fork-safe)
    net_original, classes_original = load_yolo_model(
        MODEL1_DIR, "model1.cfg", "model1.weights", "model1.names"
    )
    net_cropped, classes_cropped = load_yolo_model(
        MODEL2_DIR, "model2.cfg", "model2.weights", "model2.names"
    )

    original_detections = run_yolo_inference(net_original, classes_original, image)
    cropped_detections = run_yolo_inference(net_cropped, classes_cropped, image)

    score = len(cropped_detections)  # simple scoring logic

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

    print(f"✅ Processed {relative_image_path}: score={score}")
