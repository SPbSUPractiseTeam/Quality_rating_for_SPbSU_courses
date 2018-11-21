import numpy as np


def calculate_questions(list_for_questions):
    # calculating: sum of grades on question and number of answers on question
    percentage = list_for_questions.groupby(['course_name', 'problem_id', 'page', 'attempts', 'max_grade', 'question'])[
        'result'].agg([np.sum, np.size])

    # calculating percentage of right answers on each question
    percentage = 100 * percentage['sum'] / percentage['size']
    percentage = percentage.reset_index()
    # merge questions and percentage of right answers
    percentage['questions'] = percentage[0].map(str)
    percentage.drop(columns=['question', 0])

    # merge questions in test
    percentage = percentage.groupby(['course_name', 'problem_id', 'page', 'attempts', 'max_grade'])['questions'].apply(
        ','.join).reset_index()

    return percentage
