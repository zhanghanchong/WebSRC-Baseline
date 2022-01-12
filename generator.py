import csv
import os
import re
import string


def normalize_answer(answer):
    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_articles(text):
        regex = re.compile(r'\b(a|an|the)\b', re.UNICODE)
        return re.sub(regex, ' ', text)

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(answer))))


def generate_dataset():
    os.mkdir('dataset')
    os.system('cp -r ./data/* ./dataset')
    for root, _, filenames in os.walk('./dataset'):
        for filename in filenames:
            if filename != 'dataset.csv':
                continue
            with open(os.path.join(root, filename), 'r') as file:
                questions_info = list(csv.DictReader(file))
            with open(os.path.join(root, filename), 'w', newline='') as file:
                csv_writer = csv.DictWriter(file, ['id', 'question'])
                csv_writer.writeheader()
                for question_info in questions_info:
                    csv_writer.writerow({
                        'id': question_info['id'],
                        'question': question_info['question']
                    })


def generate_answer():
    os.mkdir('answer')
    os.system('cp -r ./data/* ./answer')
    for root, _, filenames in os.walk('./answer'):
        for filename in filenames:
            if not filename.endswith('.csv') and not filename.endswith('.html'):
                os.remove(os.path.join(root, filename))
                continue
            if filename != 'dataset.csv':
                continue
            with open(os.path.join(root, filename), 'r') as file:
                questions_info = list(csv.DictReader(file))
            with open(os.path.join(root, filename), 'w', newline='') as file:
                csv_writer = csv.DictWriter(file, ['id', 'answer', 'answer_start', 'tag'])
                csv_writer.writeheader()
                for question_info in questions_info:
                    csv_writer.writerow({
                        'id': question_info['id'],
                        'answer': question_info['answer'] if normalize_answer(question_info['answer']) else '',
                        'answer_start': question_info['answer_start'],
                        'tag': question_info['element_id']
                    })


generate_dataset()
generate_answer()
