import os, shutil, hashlib

from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import QueryDict, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.views.generic.edit import FormView
from django.views.generic.base import View

from mainapp.models import Course, Log, Module, Lesson, Video, Test, Attempt
from mainapp.forms import UploadFileForm, CustomUserCreationForm
from mainapp.support_scripts import save_file
from mainapp.tokens import account_activation_token


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")


def delete_course(request):
    if 'course_id' not in request.POST:
        return HttpResponseBadRequest("Ошибочный запрос")
    else:
        course_id = int(request.POST['course_id'])
        course = Course.objects.filter(id=course_id)
        if len(course) != 1:
            return HttpResponseBadRequest("Курс не существует")
        elif course[0].user != request.user:
            return HttpResponseBadRequest("У вас нет доступа для удаления данного курса")
        else:
            md5_hash = course[0].hash_str_id
            for dir_name in ['logs', 'json', 'images']:
                dir_path = os.path.join(settings.MEDIA_ROOT, request.user.username, dir_name,
                                        md5_hash)
                if os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
            course.delete()
            return HttpResponse()


def delete_log(request):
    if 'log_id' not in request.POST:
        return HttpResponseBadRequest("Ошибочный запрос")
    else:
        log_id = int(request.POST['log_id'])
        log = Log.objects.filter(id=log_id)
        connected_logs = Log.objects.filter(course=log[0].course)
        if len(connected_logs) == 1:
            return HttpResponseBadRequest("Это последняя загрузка данного курса в системе")
        elif len(log) != 1:
            return HttpResponseBadRequest("Загрузка не существует")
        elif log[0].course.user != request.user:
            return HttpResponseBadRequest("У вас нет доступа для удаления данной загрузки")
        else:
            response = HttpResponse()
            response.set_cookie('current_course_id', log[0].course.id)
            log.delete()
            return response


def update_course_title(request):
    if 'course_id' not in request.POST:
        return HttpResponseBadRequest("Ошибочный запрос")
    else:
        course_id = int(request.POST['course_id'])
        new_title = request.POST['title']
        course = Course.objects.filter(id=course_id)
        if len(course) != 1:
            return HttpResponseBadRequest("Курс не существует")
        elif course[0].user != request.user:
            return HttpResponseBadRequest("У вас нет доступа для изменения данного курса")
        elif course[0].russian_title == new_title:
            return HttpResponseBadRequest("Название курса не изменено")
        else:
            course.update(russian_title=new_title)
            return HttpResponse()


def upload_file(request):
    course_id = -1
    if request.method == 'POST' and request.POST and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            md5_hash = hashlib.md5(request.FILES['log'].name.encode()).hexdigest()
            course_id = save_file(request.FILES['log'],
                                  os.path.join(settings.MEDIA_ROOT, request.user.username, "logs", md5_hash,
                                               request.FILES['log'].name), request.user, request.POST['title'])
    else:
        form = UploadFileForm()
    response = render(request, 'upload.html', {'form': form})
    response.set_cookie('current_course_id', course_id)
    return response


def registration(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Активируйте свой аккаунт на сайте {}'.format(current_site.domain)
            message = render_to_string('registration/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/message.html', {
                'message': 'Пожалуйста, подтвердите свой адрес электронной почты, чтобы закончить регистрацию'})
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'registration/message.html', {
            'message': 'Спасибо за подтверждение адреса электронной почты. Теперь вы можете войти в систему'})
    else:
        return render(request, 'registration/message.html', {'message': 'Ссылка активации не подходит!'})


class LoginFormView(FormView):
    success_url = "/"
    form_class = AuthenticationForm
    template_name = "registration/login.html"

    def form_valid(self, form):
        self.user = form.get_user()
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


@login_required(login_url='login')
def courses_list(request):
    current_user = request.user.username
    courses = Course.objects.filter(user__username__exact=current_user)
    return render(request, 'index.html', {'courses': courses})


@login_required(login_url='login')
def course_detail(request):
    course_uploaded_id = -1
    if request.method == 'POST' and request.POST and request.FILES:
        post = QueryDict('title=' + request.POST['title'])
        form = UploadFileForm(post, request.FILES)
        if form.is_valid():
            md5_hash = hashlib.md5(request.FILES['log'].name.encode()).hexdigest()
            course_uploaded_id = save_file(request.FILES['log'],
                                           os.path.join(settings.MEDIA_ROOT, request.user.username, "logs", md5_hash,
                                                        request.FILES['log'].name), request.user, request.POST['title'])
    else:
        form = UploadFileForm()
    course_id = int(request.POST['course_id'])
    log_id = int(request.POST['log_id'])
    module_id = int(request.POST['module_id'])
    logs = Log.objects.filter(course__id__exact=course_id).order_by('load_date')
    if log_id == -1:
        log_id = logs[0].id
    modules = Module.objects.filter(log__id__exact=log_id).order_by('number')
    if module_id == -1:
        module_id = modules[0].id
    lessons = Lesson.objects.filter(module__id__exact=module_id).order_by('number')
    videos = Video.objects.filter(lesson__in=lessons)
    most_viewed_video = None
    if videos.count() > 0:
        most_viewed_video = videos[0]
        for video in videos:
            if video.is_most_viewed:
                most_viewed_video = video
    tests = Test.objects.filter(lesson__in=lessons)
    attempts = Attempt.objects.filter(test__in=tests).order_by('number')
    for lesson in lessons:
        lesson_tests = tests.filter(lesson__id__exact=lesson.id).order_by('number')
        for lesson_test in lesson_tests:
            setattr(lesson_test, 'attempts', attempts.filter(test__id__exact=lesson_test.id).order_by('number'))
        lesson_videos = videos.filter(lesson__id__exact=lesson.id).order_by('number')
        setattr(lesson, 'tests', lesson_tests)
        setattr(lesson, 'videos', lesson_videos)
        setattr(lesson, 'tests_count', len(lesson_tests))
        setattr(lesson, 'videos_count', len(lesson_videos))
    response = render(request, 'detail.html',
                      {'form': form, 'logs': logs, 'modules': modules, 'lessons': lessons, 'tests': tests,
                       'videos': videos, 'attempts': attempts, 'most_viewed_video': most_viewed_video,
                       'logs_amount': len(logs)})
    response.set_cookie('current_course_id', course_uploaded_id)
    return response
