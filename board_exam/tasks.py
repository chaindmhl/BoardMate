# board_exam/tasks.py
import os
import cv2
import numpy as np
from django.conf import settings
from django_q.tasks import async_task
from django.shortcuts import get_object_or_404
from board_exam.models import Result, Student, AnswerKey

def run_yolo_inference(net, classes, img, conf_threshold=0.5):
    """
    Runs YOLO object detection and returns detected class names.
    """
    blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    detected_classes = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = int(scores.argmax())
            confidence = scores[class_id]
            if confidence > conf_threshold:
                detected_classes.append(class_id)
    return [classes[cid] for cid in detected_classes if cid < len(classes)]


def process_uploaded_answer(user_id, exam_id, image_path):
    """
    Background task to process uploaded answer image.
    """
    # Fetch student and answer key
    student = get_object_or_404(Student, user_id=user_id)
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)
    
    # Load YOLO models (make sure paths are correct)
    model1_dir = os.path.join(settings.BASE_DIR, 'model1', 'model1')
    model2_dir = os.path.join(settings.BASE_DIR, 'model2', 'model2')

    net_original = cv2.dnn.readNet(os.path.join(model1_dir, 'model1.weights'),
                                   os.path.join(model1_dir, 'model1.cfg'))
    with open(os.path.join(model1_dir, 'model1.names')) as f:
        classes_original = [line.strip() for line in f.readlines()]

    net_cropped = cv2.dnn.readNet(os.path.join(model2_dir, 'model2.weights'),
                                  os.path.join(model2_dir, 'model2.cfg'))
    with open(os.path.join(model2_dir, 'model2.names')) as f:
        classes_cropped = [line.strip() for line in f.readlines()]

    # Read uploaded image
    img = cv2.imread(image_path)
    if img is None:
        return {"error": "Image could not be read"}

    # First model inference
    original_detections = run_yolo_inference(net_original, classes_original, img)

    # Second model inference on cropped objects
    cropped_detections = run_yolo_inference(net_cropped, classes_cropped, img)

    # Prepare submitted answers for scoring
    submitted_answers = cropped_detections
    correct_answers = {str(k): v['letter'] for k, v in answer_key.answer_key.items()}

    # Compute score
    score = 0
    for seq_num, submitted in enumerate(submitted_answers, start=1):
        correct = correct_answers.get(str(seq_num))
        if correct is not None and submitted == correct:
            score += 1

    # Save result to database (update_or_create ensures unique user/exam_id)
    Result.objects.update_or_create(
        user_id=user_id,
        exam_id=exam_id,
        defaults={
            "student_id": student.student_id,
            "course": student.course,
            "student_name": student.full_name,  # Or str(student)
            "subject": answer_key.subject,
            "answer": submitted_answers,
            "correct_answer": list(correct_answers.values()),
            "score": score,
            "is_submitted": True,
            "total_items": len(correct_answers)
        }
    )

    return {"score": score, "original_detections": original_detections, "cropped_detections": cropped_detections}
