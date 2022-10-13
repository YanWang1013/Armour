from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

from .forms import MassEmailAdminForm, FlatpageCustomForm
from .models import Tip, MassEmail

admin.site.unregister(FlatPage)


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name', ]


@admin.register(MassEmail)
class MassEmailAdmin(admin.ModelAdmin):
    form = MassEmailAdminForm
    date_hierarchy = 'sent_at'
    ordering = ['-sent_at']

    search_fields = ['sender', 'sent_to', 'content', 'topics', 'locations', ]

    readonly_fields = ('sent_at', 'sender', 'sent_to',)

    """
    Clark: version field not exist, replace with sender
    """
    fieldsets = (
        (None, {
            # 'fields': ('version', 'locations', 'topics', 'content', 'lnk'),
            'fields': ('sender', 'locations', 'topics', 'content', 'lnk'),
        }),

    )
    list_display = ('sent_at', 'sender', 'get_receivers',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FlatPage)
class FlatPagesCustomAdmin(FlatPageAdmin, ):
    form = FlatpageCustomForm
