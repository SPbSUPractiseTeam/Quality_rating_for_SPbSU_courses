import json
import os


def output(res, course_name, path):
    result = dict()
    res = res.to_dict('records')
    attempt_idx = 0
    test_idx = 0
    for item in res:
        if item['course_name'] not in result:
            result[item['course_name']] = {'tests': {}}
        if item['problem_id'] not in result[item['course_name']]['tests']:
            test_idx+=1
            result[item['course_name']]['tests'][item['problem_id']] = {'attempts': []}
            attempt_idx = 0
        attempt_idx += 1
        result[item['course_name']]['tests'][item['problem_id']]['attempts'].append({'questions': item['questions']})
        result[item['course_name']]['tests'][item['problem_id']]['attempts'][-1]['attempt'] = attempt_idx
        result[item['course_name']]['tests'][item['problem_id']]['attempts'][-1]['max_grade'] = item[
            'max_grade']
        result[item['course_name']]['tests'][item['problem_id']]['attempts'][-1]['number_of_solutions'] = \
            item['number_of_solutions']
        result[item['course_name']]['tests'][item['problem_id']]['number']=test_idx
        result[item['course_name']]['tests'][item['problem_id']]['attempts'][-1]['mean'] = item['mean']
        result[item['course_name']]['tests'][item['problem_id']]['attempts'][-1]['median'] = item['median']
        result[item['course_name']]['tests'][item['problem_id']]['page'] = item['page']
    file_name = os.path.join(path, course_name + '_tests_statistics.json')
    data_file = open(file_name, 'w')
    data_file.write(json.dumps(result))
    data_file.close()
    return file_name
