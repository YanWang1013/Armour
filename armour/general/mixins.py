from braces.views import AjaxResponseMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from ..legislation.models import ISOStandardResponse, ISOStandard


class AjaxableResponseMixin(AjaxResponseMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.is_ajax(request):
            raise PermissionDenied()
        return super(AjaxableResponseMixin, self).dispatch(request, *args, **kwargs)

    # for models
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        d = {'content': render_to_string(self.template_name, self.get_context_data(), request=self.request)}
        return JsonResponse(d, status=400)

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        data = {'pk': self.object and self.object.pk or '', }
        return JsonResponse(data)

    @staticmethod
    def is_ajax(request):
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


class AnonymousMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return HttpResponseRedirect(reverse_lazy(settings.LOGIN_REDIRECT_URL))
        return super(AnonymousMixin, self).dispatch(request, *args, **kwargs)


class CCardRequireMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user and not request.user.company:
            return HttpResponseRedirect(reverse_lazy("organization-step-1"))
        elif request.user and request.user.company and (
                not request.user.company.active or not request.user.company.specqgenerated):
            return HttpResponseRedirect(reverse_lazy("organization-step-1"))

        elif request.user and request.user.company and not hasattr(request.user.company,
                                                                   'copmanycc') and not request.user.company.check_valid_payment():
            return HttpResponseRedirect(reverse_lazy("cc-update"))

        return super(CCardRequireMixin, self).dispatch(request, *args, **kwargs)


class PaymentValidMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.company:
            return HttpResponseRedirect(reverse_lazy("panel"))
        elif request.user.company and request.user.company.free and not request.user.company.specqgenerated:
            return HttpResponseRedirect(reverse_lazy("organization-step-1"))
        elif not request.user.company.check_valid_payment() and not request.user.is_superuser:
            return HttpResponseRedirect(reverse_lazy("select-your-plan"))
        return super(PaymentValidMixin, self).dispatch(request, *args, **kwargs)


class PaymentValidMixinAJAX(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.company:
            return JsonResponse({'error': "You can't do this operation"}, status=400)
        elif not request.user.company.check_valid_payment():
            return JsonResponse({'error': "You can't do this operation"}, status=400)
        return super(PaymentValidMixinAJAX, self).dispatch(request, *args, **kwargs)


class OrganizationOwner(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or not request.user.is_company_owner:
            raise PermissionDenied()

        return super(OrganizationOwner, self).dispatch(request, *args, **kwargs)


"""
Clark: Don't use this class. Don't need in ISO version
"""

# FIXME possible version check needed
# class VerifyAllSpecQuestions(AccessMixin):
#     def dispatch(self, request, *args, **kwargs):
#         conf = request.user.company.get_open_isoproduct()
#         filled = LegislationSpecQuestion.objects.filter(position__register=conf).distinct().count()
#         count = request.user.company.gen_all_published_products().get('counter', 0)
#
#         if count > filled and count > 0:
#             messages.add_message(request, messages.ERROR, 'Please answer all questions')
#             return HttpResponseRedirect(reverse_lazy("spec-questions"))
#
#         return super(VerifyAllSpecQuestions, self).dispatch(request, *args, **kwargs)

"""
Clark: Refactor VerifyLegTopis with VerifyISOStandard
"""


class VerifyISOStandard(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        conf = request.user.company.get_open_isoproduct()
        stop = False
        """
        Clark: Check if conf.legislationpos is None, ignore LegislationPosition and check using ISOProduct
        """
        # if conf.legislationpos is not None:
        #     for pos in conf.legislationpos.filter(topic__isnull=False, location__isnull=False):
        #         progress = conf.get_isostandard_progress(pos.location.id, pos.topic.id)
        #         if progress.get('allprogress', 0) < 100:
        #             stop = True
        #             break
        if conf is not None:
            progress = conf.get_isostandard_progress()
            if progress.get('all_progress', 0) < 100:
                stop = True

        if stop:
            request.session['validerror'] = True

            messages.add_message(request, messages.ERROR, 'You have to answer all compliance questions')
            return HttpResponseRedirect(reverse_lazy("iso-standards"))

        return super(VerifyISOStandard, self).dispatch(request, *args, **kwargs)


"""
Clark: Don't use this class. Don't need in ISO version
"""

# class VerifyAllSpecQuestionsAJAX(AccessMixin):
#     def dispatch(self, request, *args, **kwargs):
#         conf = self.request.user.company.get_open_isoproduct()
#         filled = LegislationSpecQuestion.objects.filter(position__register=conf)
#         count = 0
#
#         for c in self.request.user.company.gen_products().get('questions', []):
#             count = count + c.get_questions().count()
#
#         if count > filled.count() and count > 0:
#             return JsonResponse({'error': "You can't do this operation"}, status=400)
#
#         return super(VerifyAllSpecQuestionsAJAX, self).dispatch(request, *args, **kwargs)

"""
Clark: Refactor VerifyLegTopisAJAX with VerifyISOStandardAJAX
"""


class VerifyISOStandardAJAX(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        conf = request.user.company.get_open_isoproduct()

        topicsres = ISOStandardResponse.objects.filter(position__register=conf, response__isnull=False).count()
        topics = ISOStandard.objects.filter(published=True).count()

        if topicsres > topics > 0:
            return JsonResponse({'error': "You can't do this operation"}, status=400)

        return super(VerifyISOStandardAJAX, self).dispatch(request, *args, **kwargs)


class OrganizationIsActive(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous:
            raise PermissionDenied()
        elif request.user.company and not request.user.company.active:
            return HttpResponseRedirect(reverse_lazy("organization-step-1"))

        return super(OrganizationIsActive, self).dispatch(request, *args, **kwargs)


class OrganizationIsFree(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous:
            raise PermissionDenied()
        elif request.user.company and request.user.company.get_free_payments_count() > 0:
            raise PermissionDenied()

        return super(OrganizationIsFree, self).dispatch(request, *args, **kwargs)


class SpecQGeneratedIsActive(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous:
            raise PermissionDenied()
        elif request.user.company and request.user.company.specqgenerated:
            return HttpResponseRedirect(reverse_lazy("select-your-plan"))

        return super(SpecQGeneratedIsActive, self).dispatch(request, *args, **kwargs)


class PlanCheckFree(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous:
            raise PermissionDenied()
        elif request.user.company and not request.user.company.free:
            return HttpResponseRedirect(reverse_lazy("iso-standards"))

        return super(PlanCheckFree, self).dispatch(request, *args, **kwargs)
