from django.contrib import admin
from .models import User, Workflow, Templates, WorkflowMapping, APILog

admin.site.register(User)
admin.site.register(Workflow)
admin.site.register(Templates)
admin.site.register(WorkflowMapping)
admin.site.register(APILog)