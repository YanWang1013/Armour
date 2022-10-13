from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from tabbed_admin import TabbedModelAdmin

from armour.user.forms import MyUserMixinForm
from armour.user.models import User
from .forms import CompanyPaymentsForm
from .models import Company, Employee, Payments


class CompanyUsersOptions(NestedStackedInline, admin.StackedInline):
    model = User
    extra = 0

    form = MyUserMixinForm
    readonly_fields = ('date_joined', 'last_login',)


class EmployeeOptions(NestedStackedInline, admin.StackedInline):
    model = Employee
    extra = 0


class PaymentsOptions(NestedStackedInline, admin.StackedInline):
    model = Payments
    form = CompanyPaymentsForm
    extra = 0
    readonly_fields = ['discount_code', 'discount_size', 'discount', 'stripe_subs_id', 'stripe_plan_id',
                       'stripe_invoice_id', 'stripe_charge_id', 'refunded', 'refunddate', 'stripe_refund_id',
                       'stripe_refund_charge_id']


@admin.register(Company)
class CompanyAdmin(TabbedModelAdmin, NestedModelAdmin):
    list_display = ('name', 'street', 'zipcode', 'city', 'email', 'website', 'country', 'currency', 'active',)

    tab_general = (
        (None, {
            'fields': (
                'name', 'street', 'zipcode', 'city', 'email', 'website', 'country', 'currency', 'active',),
        }),
    )
    tab_admins = (CompanyUsersOptions,)
    tab_employee = (EmployeeOptions,)
    tab_payments = (PaymentsOptions,)

    tabs = [
        ('General', tab_general),
        ('Admins', tab_admins),
        ('Employees', tab_employee),
        ('Payments', tab_payments),
    ]
