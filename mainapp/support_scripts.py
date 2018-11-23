import os
import json
import datetime
from mainapp.modules.analysis import analysis
from mainapp.modules.preprocessing import log_parser
import matplotlib.pyplot as plt
import numpy as np
from mainapp.models import Course, LoadDate, Week, Test, Attempt, Video

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
        parse_json_to_database(*json_files, user, title, charts_save_path)


def parse_json_to_database(video_json_file_path, tests_json_file_path, user, russian_title, charts_save_path):
    with open(video_json_file_path, "r") as video_json_file:
        video_dict = json.load(video_json_file)
    with open(tests_json_file_path, "r") as tests_json_file:
        tests_dict = json.load(tests_json_file)
        course = Course.objects.get_or_create(user=user, title=list(tests_dict.keys())[0], russian_title=russian_title)[
            0]
    date = LoadDate.objects.create(course=course, date=datetime.datetime.now())
    parse_tests_json(course, tests_dict)
    parse_video_json(video_dict, date, charts_save_path)


def parse_tests_json(course, tests_dict):
    for problem_id, test_item in tests_dict[course.title]['tests'].items():
        test = Test.objects.get_or_create(hash_str_id=problem_id, course=course,
                                          defaults={'number': test_item['number'], 'link': test_item['page']})[0]
        for attempt_item in test_item['attempts']:
            Attempt.objects.get_or_create(number=attempt_item["attempt"], test=test,
                                          defaults={'average_grade': attempt_item['mean'],
                                                    'median': attempt_item['median'],
                                                    'questions': attempt_item['questions'],
                                                    'number_of_solutions': attempt_item[
                                                        'number_of_solutions'],
                                                    'max_grade': attempt_item['max_grade']})


def parse_video_json(video_dict, date, charts_save_path):
    idx_week = 0
    for week_item in video_dict['sections']:
        most_viewed_video_hash_str = ""
        most_viewed_video_percent = 0.0
        idx_week += 1
        idx_video = 0
        week = Week.objects.get_or_create(
            date=date,
            hash_str_id=week_item["section_name"],
            defaults={'number': idx_week})[0]
        for video_item in week_item['subsections']:
            idx_video += 1
            video_info = video_item['videos'][0]
            chart_link = make_img(video_info, video_item["subsection_name"], charts_save_path)
            Video.objects.create(hash_str_id=video_item["subsection_name"],
                                 week=week, link=video_info['page'],
                                 number=idx_video,
                                 chart_link=chart_link,
                                 material_viewed=video_info['watched_percent'],
                                 users_watched=video_info['user_percent'],
                                 is_most_viewed=False)
            if video_info['user_percent'] > most_viewed_video_percent:
                most_viewed_video_hash_str = video_item["subsection_name"]
                most_viewed_video_percent = video_info['user_percent']
        Video.objects.filter(hash_str_id=most_viewed_video_hash_str, week=week).update(is_most_viewed=True)


def make_img(video_info, video_hash_str_id, save_path):
    save_path = os.path.join(save_path, video_hash_str_id + '.png')
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
