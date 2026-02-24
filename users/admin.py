
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Instructor

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Instructor)

