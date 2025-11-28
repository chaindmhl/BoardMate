from django.contrib import admin
from .models import Question, AnswerKey, TestKey, CustomUser, Teacher, Student, Result

admin.site.register(CustomUser)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Question)
admin.site.register(Result)
admin.site.register(AnswerKey)
admin.site.register(TestKey)
