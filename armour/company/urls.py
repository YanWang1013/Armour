from django.conf.urls import url
from .views import CCUpdateView, CCConfirmView, CCSuccessView, OrganizationUpdate, EmployeeAddView, EmployeeListView, \
    EmployeeEditView, EmployeeDeleteView, OrganizationAdmins, OrganizationAdminsListView, OrganizationAdminsAddView, \
    OrganizationAdminsEditView, OrganizationAdminsDeleteView, CompanyUpdate, LegalUpdate, SubscriptionView, \
    PaymentsListView, CancelSubscriptionView, CompanyBuilderStep1View, CompanyBuilderStep1UpdateView, CompanyBuilderStep2UpdateView, CompanyBuilderStep3UpdateView, CompanyBuilderStep4UpdateView,CompanyBuilderConfirmationView, StartFreeView

urlpatterns = [
    url(r'^credit-cart/update/$', CCUpdateView.as_view(), {}, 'cc-update'),
    url(r'^credit-cart/confirm/$', CCConfirmView.as_view(), {}, 'cc-confirm'),
    url(r'^credit-cart/success/(?P<uuid>[\w\-]+)/$', CCSuccessView.as_view(), {}, 'cc-success'),
    url(r'^organisation/update/$', OrganizationUpdate.as_view(), {}, 'organization-update'),
    url(r'^employee/add/$', EmployeeAddView.as_view(), {}, 'employee-add'),
    url(r'^employee/list/$', EmployeeListView.as_view(), {}, 'employee-list'),
    url(r'^employee/edit/(?P<pk>\d+)/$', EmployeeEditView.as_view(), {}, 'employee-edit'),
    url(r'^employee/delete/(?P<pk>\d+)/$', EmployeeDeleteView.as_view(), {}, 'employee-delete'),
    url(r'^organisation/admins/$', OrganizationAdmins.as_view(), {}, 'organization-admins'),
    url(r'^organisation/admins/list/$', OrganizationAdminsListView.as_view(), {}, 'organization-admins-list'),
    url(r'^organisation/admins/add/$', OrganizationAdminsAddView.as_view(), {}, 'organization-admins-add'),
    url(r'^organisation/admins/edit/(?P<pk>\d+)/$', OrganizationAdminsEditView.as_view(), {},
        'organization-admins-edit'),
    url(r'^organisation/admins/delete/(?P<pk>\d+)/$', OrganizationAdminsDeleteView.as_view(), {},
        'organization-admins-delete'),
    url(r'^profile/update/$', CompanyUpdate.as_view(), {}, 'profile-update'),
    url(r'^profile/legal-information/$', LegalUpdate.as_view(), {}, 'legal-info'),
    url(r'^subscription/$', SubscriptionView.as_view(), {}, 'subscription'),
    url(r'^subscription/list/$', PaymentsListView.as_view(), {}, 'subscription-list'),
    url(r'^subscription/cancel/$', CancelSubscriptionView.as_view(), {}, 'subscription-cancel'),
    url(r'^organisation/builder/step/1/$', CompanyBuilderStep1View.as_view(), {}, 'organization-step-1'),
    url(r'^organisation/builder/step/1/update/$', CompanyBuilderStep1UpdateView.as_view(), {},
        'organization-step-1-update'),
    url(r'^organisation/builder/step/2/update/$', CompanyBuilderStep2UpdateView.as_view(), {},
        'organization-step-2-update'),
    url(r'^organisation/builder/step/3/update/$', CompanyBuilderStep3UpdateView.as_view(), {},
        'organization-step-3-update'),
    url(r'^organisation/builder/step/4/update/$', CompanyBuilderStep4UpdateView.as_view(), {},
        'organization-step-4-update'),
    url(r'^organisation/builder/step/confirmation/$', CompanyBuilderConfirmationView.as_view(), {},
        'organization-step-confirmation'),
    url(r'^organisation/start/free/trial/$', StartFreeView.as_view(), {},
        'organization-start-free'),

]
