from django.contrib import admin

# Register your models here.

from inspection.models import InspectionHistory

admin.site.register([InspectionHistory])
