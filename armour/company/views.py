from django.views.generic import UpdateView, FormView, CreateView, View, DeleteView, RedirectView
from django.views.generic import DetailView, TemplateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import BillingCompanyForm, PaymentForm, OrganizationCompanyForm, EmployeeForm, AdminForm, \
    ProfileCompanyForm, TopicForm, CompanyBuilderStep1Form, OrganizationBuilderStep3Form, OrganizationBuilderStep4Form, \
    UserProfileForm
from .models import Company, Payments, Employee, PaymentsPositions
from django.conf import settings
from ..general.mixins import CCardRequireMixin, PaymentValidMixin, OrganizationOwner, OrganizationIsActive, \
    OrganizationIsFree
from django.template.loader import render_to_string
from ..general.mixins import AjaxableResponseMixin, PaymentValidMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import stripe
from django.http import HttpResponseRedirect
from django.contrib import messages
from datetime import datetime, timedelta
from ..legislation.models import DiscountCodes, ISOProduct

User = get_user_model()


class CCUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'company/cc-update.html'
    form_class = BillingCompanyForm
    success_url = reverse_lazy("cc-confirm")
    model = Company

    def get_context_data(self, **kwargs):
        context = super(CCUpdateView, self).get_context_data(**kwargs)
        context['TOKEN_KEY'] = settings.STRIPE_PUB_KEY
        dcode = self.request.session.get('dcode', None)
        code = None
        if dcode:
            code = DiscountCodes.objects.get(id=dcode)

        context['code'] = code

        price = 0
        tax = 0
        total = 0
        discount = 0
        subtotal = 0
        if self.request.user.company:
            price = self.request.user.company.gen_price()
            if code:
                subtotal = self.request.user.company.gen_price(code.size)
                tax = self.request.user.company.gen_tax(code.size)
            else:
                subtotal = self.request.user.company.gen_price()
                tax = self.request.user.company.gen_tax()

            discount = price - subtotal
            total = subtotal + tax

        context['price'] = price
        context['tax'] = tax
        context['total'] = total
        context['discount'] = discount
        context['subtotal'] = subtotal

        return context

    def get_object(self, queryset=None):
        return self.request.user.company

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class CCConfirmView(LoginRequiredMixin, CCardRequireMixin, FormView):
    template_name = 'company/ccard-confirm.html'
    model = Payments
    form_class = PaymentForm
    success_url = reverse_lazy("cc-confirm")
    uuid = None

    def get_success_url(self, **kwargs):
        return reverse_lazy('cc-success', args=(self.uuid,))

    def post(self, request, *args, **kwargs):
        if not hasattr(request.user.company, 'copmanycc'):
            return HttpResponseRedirect(reverse_lazy("cc-update"))

        form = self.get_form()
        if form.is_valid():
            p = form.save()
            self.uuid = p.uuid
            if request.session.has_key('dcode'):
                del request.session['dcode']

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CCConfirmView, self).get_context_data(**kwargs)
        context['company'] = self.request.user.company

        dcode = self.request.session.get('dcode', None)
        code = None
        if dcode:
            code = DiscountCodes.objects.get(id=dcode)

        context['code'] = code

        price = 0
        tax = 0
        total = 0
        discount = 0
        subtotal = 0
        if self.request.user.company:
            price = self.request.user.company.gen_price()
            if code:
                subtotal = self.request.user.company.gen_price(code.size)
                tax = self.request.user.company.gen_tax(code.size)
            else:
                subtotal = self.request.user.company.gen_price()
                tax = self.request.user.company.gen_tax()

            discount = price - subtotal
            total = subtotal + tax

        context['price'] = price
        context['tax'] = tax
        context['total'] = total
        context['discount'] = discount
        context['subtotal'] = subtotal

        return context


class CCSuccessView(LoginRequiredMixin, CCardRequireMixin, PaymentValidMixin, DetailView):
    template_name = 'company/ccard-success.html'
    model = Payments
    pk_url_kwarg = "uuid"

    def get_object(self, queryset=None):
        return self.get_queryset().get(uuid=self.kwargs.get(self.pk_url_kwarg), company=self.request.user.company)


class OrganizationUpdate(LoginRequiredMixin, PaymentValidMixin, UpdateView):
    template_name = 'company/organization-update.html'
    form_class = OrganizationCompanyForm
    # success_url = reverse_lazy("spec-questions")
    success_url = reverse_lazy("iso-standards")
    model = Company

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user.company


class EmployeeAddView(LoginRequiredMixin, PaymentValidMixin, AjaxableResponseMixin, CreateView):
    form_class = EmployeeForm
    template_name = "company/employee.html"
    model = Employee
    object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super(EmployeeAddView, self).get_context_data(**kwargs)
        ctx['add'] = True
        return ctx

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data(*args, **kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def form_invalid(self, form):
        response = super(EmployeeAddView, self).form_invalid(form)
        d = {'content': render_to_string(self.template_name, self.get_context_data(), request=self.request)}
        return JsonResponse(d, status=400)

    def form_valid(self, form):
        response = super(EmployeeAddView, self).form_valid(form)
        data = {'pk': self.object.pk, }
        return JsonResponse(data)

    def get_success_url(self):
        pass


class EmployeeListView(LoginRequiredMixin, PaymentValidMixin, AjaxableResponseMixin, View):
    template_name = "company/organization-employee-list.html"

    def get(self, request, *args, **kwargs):
        d = {'content': render_to_string(self.template_name, {'company': self.request.user.company}, request=request)}
        return JsonResponse(d)


class EmployeeEditView(LoginRequiredMixin, PaymentValidMixin, AjaxableResponseMixin, UpdateView):
    form_class = EmployeeForm
    template_name = "company/employee.html"
    model = Employee
    object = None

    def get_object(self):
        return Employee.objects.get(pk=self.kwargs.get('pk'), company=self.request.user.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        ctx = self.get_context_data(**kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def form_invalid(self, form):
        response = super(EmployeeEditView, self).form_invalid(form)
        d = {'content': render_to_string(self.template_name, self.get_context_data(), request=self.request)}
        return JsonResponse(d, status=400)

    def form_valid(self, form):
        response = super(EmployeeEditView, self).form_valid(form)
        data = {'pk': self.object.pk, }
        return JsonResponse(data)

    def get_success_url(self):
        pass


class EmployeeDeleteView(LoginRequiredMixin, PaymentValidMixin, AjaxableResponseMixin, DeleteView):
    template_name = "company/employee-delete.html"
    model = Employee
    object = None

    def get_object(self):
        return Employee.objects.get(pk=self.kwargs.get('pk'), company=self.request.user.company)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        ctx = self.get_context_data(**kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        data = {'pk': self.object.pk, }
        return JsonResponse(data)

    def get_success_url(self):
        pass


class OrganizationAdmins(LoginRequiredMixin, OrganizationOwner, PaymentValidMixin, TemplateView):
    template_name = 'company/organization-admins.html'

    def get_context_data(self, **kwargs):
        context = super(OrganizationAdmins, self).get_context_data(**kwargs)
        context['company'] = self.request.user.company
        return context


class OrganizationAdminsListView(LoginRequiredMixin, OrganizationOwner, AjaxableResponseMixin, View):
    template_name = "company/organization-admin-list.html"

    def get(self, request, *args, **kwargs):
        d = {'content': render_to_string(self.template_name, {
            'admins': self.request.user.company.companyusers.filter(is_company_admin=True)}, request=request)}
        return JsonResponse(d)


class OrganizationAdminsAddView(LoginRequiredMixin, OrganizationOwner, AjaxableResponseMixin, CreateView):
    form_class = AdminForm
    template_name = "company/admin.html"
    model = User
    object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, *args, **kwargs):
        ctx = super(OrganizationAdminsAddView, self).get_context_data(*args, **kwargs)
        ctx['add'] = True
        return ctx

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data(*args, **kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def form_invalid(self, form):
        response = super(OrganizationAdminsAddView, self).form_invalid(form)
        d = {'content': render_to_string(self.template_name, self.get_context_data(), request=self.request)}
        return JsonResponse(d, status=400)

    def form_valid(self, form):
        response = super(OrganizationAdminsAddView, self).form_valid(form)
        data = {'pk': self.object.pk, }
        return JsonResponse(data)

    def get_success_url(self):
        pass;


class OrganizationAdminsEditView(LoginRequiredMixin, OrganizationOwner, AjaxableResponseMixin, UpdateView):
    form_class = AdminForm
    template_name = "company/admin.html"
    model = User
    object = None

    def get_object(self):
        return self.request.user.company.companyusers.get(is_company_admin=True, pk=self.kwargs.get('pk'))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        ctx = self.get_context_data(*args, **kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def form_invalid(self, form):
        response = super(OrganizationAdminsEditView, self).form_invalid(form)
        d = {'content': render_to_string(self.template_name, self.get_context_data(), request=self.request)}
        return JsonResponse(d, status=400)

    def form_valid(self, form):
        response = super(OrganizationAdminsEditView, self).form_valid(form)
        data = {'pk': self.object.pk, }
        return JsonResponse(data)

    def get_success_url(self):
        pass


class OrganizationAdminsDeleteView(LoginRequiredMixin, OrganizationOwner, AjaxableResponseMixin, DeleteView):
    template_name = "company/admin-delete.html"
    model = User
    object = None

    def get_object(self):
        return self.request.user.company.companyusers.get(is_company_admin=True, is_company_owner=False,
                                                          pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        ctx = self.get_context_data(*args, **kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        data = {'pk': self.object.pk, }
        return JsonResponse(data)

    def get_success_url(self):
        pass


class CompanyUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'company/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy("panel")
    model = User

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user


class LegalUpdate(LoginRequiredMixin, OrganizationOwner, UpdateView):
    template_name = 'company/legal-information.html'
    form_class = TopicForm
    success_url = reverse_lazy("legal-info")
    model = Company

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user.company


class SubscriptionView(LoginRequiredMixin, OrganizationOwner, CCardRequireMixin, DetailView):
    template_name = 'company/subscription.html'

    def get_object(self, queryset=None):
        return self.request.user.company


class SubscriptionList(LoginRequiredMixin, OrganizationOwner, DetailView):
    template_name = 'company/subscription.html'

    def get_object(self, queryset=None):
        return self.request.user.company


class PaymentsListView(LoginRequiredMixin, OrganizationOwner, ListView):
    template_name = 'company/payment_list.html'
    model = Payments
    paginate_by = 10

    def get_queryset(self):
        return self.request.user.company.get_payments()


class CancelSubscriptionView(LoginRequiredMixin, CCardRequireMixin, View):
    success_url = reverse_lazy("subscription")

    def post(self, request, *args, **kwargs):
        # stripe.api_key = settings.STRIPE_SECRET_KEY
        messages.success(request, 'All subscriptions have been canceled')
        return HttpResponseRedirect(self.success_url)


class CompanyBuilderStep1View(LoginRequiredMixin, CreateView):
    template_name = 'company/profile-step1.html'
    form_class = CompanyBuilderStep1Form
    success_url = reverse_lazy("organization-step-2-update")
    model = Company

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous and request.user.company and not request.user.company.active:
            return HttpResponseRedirect(reverse_lazy('organization-step-1-update'))
        elif not request.user.is_anonymous and request.user.company and request.user.company.active:
            # return HttpResponseRedirect(reverse_lazy('spec-questions'))
            return HttpResponseRedirect(reverse_lazy('iso-standards'))

        return super(CompanyBuilderStep1View, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class CompanyBuilderStep1UpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'company/profile-step1.html'
    form_class = CompanyBuilderStep1Form
    success_url = reverse_lazy("organization-step-2-update")
    model = Company

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user.company


class CompanyBuilderStep2UpdateView(LoginRequiredMixin, OrganizationOwner, UpdateView):
    template_name = 'company/profile-step2.html'
    form_class = TopicForm
    success_url = reverse_lazy("organization-step-3-update")
    model = Company

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user.company


class CompanyBuilderStep3UpdateView(LoginRequiredMixin, OrganizationOwner, UpdateView):
    template_name = 'company/profile-step3.html'
    form_class = OrganizationBuilderStep3Form
    success_url = reverse_lazy("organization-step-4-update")
    model = Company

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs.update({'request': self.request})
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user.company


class CompanyBuilderStep4UpdateView(LoginRequiredMixin, OrganizationOwner, UpdateView):
    template_name = 'company/profile-step4.html'
    form_class = OrganizationBuilderStep4Form
    success_url = reverse_lazy("organization-step-confirmation")
    model = Company

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs.update({'request': self.request})
        return kwargs

    def get_object(self, queryset=None):
        return self.request.user.company


class CompanyBuilderConfirmationView(LoginRequiredMixin, OrganizationIsActive, TemplateView):
    template_name = 'company/profile-confirmation.html'


class StartFreeView(LoginRequiredMixin, OrganizationIsActive, OrganizationIsFree, RedirectView):
    pattern_name = 'iso-standards'

    def get_redirect_url(self, *args, **kwargs):

        iss_open = self.request.user.company.get_open_isoproduct()
        if iss_open:
            today = datetime.now()
            valid = today + timedelta(days=settings.FREE_DAYS)
            payment = Payments(company=self.request.user.company, price=0, validate=valid, success=True, free=True)
            payment.save()

            for pos in self.request.user.company.gen_price_pos():
                """
                Clark: Ignore location
                """
                # payment_position = PaymentsPositions(payment=payment, price=0, topic=pos.get('topic'),
                # location=pos.get('location'))
                payment_position = PaymentsPositions(payment=payment, price=0, topic=pos.get('topic'))
                payment_position.save()

        self.request.user.company.free = True
        self.request.user.company.selectplan = True
        self.request.user.company.save()

        return super(StartFreeView, self).get_redirect_url(*args, **kwargs)
