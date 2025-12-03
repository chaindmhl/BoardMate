import os
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from board_exam.models import Result, Student, AnswerKey

COLAB_URL = settings.COLAB_URL + "/process_answer"

def process_uploaded_answer(user_id, exam_id, image_path):
    """
    Sends the uploaded answer image to Colab for processing,
    then stores the result in the database.
    """
    # Log received arguments for debugging
    print("[TASK] Started process_uploaded_answer")
    print(f"[TASK] user_id={user_id}, exam_id={exam_id}, image_path={image_path}")

    # Ensure user_id is int
    try:
        user_id = int(user_id)
    except ValueError:
        print(f"[ERROR] user_id is not an integer: {user_id}")
        return {"error": "Invalid user_id"}

    # Check if image exists
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found: {image_path}")
        return {"error": "Image file does not exist"}

    # Fetch student
    student = get_object_or_404(Student, user_id=user_id)

    # Fetch answer key
    answer_key = get_object_or_404(AnswerKey, set_id=exam_id)

    # Send image to Colab
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"exam_id": exam_id, "user_id": user_id}
        try:
            response = requests.post(COLAB_URL, files=files, data=data)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to send image to Colab: {str(e)}")
            return {"error": f"Failed to process image: {str(e)}"}

    result_data = response.json()
    submitted_answers = result_data.get("submitted_answers", [])
    score = result_data.get("score", 0)

    # Correct answers from AnswerKey
    correct_answers = answer_key.answer_key
    correct_list = [v["letter"] for v in correct_answers.values()] if isinstance(correct_answers, dict) else list(correct_answers)

    # Save or update result
    Result.objects.update_or_create(
        user_id=user_id,
        exam_id=exam_id,
        defaults={
            "student_id": student.student_id,
            "course": student.course,
            "student_name": f"{student.last_name}, {student.first_name} {student.middle_name or ''}".strip(),
            "subject": answer_key.subject,
            "answer": submitted_answers,   # this should be the real answers
            "correct_answer": correct_list,
            "score": score,
            "is_submitted": True,
            "total_items": len(correct_list),
            "elapsed_time": elapsed
        }
    )


    print(f"[TASK] Finished processing user_id={user_id} exam_id={exam_id}, score={score}")
    return {"score": score, "submitted_answers": submitted_answers}
