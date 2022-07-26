import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
from CRM.models import *
print(Client.objects.all())