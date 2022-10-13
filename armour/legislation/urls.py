from django.conf.urls import url

"""
Clark: Restore TemplateListView
"""

from .views import ISOStandardView, ISOStandardContentView, \
    SetISOStandardView, ISONCView, SetNonConformanceView, FinishView, ProductListView, \
    StartNewView, LegislationDocView, ISOReportView, OuterNonConformanceView, SetOuterNonConformanceView, \
    LegislationDeleteView, LegislationNCReportView, PlanSelectView, \
    TemplateListView, GuidanceListView, LegUpdateView, LegislationNCOuterReportView, SetDiscountView, \
    ManagementSystemView, ManagementSystemGetView, ManagementSystemFileUploadView, PlanView, PdfView

urlpatterns = [
    url(r'^my/list/$', ProductListView.as_view(), {}, 'product-report'),
    # url(r'^specific-questions/$', SpecificQuestions.as_view(), {}, 'spec-questions'),
    # url(r'^specific-questions/set/$', SetSpecQuestionView.as_view(), {}, 'spec-question-set'),
    url(r'^iso-standards/$', ISOStandardView.as_view(), {}, 'iso-standards'),
    url(r'^iso-standards/content/$', ISOStandardContentView.as_view(), {}, 'iso-standards-content'),
    url(r'^iso-standards/set/$', SetISOStandardView.as_view(), {}, 'iso-standards-set'),
    url(r'^non-conformance/$', ISONCView.as_view(), {}, 'non-conformance'),
    url(r'^non-conformance/set/(?P<pk>\d+)/$', SetNonConformanceView.as_view(), {}, 'non-conformance-set'),
    url(r'^finish/$', FinishView.as_view(), {}, 'finish'),
    url(r'^start/$', StartNewView.as_view(), {}, 'start-legislation'),
    url(r'^document/download/(?P<pk>[0-9A-Fa-f-]+)/$', LegislationDocView.as_view(), {}, 'get-leg-doc'),
    url(r'^document/report/pdf/(?P<pk>[0-9A-Fa-f-]+)/$', ISOReportView.as_view(), {}, 'get-report-pdf'),
    url(r'^non-conformance/compact/$', OuterNonConformanceView.as_view(), {}, 'additional-non-conformance'),
    url(r'^non-conformance/compact/set/(?P<pk>\d+)/$', SetOuterNonConformanceView.as_view(), {},
        'additional-non-conformance-set'),
    url(r'^legislation/delete/(?P<pk>\d+)/$', LegislationDeleteView.as_view(), {}, 'legislation-delete'),
    url(r'^document/report/nc/pdf/(?P<pk>[0-9A-Fa-f-]+)/(?P<mode>[\w\-]+)/$', LegislationNCReportView.as_view(), {},
        'get-report-nc-pdf'),
    url(r'^document/report/outer/nc/pdf/$', LegislationNCOuterReportView.as_view(), {},
        'get-report-nc-outer-pdf'),
    # url(r'^specific-questions/confirmation/$', SpecQuestionConfirmationView.as_view(), {},
    #    'spec-questions-confirmation'),
    url(r'^select/your/plan/$', PlanSelectView.as_view(), {}, 'select-your-plan'),
    url(r'^template/list/$', TemplateListView.as_view(), {}, 'template-list'),
    url(r'^guidance/list/$', GuidanceListView.as_view(), {}, 'guidance-list'),
    url(r'^version/update/$', LegUpdateView.as_view(), {}, 'legislation-version-update'),
    url(r'^discount/set/$', SetDiscountView.as_view(), {}, 'discount-set'),
    url(r'^management-system/view/$', ManagementSystemView.as_view(), {}, 'management-system-view'),
    url(r'^management-system/manage/$', ManagementSystemGetView.as_view(), {}, 'management-system-manage'),
    url(r'^management-system/file/$', ManagementSystemFileUploadView.as_view(), {}, 'management-system-file'),
    url(r'^plan/view/$', PlanView.as_view(), {}, 'plan-view'),
    url(r'^test/view/$', PdfView.as_view(), {}, 'pdf-view'),
]
