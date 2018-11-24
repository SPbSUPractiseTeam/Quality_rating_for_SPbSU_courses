from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login$', views.LoginFormView.as_view(), name='login_page'),
    url(r'^register$', views.registration, name='register_page'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout_page'),
    url(r'^upload$', views.upload_file, name='upload_file'),
    url(r'^$', views.courses_list, name='courses_list'),
    url(r'^detail$', views.course_detail, name='course_detail'),
    url('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
]
