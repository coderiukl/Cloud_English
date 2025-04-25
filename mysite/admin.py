from django.contrib import admin
from .models import User, Topic, Section, Subtopic, AudioExercise
# Register your models here.
admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Section)
admin.site.register(Subtopic)
admin.site.register(AudioExercise)