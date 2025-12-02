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

# Confidence threshold for YOLO detection
CONF_THRESHOLD = 0.5

# Dictionary to cache models per worker
_worker_models = {}

def load_yolo_model(model_dir, cfg_name, weights_name, names_name):
    """Load YOLO model and class names given exact filenames"""
    cfg_file = os.path.join(model_dir, cfg_name)
    weights_file = os.path.join(model_dir, weights_name)
    names_file = os.path.join(model_dir, names_name)

    # Check if files exist
    for f in [cfg_file, weights_file, names_file]:
        if not os.path.exists(f):
            raise FileNotFoundError(f"YOLO model file missing: {f}")

    net = cv2.dnn.readNet(weights_file, cfg_file)

    with open(names_file) as f:
        classes = f.read().strip().split("\n")

    return net, classes

def get_worker_models():
    """
    Load YOLO models once per worker (singleton).
    Ensures safe loading in Django-Q workers.
    """
    if not _worker_models:
        _worker_models["original"], _worker_models["original_classes"] = load_yolo_model(
            MODEL1_DIR, "model1.cfg", "model1.weights", "model1.names"
        )
        _worker_models["cropped"], _worker_models["cropped_classes"] = load_yolo_model(
            MODEL2_DIR, "model2.cfg", "model2.weights", "model2.names"
        )
    return _worker_models

def run_yolo_inference(net, image, classes):
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
    
    print("Detected class IDs:", detected_classes)
    print("Corresponding names:", [classes[class_id] for class_id in detected_classes if class_id < len(classes)])

    return detected_classes

def process_uploaded_answer(relative_image_path, exam_id, user_id):
    """
    Process an uploaded answer image:
    - Runs YOLO models
    - Computes score
    - Saves result to the DB
    """
    # Load models safely inside the worker
    models = get_worker_models()
    net_original = models["original"]
    classes_original = models["original_classes"]
    net_cropped = models["cropped"]
    classes_cropped = models["cropped_classes"]

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
    original_detections = run_yolo_inference(net_original, image, classes_original)
    cropped_detections = run_yolo_inference(net_cropped, image, classes_cropped)

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
