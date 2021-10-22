from django.contrib import admin

# Register your models here.

from db_models.models import InspectionHistory

admin.site.register([InspectionHistory])
