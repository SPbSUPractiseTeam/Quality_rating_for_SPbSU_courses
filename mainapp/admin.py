from django.contrib import admin
from .models import Course, Log, Module, Lesson, Video, Test, Attempt

admin.site.register(Course)
admin.site.register(Log)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Video)
admin.site.register(Test)
admin.site.register(Attempt)
