import pandas as pd

from .content import test_questions_analisys as qa
from .content import tests_analisys as ta
from .output import output as out


def execute(cursor, course_name, path):
    # and questions NOT LIKE '__' means that we needn't questions like {}
    # and attempts < 4 means that we use only three first attempts, other attempts are not interesting
    request = """
        select 
        course_name, problem_id,
        attempts, questions,
        page, grade, max_grade
        from problem_check
        where questions NOT LIKE '__'
        and attempts < 4
        """
    cursor.execute(request)
    data = cursor.fetchall()

    columns_names = []
    for i in cursor.description[:]:
        columns_names.append(i[0])

    df = pd.DataFrame(data=data, columns=columns_names)

    # changing refer link and cut problem_id
    df['page'] = df['page'].apply(lambda x: x.split('/handler')[0])
    df['problem_id'] = df['problem_id'].apply(lambda x: x.split('@')[-1])

    # calculating: average grade, median of grade, number of answers for each test
    avg = ta.calculate_tests(df)

    # counting percent of right answers on each question
    # parsing questions string in two columns: question and result
    list_for_questions = pd.DataFrame(
        columns=('course_name', 'problem_id', 'page', 'question', 'attempts', 'result', 'max_grade'))

    for row_counter in range(df.shape[0]):
        current_attempt = df.attempts[row_counter]
        current_page = df.page[row_counter]
        current_course = df.course_name[row_counter]
        current_grade = df.max_grade[row_counter]
        current_problem = df.problem_id[row_counter]
        row = (df.questions[row_counter][1:-1]).split(',')
        for cell_row in row:
            temp_row = cell_row.split(':')
            if temp_row[1] == 'True':
                list_for_questions = list_for_questions.append(
                    {'course_name': current_course, 'problem_id': current_problem, 'page': current_page,
                     'question': temp_row[0], 'attempts': current_attempt, 'result': 1, 'max_grade': current_grade},
                    ignore_index=True)
            else:
                list_for_questions = list_for_questions.append(
                    {'course_name': current_course, 'problem_id': current_problem, 'page': current_page,
                     'question': temp_row[0], 'attempts': current_attempt, 'result': 0, 'max_grade': current_grade},
                    ignore_index=True)

    list_for_questions['question'] = list_for_questions['question'].map(str.strip)  # deleting spaces
    list_for_questions['question'] = list_for_questions['question'].apply(
        lambda x: ('"' + x.split('_')[-2] + '_' + x.split('_')[-1]))

    perc = qa.calculate_questions(list_for_questions)

    # merge results of analysis (average and percentage) into one table
    res = pd.merge(avg, perc, on=['course_name', 'problem_id', 'page', 'attempts', 'max_grade'], how='outer')
    return out.output(res, course_name, path)
