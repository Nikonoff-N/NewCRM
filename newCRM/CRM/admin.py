from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Client)
admin.site.register(Payment)
admin.site.register(Teacher)
admin.site.register(Lesson)
admin.site.register(Phone)
admin.site.register(Group)