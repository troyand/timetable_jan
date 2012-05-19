from django.contrib import admin
from timetable.university.models import *

from django.db.models import get_models, get_app

app_models = get_app('university')
for model in get_models(app_models):
    admin.site.register(model)
