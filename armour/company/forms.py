# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from ..company.models import Company, CompanyCC, Payments, PaymentsPositions, Employee
from django.utils.translation import ugettext_lazy as _
import stripe
from django.conf import settings
from datetime import datetime, timedelta
from ..legislation.models import Topic, Location, DiscountCodes
from django.template.defaultfilters import filesizeformat

User = get_user_model()
y_range = lambda x, y: zip(range(x, y), range(x, y))
months = y_range(1, 13)


class BillingCompanyForm(forms.ModelForm):
    fname = forms.CharField(label=_("First name"), required=True, max_length=400)
    lname = forms.CharField(label=_("Last name"), required=True, max_length=400)
    email = forms.CharField()
    card_num = forms.CharField(label='Card Number')
    card_code = forms.CharField(help_text='3 or 4 digit number, usually on the back',
                                widget=forms.TextInput(attrs={'size': 3}), label='CCV', max_length=4)
    month_expires = forms.ChoiceField(choices=months)
    year_expires = forms.ChoiceField(choices=[], )
    card_token = forms.CharField(widget=forms.HiddenInput, required=True)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(BillingCompanyForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            if not kwargs.get('instance').billcity:
                self.initial['billcity'] = kwargs.get('instance').city

            if not kwargs.get('instance').billzipcode:
                self.initial['billzipcode'] = kwargs.get('instance').zipcode

            if not kwargs.get('instance').billcountry:
                self.initial['billcountry'] = kwargs.get('instance').country

            if not kwargs.get('instance').billstreet:
                self.initial['billstreet'] = kwargs.get('instance').street

            if not hasattr(kwargs.get('instance'), "copmanycc"):
                self.initial['fname'] = request.user.first_name
                self.initial['lname'] = request.user.last_name
                self.initial['email'] = request.user.email
            else:
                self.initial['fname'] = kwargs.get('instance').copmanycc.name
                self.initial['lname'] = kwargs.get('instance').copmanycc.surname
                self.initial['email'] = kwargs.get('instance').copmanycc.email
                self.fields['card_num'].widget.attrs['placeholder'] = "**** **** **** %s" % kwargs.get(
                    'instance').copmanycc.cc4

        self.fields['name'].widget.attrs['class'] = "form-control"
        self.fields['billstreet'].widget.attrs['class'] = "form-control"
        self.fields['billzipcode'].widget.attrs['class'] = "form-control"
        self.fields['billcity'].widget.attrs['class'] = "form-control"
        self.fields['billcountry'].widget.attrs['class'] = "form-control"
        self.fields['fname'].widget.attrs['class'] = "form-control"
        self.fields['lname'].widget.attrs['class'] = "form-control"
        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['card_num'].widget.attrs['class'] = "form-control"
        self.fields['card_code'].widget.attrs['class'] = "form-control"
        self.fields['month_expires'].widget.attrs['class'] = "form-control"
        self.fields['year_expires'].widget.attrs['class'] = "form-control"
        self.fields['currency'].widget.attrs['class'] = "form-control"
        self.fields['currency'].required = True

        years = datetime.now().year
        cy = years + 8
        y = []
        while years <= cy:
            y.append(("%s" % years, "%s" % years))
            years += 1

        self.fields['year_expires'].choices = y

    def save(self, commit=True, *args, **kwargs):
        obj = super(BillingCompanyForm, self).save(commit=False)
        obj.save()

        data = self.cleaned_data
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not hasattr(obj, 'copmanycc'):
            cust_data = stripe.Customer.create(
                email=data.get('email'),
                source=data.get('card_token'),
                name="%s %s" % (data.get('fname'), data.get('lname'))
            )

            cc = CompanyCC(company=obj, cc4=data.get('card_num')[0:4], stripe_id=cust_data.get('id'),
                           name=data.get('fname'), surname=data.get('lname'), email=data.get('email'))
            cc.save()
        else:
            stripe.Customer.modify(obj.copmanycc.stripe_id,
                                   email=data.get('email'),
                                   source=data.get('card_token'),
                                   name="%s %s" % (data.get('fname'), data.get('lname'))
                                   )

            obj.copmanycc.cc4 = data.get('card_num')[0:4]
            obj.copmanycc.name = data.get('fname')
            obj.copmanycc.surname = data.get('fname')
            obj.copmanycc.email = data.get('email')
            obj.copmanycc.save()

        return obj

    class Meta:
        model = Company
        fields = (
            'name', 'billstreet', 'billzipcode', 'billcity', 'billcountry', 'card_num', 'year_expires', 'month_expires',
            'card_code', 'fname', 'lname', 'email', 'card_token', 'currency')


class PaymentForm(forms.Form):
    hidden_field = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, request, *args, **kwargs):
        self.company = request.user.company
        self.stripe_subs_id = None
        self.stripe_subs_status = None
        self.stripe_plan_id = None
        self.stripe_invoice_id = None
        self.stripe_invoice_pdf = None
        self.stripe_charge_id = None
        self.code = None
        self.discount = 0
        self.discount_size = 0
        dcode = request.session.get('dcode', None)
        if dcode:
            self.code = DiscountCodes.objects.get(id=dcode)
            self.net = self.company.gen_price()
            self.price_pos = self.company.gen_price_pos(self.code.size)
            self.price = self.company.gen_price(self.code.size)
            self.tax = self.company.gen_tax(self.code.size)
            self.total = self.price + self.tax

            self.discount = self.net - self.price
            self.discount_size = self.code.size

        else:
            self.price_pos = self.company.gen_price_pos()
            self.price = self.company.gen_price()
            self.tax = self.company.gen_tax()
            self.total = self.price + self.tax

        super(PaymentForm, self).__init__(*args, **kwargs)

    def clean(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        items = []
        for pos in self.price_pos:
            if not pos.get('paid', False):
                plan = stripe.Plan.create(
                    amount=int(pos.get('price') * 100),
                    interval="year",
                    product={
                        "name": "Year plan %s - %s for %s" % (
                            pos.get('location').name, pos.get('topic').name, self.company.name)
                    },
                    currency=self.company.currency.name,
                )
                if pos.get('location').vat:
                    items.append({"plan": plan.get('id', None), "tax_rates": [pos.get('location').vat.stripeId]})
                else:
                    items.append({"plan": plan.get('id', None)})

        if len(items) > 0:
            self.stripe_plan_id = plan.get('id', None)
            subs = stripe.Subscription.create(
                customer=self.company.copmanycc.stripe_id,
                items=items,
            )
            self.stripe_subs_id = subs.get('id', None)
            self.stripe_subs_status = subs.get('status', '')
            self.stripe_invoice_id = subs.get('latest_invoice', '')
            if self.stripe_invoice_id:
                inv = stripe.Invoice.retrieve(self.stripe_invoice_id)
                pdf = inv.get('invoice_pdf', None)
                if pdf and pdf != 'null':
                    self.stripe_invoice_pdf = pdf

                charge = inv.get('charge', None)
                if charge and charge != 'null':
                    self.stripe_charge_id = charge

        return self.cleaned_data

    def save(self, commit=True, *args, **kwargs):
        today = datetime.now()
        if self.stripe_subs_status == 'active':
            valid = today + timedelta(days=365)
            success = True
        else:
            success = False
            valid = today - timedelta(days=1)

        payment = Payments(company=self.company, price=self.price, stripe_subs_id=self.stripe_subs_id,
                           stripe_invoice_id=self.stripe_invoice_id, stripe_charge_id=self.stripe_charge_id,
                           stripe_plan_id=self.stripe_plan_id, validate=valid, success=success, tax=self.tax,
                           total=self.total, stripe_invoice_pdf=self.stripe_invoice_pdf,
                           discount_code=self.code, discount=self.discount, discount_size=self.discount_size,
                           currency=self.company.currency)
        payment.save()

        for pos in self.price_pos:
            payp = PaymentsPositions(payment=payment, price=pos.get('price'), topic=pos.get('topic'),
                                     location=pos.get('location'))
            payp.save()

        self.company.free = False
        self.company.selectplan = True
        self.company.save()

        if self.code:
            self.code.used = True
            self.code.save()

        return payment

    class Meta:
        fields = ('hidden_field',)


class ProfileCompanyForm(forms.ModelForm):

    def clean_image(self):
        document = self.cleaned_data['image']
        if hasattr(document, 'size'):
            if document.size > settings.MAX_UPLOAD_SIZE:
                error_msg = 'The picture is too big (%s). The limit is %s'
                sizes = filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(document.size)
                raise forms.ValidationError(error_msg % sizes)
        return document

    first_name = forms.CharField(label=_("First name"), required=True, )
    last_name = forms.CharField(label=_("Last name"), required=True, )
    usemail = forms.CharField(label=_("Email"), required=True, )

    def __init__(self, request, *args, **kwargs):
        self.request = request

        super(ProfileCompanyForm, self).__init__(*args, **kwargs)
        self.initial['first_name'] = request.user.first_name
        self.initial['last_name'] = request.user.last_name
        self.initial['usemail'] = request.user.email

        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['first_name'].widget.attrs['class'] = "form-control"
        self.fields['last_name'].widget.attrs['class'] = "form-control"
        self.fields['name'].widget.attrs['class'] = "form-control"
        self.fields['street'].widget.attrs['class'] = "form-control"
        self.fields['zipcode'].widget.attrs['class'] = "form-control"
        self.fields['city'].widget.attrs['class'] = "form-control"
        self.fields['country'].widget.attrs['class'] = "form-control"
        self.fields['website'].widget.attrs['class'] = "form-control"
        self.fields['usemail'].widget.attrs['class'] = "form-control"
        self.fields['currency'].widget.attrs['class'] = "form-control"

    def clean_usemail(self):
        usemail = self.cleaned_data.get('usemail')

        if User.objects.filter(email=usemail).exclude(id=self.request.user.id).count() > 0:
            raise forms.ValidationError(_("You can not use this email, use another one."))

        return usemail

    def save(self, commit=True, *args, **kwargs):
        obj = super(ProfileCompanyForm, self).save(commit=False, *args, **kwargs)
        obj.save()
        self.save_m2m()
        data = self.cleaned_data
        if data['first_name'] and data['last_name'] and data['usemail']:
            self.request.user.first_name = data['first_name']
            self.request.user.last_name = data['last_name']
            self.request.user.email = data['usemail']
            self.request.user.save()

        return obj

    class Meta:
        model = Company
        fields = ('name', 'street', 'zipcode', 'city', 'email', 'usemail', 'website', 'country', 'currency', 'image',)


class OrganizationCompanyForm(ProfileCompanyForm):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(OrganizationCompanyForm, self).__init__(request, *args, **kwargs)
        self.fields['scope'].widget.attrs['class'] = "form-control"
        self.fields['scope'].required = False
        """
        Clark: Add query set of Location and Topic for form fields
        """
        # self.fields['locations'].required = True
        # self.fields['locations'].queryset = self.fields['locations'].queryset.filter(published=True)
        self.fields['topics'].required = True
        self.fields['topics'].queryset = self.fields['topics'].queryset.filter(published=True)

        self.fields['category'].required = True
        self.fields['category'].queryset = self.fields['category'].queryset.filter(published=True)
        # self.fields['req'].widget.attrs['class'] = "form-control"
        # self.fields['req'].required = False
        # self.fields['req'].queryset = self.fields['req'].queryset.filter(published=True)
        self.fields['usemail'].required = False
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False

    def save(self, commit=True, *args, **kwargs):
        obj = super(OrganizationCompanyForm, self).save(commit=False, *args, **kwargs)

        if commit:
            obj.save()
            self.save_m2m()

        return obj

    class Meta:
        model = Company
        """
        Clark: Add location and topic, Remove req
        """
        fields = ProfileCompanyForm.Meta.fields + ( 'scope', 'category', 'locations', 'topics')
        widgets = {
            'scope': forms.Textarea(attrs={'rows': 2}),
        }


class EmployeeForm(forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        self.company = request.user.company
        super(EmployeeForm, self).__init__(*args, **kwargs)

        self.fields['fname'].widget.attrs['class'] = "form-control"
        self.fields['lname'].widget.attrs['class'] = "form-control"
        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['position'].widget.attrs['class'] = "form-control"
        self.fields['status'].widget.attrs['class'] = "form-control"
        self.fields['fname'].required = True
        self.fields['lname'].required = True
        self.fields['email'].required = True
        self.fields['position'].required = True
        self.fields['status'].required = True

    def save(self, commit=True, *args, **kwargs):
        obj = super(EmployeeForm, self).save(commit=False, *args, **kwargs)
        if commit:
            obj.company = self.company
            obj.save()

        return obj

    class Meta:
        model = Employee
        fields = ('fname', 'lname', 'email', 'position', 'status')


class AdminForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, strip=False, required=True,
                                min_length=6)

    def __init__(self, request, *args, **kwargs):
        self.company = request.user.company
        super(AdminForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs['class'] = "form-control"
        self.fields['last_name'].widget.attrs['class'] = "form-control"
        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['password1'].widget.attrs['class'] = "form-control"
        self.fields['password1'].required = False
        self.fields['is_active'].widget.attrs['class'] = "form-check-input"

    def save(self, commit=True, *args, **kwargs):
        obj = super(AdminForm, self).save(commit=False, *args, **kwargs)
        data = self.cleaned_data
        if commit:
            obj.company = self.company
            obj.is_company_admin = True
            obj.save()

            if data.get('password1', None) and data.get('password1', None) != '':
                obj.set_password(data['password1'])
                obj.save()

        return obj

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'is_active')


"""
Clark: Refactor LegalForm as TopicForm and Remove locations
"""


class TopicForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(),
                                            widget=forms.CheckboxSelectMultiple(),
                                            required=True)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(TopicForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, *args, **kwargs):
        obj = super(TopicForm, self).save(commit=False)
        obj.save()
        self.save_m2m()

        return obj

    class Meta:
        model = Company
        fields = ('topics',)


class CompanyBuilderStep1Form(forms.ModelForm):

    def clean_image(self):
        document = self.cleaned_data['image']
        if hasattr(document, 'size'):
            if document.size > settings.MAX_UPLOAD_SIZE:
                error_msg = 'The picture is too big (%s). The limit is %s'
                sizes = filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(document.size)
                raise forms.ValidationError(error_msg % sizes)
        return document

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.logusser = None

        super(CompanyBuilderStep1Form, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = "form-control"
        self.fields['street'].widget.attrs['class'] = "form-control"
        self.fields['zipcode'].widget.attrs['class'] = "form-control"
        self.fields['city'].widget.attrs['class'] = "form-control"
        self.fields['country'].widget.attrs['class'] = "form-control"
        self.fields['website'].widget.attrs['class'] = "form-control"
        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['currency'].widget.attrs['class'] = "form-control"
        self.fields['scope'].widget.attrs['class'] = "form-control"
        self.fields['currency'].required = True

    def save(self, commit=True, *args, **kwargs):
        obj = super(CompanyBuilderStep1Form, self).save(commit=False)
        obj.save()
        self.save_m2m()
        self.request.user.company = obj
        self.request.user.save()
        return obj

    class Meta:
        model = Company
        fields = ('name', 'street', 'city', 'country', 'website', 'currency', 'zipcode', 'email', 'image', 'scope')

        widgets = {
            'scope': forms.Textarea(attrs={'rows': 2})
        }


class OrganizationBuilderStep3Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationBuilderStep3Form, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = "form-control"
        self.fields['category'].required = True
        self.fields['category'].queryset = self.fields['category'].queryset.filter(published=True)

    def save(self, commit=True, *args, **kwargs):
        obj = super(OrganizationBuilderStep3Form, self).save(commit=False)
        if commit:
            obj.save()
            self.save_m2m()

        return obj

    class Meta:
        model = Company
        fields = ('category',)


class OrganizationBuilderStep4Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationBuilderStep4Form, self).__init__(*args, **kwargs)
        """
        Clark: Add filter by company topic
        """
        topics = kwargs.get('instance').topics
        if topics.count() > 0:
            topic_ids = topics.values_list("id", flat=True).distinct()
            if len(topic_ids) == 0:
                topic_ids = []
        else:
            topic_ids = []
        self.fields['isostandard'].widget.attrs['class'] = "form-control"
        self.fields['isostandard'].required = True
        self.fields['isostandard'].queryset = self.fields['isostandard'].queryset.filter(published=True,
                                                                                         topic__in=topic_ids)

    def save(self, commit=True, *args, **kwargs):
        obj = super(OrganizationBuilderStep4Form, self).save(commit=False)
        obj.active = True
        """
        Clark: Set specqgenerated to True
        """
        obj.specqgenerated = True
        if commit:
            obj.save()
            self.save_m2m()

        return obj

    class Meta:
        model = Company
        fields = ('isostandard',)


class UserProfileForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        self.company = request.user.company
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = "form-control"
        self.fields['last_name'].widget.attrs['class'] = "form-control"
        self.fields['email'].widget.attrs['class'] = "form-control"
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class CompanyPaymentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompanyPaymentsForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)

    def save(self, commit=True, *args, **kwargs):
        obj = super(CompanyPaymentsForm, self).save(commit=False, *args, **kwargs)
        obj.save()
        if obj.refund and obj.stripe_charge_id and not obj.refunded:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            ref = stripe.Refund.create(charge=obj.stripe_charge_id, )
            status = ref.get('status', '')
            if status == "succeeded":
                obj.refunded = True
                obj.stripe_refund_id = ref.get('id', '')
                obj.stripe_refund_charge_id = ref.get('charge', '')
                obj.refunddate = datetime.now()
                obj.save()

        return obj

    class Meta:
        model = Payments
        fields = '__all__'
