import os, hashlib, json, datetime
from mainapp.modules.analysis import analysis
from mainapp.modules.preprocessing import log_parser
import matplotlib.pyplot as plt
import numpy as np
from mainapp.models import Course, Log, Module, Lesson, Video, Test, Attempt


def get_split_path(path):
    disk_and_path = path.split(os.sep + os.sep)
    split_path = []
    if len(disk_and_path) > 1:
        split_path.append(disk_and_path[0] + os.sep)
        split_path.extend(disk_and_path[1].split(os.sep))
    else:
        split_path.extend(disk_and_path[0].split(os.sep))
    return split_path


def save_file(file, path, user, title):
    md5_hash = hashlib.md5(file.name.encode()).hexdigest()
    dirs = os.sep.join(path.split(os.sep)[:-1])
    split_path = get_split_path(dirs)
    save_path = []
    charts_save_path = []
    for path_dir in split_path:
        if path_dir == 'logs':
            save_path.append('json')
            charts_save_path.append('images')
        else:
            charts_save_path.append(path_dir)
            save_path.append(path_dir)
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    path = os.sep.join([dirs, file.name])
    with open(path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    save_path = os.sep.join(save_path)
    charts_save_path = os.sep.join(charts_save_path)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(charts_save_path):
        os.makedirs(charts_save_path)
    json_files = make_analytic_json(file.name, dirs, save_path)
    os.remove(path)
    if json_files is not None:
        return parse_json_to_database(*json_files, user, title, charts_save_path, md5_hash)
    else:
        return 0


def parse_json_to_database(video_json_file_path, tests_json_file_path, user, russian_title, charts_save_path, md5_hash):
    with open(video_json_file_path, "r") as video_json_file:
        video_dict = json.load(video_json_file)
    with open(tests_json_file_path, "r") as tests_json_file:
        tests_dict = json.load(tests_json_file)
        course = Course.objects.get_or_create(user=user,
                                              title=list(tests_dict.keys())[0],
                                              russian_title=russian_title,
                                              defaults={'hash_str_id': md5_hash}
                                              )[0]
    log = Log.objects.create(course=course,
                             load_date=datetime.datetime.now())
    parse_tests_json(tests_dict, log)
    parse_video_json(video_dict, log, charts_save_path)
    return course.id


def parse_tests_json(tests_dict, log):
    modules_idx = 1
    for module_item in tests_dict['tests']:
        module = Module.objects.create(hash_str_id=module_item['section'],
                                       log=log,
                                       number=modules_idx)
        modules_idx += 1
        lessons_idx = 1
        for lesson_item in module_item['subsections']:
            lesson = Lesson.objects.get_or_create(hash_str_id=lesson_item['subsection'],
                                                  module=module,
                                                  link=lesson_item['page'],
                                                  defaults={'number': lessons_idx})
            if lesson[1]:
                lessons_idx += 1
            lesson = lesson[0]
            problem_type = lesson_item['problem_type']
            tests_idx = Test.objects.filter(lesson=lesson).count() + 1
            for test_item in lesson_item['one_type_problems']:
                test = Test.objects.get_or_create(hash_str_id=test_item['problem_id'],
                                                  lesson=lesson,
                                                  type=problem_type,
                                                  defaults={'number': tests_idx})
                if test[1]:
                    tests_idx += 1
                test = test[0]
                for attempt_item in test_item['attempts']:
                    questions = list()
                    for question in attempt_item['questions']:
                        questions.append("{}){}".format(question['question'], question['percent_of_right_answers']))
                    questions = ','.join(questions)
                    Attempt.objects.get_or_create(number=attempt_item["attempt"],
                                                  test=test,
                                                  defaults={
                                                      'average_grade': attempt_item['mean'],
                                                      'median': attempt_item['median'],
                                                      'questions': questions,
                                                      'number_of_solutions': attempt_item['number_of_solutions'],
                                                      'max_grade': attempt_item['max_grade']})


def parse_video_json(video_dict, log, charts_save_path):
    modules_idx = Module.objects.filter(log=log).count() + 1
    for module_item in video_dict['sections']:
        most_viewed_video_id = 0
        most_viewed_video_percent = 0.0
        module = Module.objects.get_or_create(
            log=log,
            hash_str_id=module_item["section_name"],
            defaults={'number': modules_idx})
        if module[1]:
            modules_idx += 1
        module = module[0]
        lessons_idx = Lesson.objects.filter(module=module).count() + 1
        for lesson_item in module_item['subsections']:
            lesson = Lesson.objects.get_or_create(hash_str_id=lesson_item['subsection_name'],
                                                  module=module,
                                                  link='/'.join(
                                                      ['http:',
                                                       '',
                                                       'courses.openedu.ru',
                                                       'courses',
                                                       video_dict['course_name'],
                                                       'courseware',
                                                       module_item["section_name"],
                                                       lesson_item['subsection_name']]),
                                                  defaults={'number': lessons_idx})
            if lesson[1]:
                lessons_idx += 1
            lesson = lesson[0]
            videos_idx = 1
            for video_item in lesson_item['videos']:
                chart_link = make_img(video_item, charts_save_path)
                video = Video.objects.create(lesson=lesson,
                                             chart_link=chart_link,
                                             number=videos_idx,
                                             link=video_item['page'],
                                             material_viewed=video_item['watched_percent'],
                                             users_watched=video_item['user_percent'],
                                             is_most_viewed=False)
                if video_item['user_percent'] > most_viewed_video_percent:
                    most_viewed_video_id = video.id
                    most_viewed_video_percent = video_item['user_percent']
            Video.objects.filter(id=most_viewed_video_id, lesson=lesson).update(is_most_viewed=True)


def make_img(video_info, save_path):
    save_path = os.path.join(save_path, hashlib.blake2b(str(datetime.datetime.now()).encode()).hexdigest() + '.png')
    plt.plot(np.linspace(0, video_info['length'], video_info['intervals_number']), video_info['review_intervals'])
    plt.savefig(save_path, dpi=600)
    plt.close()
    return os.sep.join(save_path.split(os.sep)[5:])


def make_analytic_json(file_name, path_to_log, save_path):
    db_name = log_parser.open_logs(file_name, path_to_log)
    analysis.set_data(db_name, save_path)
    video_analysis_filename = analysis.use_module('video')
    tests_analysis_filename = analysis.use_module('tests')
    if video_analysis_filename is None or tests_analysis_filename is None:
        return None
    else:
        return [video_analysis_filename, tests_analysis_filename]
