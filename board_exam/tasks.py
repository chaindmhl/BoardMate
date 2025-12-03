import requests
from django.conf import settings
from board_exam.models import Result, Student

def process_uploaded_answer(file_path, exam_id, user_id, correct_answers):
    url = settings.COLAB_URL + "/process_answer"

    with open(file_path, 'rb') as f:
        response = requests.post(url, files={"image": f},
                                 data={"exam_id": exam_id,
                                       "correct_answers": correct_answers})
    result_json = response.json()

    Result.objects.update_or_create(
        user_id=user_id,
        exam_id=exam_id,
        defaults={
            "score": result_json.get("score", 0),
            "total_items": result_json.get("total_items", 0),
            "answer": list(result_json.get("seq_num_class_dict", {}).values()),
            "correct_answer": list(correct_answers.values()),
            "is_submitted": True
        }
    )
