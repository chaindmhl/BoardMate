import xml.etree.ElementTree as ET
import re
from board_exam.models import Question  # Import your Django model here

def strip_tags(html):
    # Regular expression to remove HTML tags
    return re.sub('<[^<]+?>', '', html)

def extract_and_save_questions(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Iterate over each question
    for question in root.findall('.//question'):
        # Check if 'questiontext' tag exists
        question_text_element = question.find('questiontext/text')
        if question_text_element is not None:
            question_text = strip_tags(question_text_element.text.strip())
        else:
            question_text = ''

        # Initialize variables to store correct answer and choices
        correct_answer = ''
        choices = []

        # Iterate over each answer
        for answer in question.findall('answer'):
            text = strip_tags(answer.find('text').text.strip())
            fraction = int(answer.get('fraction'))
            choices.append((text, fraction))
            if fraction == 100:
                correct_answer = text

        # Create an instance of your Django model and save it to the database
        question_instance = Question.objects.create(
            question_text=question_text,
            choiceA=choices[0][0],
            choiceB=choices[1][0],
            choiceC=choices[2][0],
            choiceD=choices[3][0],
            choiceE=choices[4][0],
            correct_answer=correct_answer
        )

# Usage
xml_file = '/media/icebox/2TB/extract_data/questions-test-top-20240405-1437.xml'
extract_and_save_questions(xml_file)
