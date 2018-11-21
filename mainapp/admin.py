from django.contrib import admin
from .models import Course, Week, Video, Test, LoadDate, Attempt

admin.site.register(Course)
admin.site.register(Week)
admin.site.register(Video)
admin.site.register(Test)
admin.site.register(Attempt)
admin.site.register(LoadDate)
