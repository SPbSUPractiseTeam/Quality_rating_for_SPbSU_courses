from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.views.generic.base import View
from mainapp.models import Course, Week, Video, Test, LoadDate, Attempt
from .forms import UploadFileForm, CustomUserCreationForm
from .support_scripts import save_file
from django.http import QueryDict
import os
from unidecode import unidecode
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User
from django.http import HttpResponse


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")


def upload_file(request):
    if request.method == 'POST' and request.POST and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            save_file(request.FILES['log'],
                      os.path.join(settings.MEDIA_ROOT, request.user.username, "logs", unidecode(request.POST['title']),
                                   request.FILES['log'].name), request.user, request.POST['title'])
    form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


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
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/message.html', {'message': 'Пожалуйста, подтвердите свой адрес электронной почты для того, чтобы закончить регистрацию'})
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
        return render(request, 'registration/message.html', {'message': 'Спасибо за подтверждение адреса электронной почты. Теперь вы можете войти в систему'})
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
    if request.method == 'POST' and request.POST and request.FILES:
        post = QueryDict('title=' + request.POST['title'])
        form = UploadFileForm(post, request.FILES)
        if form.is_valid():
            save_file(request.FILES['log'],
                      os.path.join(settings.MEDIA_ROOT, request.user.username, "logs", unidecode(request.POST['title']),
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
