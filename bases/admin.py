from material.admin.options import MaterialModelAdmin
from material.admin.sites import site

from django_q.models import Task, Schedule


class DjangoQTaskAdmin(MaterialModelAdmin):
    list_display = ['name', 'func', 'started', 'success', 'attempt_count']
    readonly_fields = ['id', 'name', 'func', 'result', 'started', 'stopped',
                       'success', 'attempt_count']
    exclude = ['hook']
    search_fields = ['id', 'name']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class DjangoQScheduleAdmin(MaterialModelAdmin):
    list_display = ['id', 'func', 'schedule_type', 'repeats', 'next_run', 'task']
    readonly_fields = ['id', 'name', 'func', 'schedule_type', 'repeats', 'next_run', 'task']
    exclude = ['hook', 'args', 'kwargs', 'minutes', 'cron']
    search_fields = ['name', 'func']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


site.register(Task, DjangoQTaskAdmin)
site.register(Schedule, DjangoQScheduleAdmin)
