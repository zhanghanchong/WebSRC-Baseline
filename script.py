import collections
import csv
import json
import os
import re
import string
from bs4 import BeautifulSoup


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


def get_tokens(text):
    return [] if not text else normalize_answer(text).split()


def get_exact_score(gold, pred):
    return int(normalize_answer(gold) == normalize_answer(pred))


def get_f1_score(gold, pred):
    gold_tokens = get_tokens(gold)
    pred_tokens = get_tokens(pred)
    count_same = sum((collections.Counter(gold_tokens) & collections.Counter(pred_tokens)).values())
    if len(gold_tokens) == 0 or len(pred_tokens) == 0:
        return int(gold_tokens == pred_tokens)
    if count_same == 0:
        return 0
    precision = count_same / len(pred_tokens)
    recall = count_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def get_pos_score(gold, addition, pred, html_code):
    h = BeautifulSoup(html_code, features='html.parser')
    e_gold, e_pred = h.find(tid=gold), h.find(tid=pred)
    if e_gold is None:
        e_prev = h.find(tid=pred-1)
        return int((e_pred is None) and ((addition == 0 and e_prev is not None) or (addition == 1 and e_prev is None)))
    if e_pred is None:
        return 0
    p_gold = {gold}
    for e in e_gold.parents:
        if int(e['tid']) < 2:
            break
        p_gold.add(int(e['tid']))
    p_pred = {pred}
    if e_pred.name != 'html':
        for e in e_pred.parents:
            if int(e['tid']) < 2:
                break
            p_pred.add(int(e['tid']))
    return len(p_gold & p_pred) / len(p_gold | p_pred)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
result = {}
with open('./result.txt', 'r') as file:
    for line_text in file.read().split('\n'):
        if len(line_text) == 0:
            break
        single_result = json.loads(line_text)
        result[single_result['id']] = {
            'answer': single_result['answer'],
            'tag': single_result['tag']
        }
count_data, exact_score, f1_score, pos_score = 0, 0, 0, 0
for root, _, filenames in os.walk('./answer'):
    for filename in filenames:
        if filename != 'dataset.csv':
            continue
        with open(os.path.join(root, filename)) as file:
            questions_info = list(csv.DictReader(file))
        for question_info in questions_info:
            count_data += 1
            with open(os.path.join(root, 'processed_data', f'{question_info["id"][2:-5]}.html')) as file:
                html_code = file.read()
            gold_answer = question_info['answer']
            gold_tag = int(question_info['tag'])
            pred_answer = result[question_info['id']]['answer']
            pred_tag = result[question_info['id']]['tag']
            exact_score += get_exact_score(gold_answer, pred_answer)
            f1_score += get_f1_score(gold_answer, pred_answer)
            pos_score += get_pos_score(gold_tag, int(question_info['answer_start']), pred_tag, html_code)
print(json.dumps({
    'EM': 100 * exact_score / count_data,
    'F1': 100 * f1_score / count_data,
    'POS': 100 * pos_score / count_data
}))
