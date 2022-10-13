from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from tabbed_admin import TabbedModelAdmin

from .forms import ISOStandardForm, KeyPointForm, VATRateForm, TemplateForm, \
    GuidanceForm
from .models import LocationCurrencyPrice, TopicCurrencyPrice, \
    Location, Topic, Currency, PriceSettings, DiscountCodes, KeyPoint, ISOStandardOption, \
    ISOStandard, ISOStandardComply, SourceNC, Template, Category, Guidance, VATRate, DocumentFolder, \
    DocumentFile, Plan


class LocationCurrencyPriceAdmin(NestedStackedInline, admin.StackedInline):
    model = LocationCurrencyPrice
    extra = 0


class TopicCurrencyPriceAdmin(NestedStackedInline, admin.StackedInline):
    model = TopicCurrencyPrice
    extra = 0


@admin.register(Location)
class LocationAdmin(TabbedModelAdmin, NestedModelAdmin):
    list_display = ('name', 'ord', 'published', 'vat')
    search_fields = ['name', ]

    tab_general = (
        (None, {
            'fields': ((), ('name', 'ord', 'published', 'vat')
                       )
        }),
    )

    tab_currency = (LocationCurrencyPriceAdmin,)
    tabs = [
        ('General', tab_general),
        ('Prices', tab_currency),
    ]


@admin.register(Topic)
class TopicAdmin(TabbedModelAdmin, NestedModelAdmin):
    """
    Clark: Add vat field
    """
    list_display = ('name', 'vat', 'ord', 'published',)
    search_fields = ['name', ]

    tab_general = (
        (None, {
            'fields': ((), ('name', 'vat', 'ord', 'published',)
                       )
        }),
    )

    tab_currency = (TopicCurrencyPriceAdmin,)
    tabs = [
        ('General', tab_general),
        ('Prices', tab_currency),
    ]


class CurrencyAdmin(admin.TabularInline):
    model = Currency
    extra = 1


class DiscountCodesAdmin(admin.TabularInline):
    model = DiscountCodes
    extra = 1
    fields = ()
    readonly_fields = ('used',)


class VATAdmin(admin.TabularInline):
    model = VATRate
    extra = 1
    fields = ()
    form = VATRateForm


@admin.register(PriceSettings)
class PriceSettingsAdmin(TabbedModelAdmin, NestedModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(PriceSettingsAdmin, self).get_actions(request)
        # del actions['delete_selected']
        return actions

    list_display = ('site',)

    tab_general = (
        (None, {
            'fields': ((), ('disc_choice', 'disc_topic', 'disc_location',),
                       ('disc_next_choice', 'disc_next_topic', 'disc_next_location',)
                       )
        }),
    )

    tab_currency = (CurrencyAdmin,)
    tab_discount = (DiscountCodesAdmin,)
    tab_vat = (VATAdmin,)

    tabs = [
        ('Price Metrics', tab_general),
        ('Currency', tab_currency),
        ('Discount Codes', tab_discount),
        ('VAT Taxes', tab_vat),
    ]


class TopicOptions(NestedStackedInline, admin.StackedInline):
    model = ISOStandardOption
    extra = 1


class ComplyOptions(NestedStackedInline, admin.StackedInline):
    model = ISOStandardComply
    extra = 1
    readonly_fields = ['created', ]
    # inlines = [TopicOptions]


class KeP(NestedStackedInline, admin.StackedInline):
    model = KeyPoint
    extra = 1
    inlines = [ComplyOptions]
    exclude = ('req',)
    form = KeyPointForm


"""
Clark: Don't use this class (QuestionOptions).Don't need in ISO version.
"""
# class QuestionOptions(NestedStackedInline, admin.StackedInline):
#     model = Question
#     extra = 1
#     form = QuestionForm


"""
Clark: Refactor LegislationTopicAdmin with ISOStandardAdmin
"""


@admin.register(ISOStandard)
class ISOStandardAdmin(TabbedModelAdmin, NestedModelAdmin):
    form = ISOStandardForm
    list_display = ('title', 'location', 'topic', 'category', 'published', 'free')
    list_filter = ('version', 'location', 'topic', 'category',)
    inlines = [
        KeP
    ]
    tab_question = (
        (None, {
            'fields': (
                'title', 'description', 'location', 'topic', 'category', 'published', 'free', 'order', 'orderfull',
                'version'),
        }),
    )
    tab_kp = (KeP,)
    # tab_quest = (QuestionOptions,)
    """
    Clark: change Key Points with Requirements
    """
    tabs = [
        ('General', tab_question),
        # ('Specific questions', tab_quest),
        # ('Key Points', tab_kp),
        ('Requirements', tab_kp),
    ]

    def copy(self, request, queryset):

        for l in queryset:
            obj = ISOStandard.objects.get(id=l.id)
            obj.pk = None
            obj.title = "[COPY] " + l.title
            obj.save()

            # for q in l.legquestions.all():
            #     objq = Question.objects.get(id=q.id)
            #     objq.pk = None
            #     objq.isostandard = obj
            #     objq.save()

            for q in l.kpoints.all():
                objq = KeyPoint.objects.get(id=q.id)
                objq.pk = None
                objq.isostandard = obj
                objq.save()

                for c in q.keypoint_comply.all():
                    objc = ISOStandardComply.objects.get(id=c.id)
                    objc.pk = None
                    objc.point = objq
                    objc.save()

    copy.short_description = "Copy"
    actions = [copy]


# @admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'published',)
    search_fields = ['name', ]


class KePReq(NestedStackedInline, admin.StackedInline):
    model = KeyPoint
    extra = 1
    inlines = [ComplyOptions]
    exclude = ('legtopic',)
    form = KeyPointForm


"""
Clark: Not need
"""


# @admin.register(Requirements)
# class RequirementsAdmin(TabbedModelAdmin, NestedModelAdmin):
#     list_display = ('name', 'published',)
#     search_fields = ['name', ]
#
#     inlines = [
#         KePReq
#     ]
#     tab_req = (
#         (None, {
#             'fields': ('name', 'description', 'published',),
#         }),
#     )
#     tab_kp = (KePReq,)
#
#     tabs = [
#         ('Genaral', tab_req),
#         ('Key Points', tab_kp),
#     ]


@admin.register(SourceNC)
class SourceNCAdmin(admin.ModelAdmin):
    list_display = ('name', 'default', 'defaulto')
    search_fields = ['name', ]


"""
Clark: Refactor DocumentAdmin with TemplateAdmin
"""


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'free')
    search_fields = ['title', ]
    form = TemplateForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'published')
    search_fields = ['name', ]


@admin.register(Guidance)
class GuidanceAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title', ]
    form = GuidanceForm


class DocumentFileInline(admin.StackedInline):
    model = DocumentFile
    max_num = 0
    readonly_fields = ['user', 'name', 'file']


@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'parent', 'created_at')
    search_fields = ['name', 'created_at', 'parent']
    readonly_fields = ['user', 'created_by_admin']
    inlines = [DocumentFileInline]
    exclude = ['product']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'period', 'user_count', 'standard_count', 'price', 'published')
    search_fields = ['name']

# @admin.register(DocumentFile)
# class DocumentFile(admin.ModelAdmin):
#     list_display = ('name', 'user', 'folder', 'created_at')
#     search_fields = ['name', 'created_at', 'folder']
#     readonly_fields = ['user']
