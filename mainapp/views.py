from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.views.generic.base import View
from mainapp.models import Course, Week, Video, Test, LoadDate, Attempt
from .forms import UploadFileForm
from .support_scripts import save_file
from django.http import QueryDict
import os

BASE_DIR = ""


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")


def upload_file(request):
    if request.method == 'POST' and request.POST and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            save_file(request.FILES['log'],
                      os.path.join(BASE_DIR, 'profiles', request.user.username, "logs", request.POST['title'],
                                   request.FILES['log'].name), request.user, request.POST['title'])
    form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


class RegisterFormView(FormView):
    form_class = UserCreationForm
    success_url = "login"
    template_name = "registration/register.html"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)


class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "registration/login.html"
    success_url = "/"

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
    if request.method == 'POST' and request.POST and request.FILES:
        post = QueryDict('title=' + request.POST['title'])
        form = UploadFileForm(post, request.FILES)
        if form.is_valid():
            save_file(request.FILES['log'],
                      os.path.join(BASE_DIR, 'profiles', request.user.username, "logs", request.POST['title'],
                                   request.FILES['log'].name), request.user, request.POST['title'])
    else:
        form = UploadFileForm()
    course_id = int(request.POST['course_id'])
    date_id = int(request.POST['date_id'])
    week_id = int(request.POST['week_id'])
    dates = LoadDate.objects.filter(course__id__exact=course_id).order_by('date')
    if date_id == -1:
        date_id = dates[0].id
    weeks = Week.objects.filter(date__id__exact=date_id).order_by('number')
    if week_id == -1:
        week_id = weeks[0].id
    videos = Video.objects.filter(week__id__exact=week_id).order_by('number')
    most_viewed_video = videos[0]
    for video in videos:
        if video.is_most_viewed:
            most_viewed_video = video
    tests = Test.objects.filter(course__id__exact=course_id)
    attempts = Attempt.objects.filter(test__in=tests).order_by('number')
    for test in tests:
        setattr(test, 'attempts', attempts.filter(test__id__exact=test.id).order_by('number'))
    return render(request, 'detail.html',
                  {'form': form, 'dates': dates, 'weeks': weeks, 'tests': tests, 'attempts': attempts,
                   'videos': videos, 'most_viewed_video': most_viewed_video})
