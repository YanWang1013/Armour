import uuid
from datetime import datetime

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from ..legislation.models import ISOProduct, Location, Topic, Currency, Sector, \
    Category, SourceNC, DiscountCodes, ISOStandard, Plan


class Company(models.Model):
    name = models.CharField(_('Company name'), max_length=400, )
    street = models.CharField(_('Street'), max_length=200)
    zipcode = models.CharField(_('Post code'), max_length=20)
    city = models.CharField(_('City'), max_length=200)
    email = models.EmailField(_('Email'), max_length=400)
    website = models.CharField(_('Website'), max_length=400, null=True, blank=True)
    country = CountryField(_('Country'), null=True, blank=False)
    locations = models.ManyToManyField(Location, verbose_name="Location", blank=True, related_name="companylocations")
    topics = models.ManyToManyField(Topic, verbose_name="Topics", blank=True, related_name="companytopics")
    vat = models.CharField(_('VAT number'), max_length=200, null=True)
    billcountry = CountryField(_('Country'), null=True, blank=True)
    billstreet = models.CharField(_('Street'), max_length=200, null=True, blank=True)
    billzipcode = models.CharField(_('Post code'), max_length=20, null=True, blank=True)
    billcity = models.CharField(_('City'), max_length=200, null=True, blank=True)
    active = models.BooleanField(_('Active'), default=False)
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), on_delete=models.SET_NULL, null=True,
                                 related_name="currencycompanies")
    sector = models.ManyToManyField(Sector, verbose_name="Sector", related_name="companysectors",
                                    blank=True)
    # req = models.ManyToManyField(Requirements, verbose_name="Standard or Other Requirements", blank=True)
    """
    Clark: Add ISOStandard
    """
    isostandard = models.ManyToManyField(ISOStandard, verbose_name="ISO Standards", blank=True)
    """
    Clark: Add Plan
    """
    plan = models.ManyToManyField(Plan, verbose_name="Plan", blank=True)
    scope = models.TextField(verbose_name="Organisational scope", null=True, max_length=3000, blank=True)
    category = models.ManyToManyField(Category, verbose_name="Sector", blank=True)
    image = models.ImageField(_('Logo'), null=True, blank=True)
    free = models.BooleanField(_('Free'), default=True)
    specqgenerated = models.BooleanField(_('Generated'), default=False, editable=False)
    selectplan = models.BooleanField(_('Select plan'), default=False, editable=False)

    def __str__(self):
        return self.name

    def get_free_payments_count(self):
        return self.company_payment.filter(success=True, free=True).count()

    def check_free_payments_isactive(self):
        today = datetime.now()
        active = False
        if self.company_payment.filter(success=True, free=True, validate__gte=today, date__lte=today, ).count() > 0:
            active = True
        return active

    def check_free_payments_active(self):
        today = datetime.now()
        active = None
        obj = self.company_payment.filter(success=True, free=True, validate__gte=today, date__lte=today, )

        if obj.count() > 0:
            active = obj[0]
        return active

    def get_payments(self):
        return self.company_payment.filter(success=True).order_by('-date')

    def get_finished(self):
        return self.product_company.filter(finished=True).order_by('-started')

    def gen_price(self, discount=0):
        ret = 0

        for p in self.gen_price_pos(discount):
            if not p.get('paid', False):
                ret += p.get('price')

        return round(ret, 2)

    def gen_total(self, discount=0):
        return self.gen_price(discount) + self.gen_tax(discount)

    def gen_tax(self, discount=0):
        ret = 0

        for p in self.gen_price_pos(discount):
            if not p.get('paid', False):
                ret += p.get('tax')

        return round(ret, 2)

    """
    Clark: Get total price of ISO product.
    """

    def gen_price_pos(self, discount=0):
        ret = []
        today = datetime.now()
        """
        Clark: Ignore Location Price and Location VAT Tax
        """
        if self.currency:
            # for l in self.currency.currencylocationprices.filter(location__in=self.locations.all()):
            for t in self.currency.currencytopicprices.filter(topic__in=self.topics.all()):
                paid = PaymentsPositions.objects.filter(payment__validate__gte=today, payment__date__lte=today,
                                                        payment__company=self, topic=t.topic).order_by('payment__date')
                tax = 0
                # price = l.price + t.price
                price = t.price
                if discount:
                    price = price - round(price * discount / 100, 2)
                total = price
                # if l.location.vat:
                #     tax = round(price * l.location.vat.value / 100, 2)
                #     total = total + tax
                if t.topic.vat:
                    tax = round(price * t.topic.vat.value / 100, 2)
                    total = total + tax
                if paid.count() == 0:
                    # ret.append(
                    #     {'location': l.location, 'topic': t.topic, 'price': price, 'paid': False, 'free': False,
                    #      'valid': '-', 'tax': tax, 'total': total})
                    ret.append(
                        {'topic': t.topic, 'price': price, 'paid': False, 'free': False, 'valid': '-', 'tax': tax,
                         'total': total})
                else:
                    last = paid.reverse()[0]
                    p = True
                    if last.payment.free:
                        p = False
                    # ret.append({'location': l.location, 'topic': t.topic, 'price': price, 'paid': p,
                    #             'free': last.payment.free, 'tax': tax, 'total': total,
                    #             'valid': '%s - %s' % (last.payment.date.strftime('%Y-%m-%d'),
                    #                                   last.payment.validate.strftime('%Y-%m-%d'))})
                    ret.append({'topic': t.topic, 'price': price, 'paid': p, 'free': last.payment.free, 'tax': tax,
                                'total': total,
                                'valid': '%s - %s' % (last.payment.date.strftime('%Y-%m-%d'),
                                                      last.payment.validate.strftime('%Y-%m-%d'))})

        return ret

    def gen_products(self, check_free=False):
        today = datetime.now()
        locations = []
        topics = []
        questions = []
        pairs = []
        payments = PaymentsPositions.objects.filter(payment__validate__gte=today, payment__date__lte=today,
                                                    payment__company=self, location__published=True,
                                                    topic__published=True).order_by('id')
        for p in payments:
            pair = "%s-%s" % (p.location, p.topic)
            if pair not in pairs:
                pairs.append(pair)
                if p.location.id not in locations:
                    locations.append(p.location.id)

                if p.topic.id not in topics:
                    topics.append(p.topic.id)
                """
                Clark: Why append p to question?
                """
                questions.append(p)
                if check_free:
                    break

        return {'locations': Location.objects.filter(id__in=locations).order_by('ord'),
                'topics': Topic.objects.filter(id__in=topics).order_by('ord'),
                'questions': questions}

    """
    Clark: Return ISO standard belong to ISO topic of company
    """

    def gen_iso_standards(self):
        """
        Clark: Not need questions filter
        """
        # qargs = [Q(legquestions__isnull=False, legquestions__questionsresponses__response=True,
        #            legquestions__questionsresponses__position__register=conf) | Q(legquestions__isnull=True)]
        # qargs1 = [Q(category__in=self.request.user.company.category.all()) | Q(category__isnull=True)]
        iso_standards = []
        if self.free:
            # src = LegislationTopic.objects.filter(*qargs, *qargs1, published=True, kpoints__isnull=False,
            #                                       location__id=request.GET.get('location'),
            #                                       topic__id=request.GET.get('topic'), free=True).order_by(
            #     'order').distinct()[
            #       :settings.FREE_LIMIT]
            iso_standards = self.isostandard.filter(published=True,
                                                    iss_keypoint__isnull=False,
                                                    free=True).order_by(
                'order').distinct()[:settings.FREE_STANDARD_LIMIT]
        else:
            # src = LegislationTopic.objects.filter(*qargs, *qargs1, published=True, kpoints__isnull=False,
            #                                       location__id=request.GET.get('location'),
            #                                       topic__id=request.GET.get('topic')).order_by('orderfull').distinct()
            """Clark: ???"""
            #standard_limit = self.plan
            iso_standards = self.isostandard.filter(published=True,
                                                    iss_keypoint__isnull=False).order_by(
                'order').distinct()
        return iso_standards

    def gen_all_published_products(self):
        today = datetime.now()
        questions = []
        loc = []
        top = []
        counter = 0
        legtopics = []
        questions_id = []

        payments = PaymentsPositions.objects.filter(payment__validate__gte=today, payment__date__lte=today,
                                                    payment__company=self, location__published=True,
                                                    topic__published=True)

        if payments.count() > 0:
            mytopic = payments.values_list("topic__id", flat=True).distinct()
            if len(mytopic) == 0:
                mytopic = [-1]

            myloc = payments.values_list("location__id", flat=True).distinct()
            if len(mytopic) == 0:
                myloc = [-1]
        else:
            myloc = self.locations.all().values_list("id", flat=True).distinct()
            mytopic = self.topics.all().values_list("id", flat=True).distinct()
        """
        Clark: I think the id__in values are interchanged at the below <for> rows 
        """
        # for l in Location.objects.filter(published=True, id__in=mytopic).order_by('ord'):
        #    for t in Topic.objects.filter(published=True, id__in=myloc).order_by('ord'):

        # for l in Location.objects.filter(published=True, id__in=myloc).order_by('ord'):
        #     for t in Topic.objects.filter(published=True, id__in=mytopic).order_by('ord'):
        #         qargs = [
        #             Q(legtopic__category__in=self.category.filter(published=True)) | Q(legtopic__category__isnull=True)]
        #
        #         if not self.free:
        #             q = Question.objects.filter(legtopic__published=True, legtopic__location=l, legtopic__topic=t,
        #                                         *qargs)
        #         else:
        #             q = Question.objects.filter(legtopic__published=True, legtopic__location=l, legtopic__topic=t,
        #                                         *qargs)
        #
        #         if q.count() > 0:
        #             questions.append({'location': l, 'topic': t, 'get_questions': q})
        #             loc.append(l)
        #             top.append(t)
        #             counter += q.count()
        #             legtopics += q.values_list('legtopic__id', flat=True)
        #             questions_id += q.values_list("id", flat=True).distinct()

        return {'locations': loc, 'topics': top, 'questions': questions, 'counter': counter, 'legtopics': legtopics,
                'questions_id': questions_id}

    def gen_version_published_products(self, version):
        questions = []
        loc = []
        top = []
        counter = 0
        legtopics = []

        # for l in Location.objects.filter(published=True).order_by('ord'):
        #     for t in Topic.objects.filter(published=True).order_by('ord'):
        #         qargs = [
        #             Q(legtopic__category__in=self.category.filter(published=True)) | Q(legtopic__category__isnull=True)]
        #
        #         if not self.free:
        #             q = Question.objects.filter(legtopic__version=version, legtopic__published=True,
        #                                         legtopic__location=l, legtopic__topic=t, *qargs)
        #         else:
        #             q = Question.objects.filter(legtopic__free=True, legtopic__version=version,
        #                                         legtopic__published=True, legtopic__location=l, legtopic__topic=t,
        #                                         *qargs)
        #
        #         if q.count() > 0:
        #             questions.append({'location': l, 'topic': t, 'get_questions': q})
        #             loc.append(l)
        #             top.append(t)
        #             counter += q.count()
        #             legtopics += q.values_list('legtopic__id', flat=True)

        return {'locations': loc, 'topics': top, 'questions': questions, 'counter': counter, 'legtopics': legtopics}

    def check_valid_payment(self):
        ret = False
        today = datetime.now()
        if self.company_payment.filter(validate__gte=today, date__lte=today).count() > 0:
            ret = True

        return ret

    """
    Clark: Refactor get_open_register with get_open_isoproduct
    """

    def get_open_isoproduct(self):
        return ISOProduct.objects.filter(finished=False, company=self).first()

    """
    Clark: Refactor get_last_register with get_last_isoproduct
    """

    def get_last_isoproduct(self):
        return ISOProduct.objects.filter(company=self).order_by("-id").first()

    def get_outer_sources(self):
        return SourceNC.objects.filter(outersources__isnull=False, outersources__company=self).order_by(
            "name").distinct()

    class Meta:
        verbose_name = _(u'Company')
        verbose_name_plural = _(u'Company')


class CompanyCC(models.Model):
    company = models.OneToOneField(Company, related_name="copmanycc", on_delete=models.CASCADE)
    cc4 = models.CharField(_('CC digit'), max_length=4, )
    stripe_id = models.CharField(_('City'), max_length=1000, null=True)
    name = models.CharField(_('Name'), max_length=400, )
    surname = models.CharField(_('Surname'), max_length=400, )
    email = models.EmailField(_('Email'), max_length=400, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _(u'Company')
        verbose_name_plural = _(u'Company')


class Payments(models.Model):
    company = models.ForeignKey(Company, related_name="company_payment", on_delete=models.CASCADE)
    stripe_subs_id = models.CharField(_('Subscription ID'), max_length=1000, null=True, editable=False)
    stripe_plan_id = models.CharField(_('Plan ID'), max_length=1000, null=True, editable=False)
    price = models.FloatField(_('Price'), validators=[MinValueValidator(0)])
    tax = models.FloatField(_('VAT'), validators=[MinValueValidator(0)], null=True, blank=False)
    total = models.FloatField(_('Total'), validators=[MinValueValidator(0)], null=True, blank=False)
    date = models.DateTimeField(_('Created'), auto_now_add=True)
    validate = models.DateTimeField(_('Validation date'), )
    success = models.BooleanField(_('Success'), default=False)
    uuid = models.UUIDField(editable=False, null=True)
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'), on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    free = models.BooleanField(_('Free'), default=False)
    stripe_invoice_id = models.CharField(_('Invoice ID'), max_length=1000, null=True, editable=False)
    stripe_invoice_pdf = models.URLField(_('Invoice PDF'), max_length=1000, null=True)
    stripe_charge_id = models.CharField(_('Charge ID'), max_length=1000, null=True, editable=False)
    discount_code = models.ForeignKey(DiscountCodes, verbose_name=_('Discount code'), editable=False,
                                      on_delete=models.SET_NULL, null=True, related_name="discountpayments")
    discount_size = models.PositiveIntegerField("Size [%]", null=True, editable=False)
    discount = models.FloatField(_('Discount'), null=True, editable=False)
    refund = models.BooleanField(_('Refund'), default=False)
    refunded = models.BooleanField(_('Refunded'), default=False, editable=False)
    stripe_refund_id = models.CharField(_('Refund ID'), max_length=1000, null=True, editable=False)
    stripe_refund_charge_id = models.CharField(_('Refund Charge ID'), max_length=1000, null=True, editable=False)
    refunddate = models.DateTimeField(_('Refund date'), null=True, blank=True)

    def __str__(self):
        return str(self.price)

    def save(self, *args, **kwargs):
        super(Payments, self).save(*args, **kwargs)
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
            self.save()

    class Meta:
        verbose_name = _(u'Payments')
        verbose_name_plural = _(u'Payments')
        ordering = ["-date"]


class PaymentsPositions(models.Model):
    payment = models.ForeignKey(Payments, related_name="payment_position", on_delete=models.CASCADE)
    price = models.FloatField(_('Price'), validators=[MinValueValidator(0)])
    date = models.DateTimeField(_('Created'), auto_now_add=True)
    location = models.ForeignKey(Location, verbose_name="Location", blank=True, null=True, on_delete=models.SET_NULL)
    topic = models.ForeignKey(Topic, verbose_name="Topics", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.price)

    def get_questions(self):
        # qargs = [Q(legtopic__category__in=self.payment.company.category.all()) | Q(legtopic__category__isnull=True)]
        #
        # return Question.objects.filter(legtopic__topic=self.topic, legtopic__location=self.location, published=True,
        #                                legtopic__published=True, *qargs)
        return []

    class Meta:
        verbose_name = _(u'Payments position')
        verbose_name_plural = _(u'Payments positions')


class Employee(models.Model):
    company = models.ForeignKey(Company, related_name="employee", on_delete=models.CASCADE)
    fname = models.CharField(_('Fist Name'), max_length=400, )
    lname = models.CharField(_('Last name'), max_length=400, )
    email = models.EmailField(_('Email'), max_length=400, null=True)
    position = models.CharField(_('Position'), max_length=150, )
    status = models.CharField(_('Status'), max_length=150, )

    def __str__(self):
        return "%s %s" % (self.fname, self.lname)

    class Meta:
        verbose_name = _(u'Employee')
        verbose_name_plural = _(u'Employees')
