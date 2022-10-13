import json
import mimetypes
import os
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from django.http import JsonResponse, Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DetailView, View, RedirectView, TemplateView, DeleteView
from wkhtmltopdf.views import PDFTemplateView

from .models import ISOProduct, ISOStandard, \
    ISOStandardResponse, ISOStandardNCResponse, SourceNC, \
    Template, NCOuterResponse, NCOuterResponseStates, \
    ISOStandardKeyPointResponse, KeyPoint, Guidance, DiscountCodes, DocumentFile, DocumentFolder, Plan
from ..company.models import PaymentsPositions
from ..general.mixins import PaymentValidMixin, AjaxableResponseMixin, VerifyISOStandard, \
    VerifyISOStandardAJAX, PaymentValidMixinAJAX, OrganizationIsActive, PlanCheckFree

"""
Clark: Don't need in ISO version. 
"""

# class SpecificQuestions(LoginRequiredMixin, OrganizationIsActive, DetailView):
#     template_name = 'legislation/specific-questions.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(SpecificQuestions, self).get_context_data(**kwargs)
#         conf = self.request.user.company.get_open_isoproduct()
#         src = self.request.user.company.gen_all_published_products()
#
#         if len(src.get('questions_id', [])) > 0:
#             LegislationSpecQuestion.objects.filter(position__register=conf, ).exclude(
#                 question__id__in=src.get('questions_id', [])).delete()
#
#         context['data'] = src
#         context['selected'] = LegislationSpecQuestion.objects.filter(position__register=conf, )
#         return context
#
#     def get_object(self, **kwargs):
#         conf = self.request.user.company.get_open_isoproduct()
#
#         if not conf:
#             conf = ISOProduct.objects.create(company=self.request.user.company)
#             return conf
#         else:
#             return conf


"""
Clark: Don't need in ISO version.
"""

# class SetSpecQuestionView(LoginRequiredMixin, OrganizationIsActive, AjaxableResponseMixin, View):
#     def post(self, request, *args, **kwargs):
#         conf = self.request.user.company.get_open_isoproduct()
#
#         body_unicode = request.body.decode('utf-8')
#         data = json.loads(body_unicode)
#         question = data.get('question')
#         reply = data.get('reply', '0')
#         answer = False
#         if int(reply) == 1:
#             answer = True
#
#         quest = Question.objects.get(id=question)
#
#         poz, created = LegislationPosition.objects.get_or_create(register=conf, topic=quest.isostandard.topic,
#                                                                  location=quest.isostandard.location)
#
#         sc, created = LegislationSpecQuestion.objects.get_or_create(position=poz, question=quest)
#         sc.response = answer
#         sc.save()
#
#         return JsonResponse({"status": "OK"})


"""
Clark:  Remove VerifyAllSpecQuestions and Add OrganizationIsActive
        Refactor LegislationTopicsView with ISOStandardView
"""


class ISOStandardView(LoginRequiredMixin, PaymentValidMixin, OrganizationIsActive, DetailView):
    # class LegislationTopicsView(LoginRequiredMixin, PaymentValidMixin, VerifyAllSpecQuestions, DetailView):
    template_name = 'legislation/iso-standards.html'

    def get_context_data(self, **kwargs):
        context = super(ISOStandardView, self).get_context_data(**kwargs)

        # context['data'] = self.request.user.company.gen_all_published_products()
        # context['data'] = self.request.user.company.gen_products(check_free=True)
        """
        Clark: Add to create ISO Product, ISOStandardResponse
        """
        if not self.request.user.company.get_open_isoproduct():
            ISOProduct.objects.create(company=self.request.user.company)
            for iss in self.request.user.company.gen_iso_standards():
                ISOStandardResponse.objects.create(product=self.request.user.company.get_open_isoproduct(),
                                                   isostandard=iss)

        return context

    def get_object(self, **kwargs):
        return self.request.user.company.get_open_isoproduct()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


"""
Clark:  Remove VerifyAllSpecQuestionsAJAX
        Refactor LegislationTopicsContentView with ISOStandardContentView
"""


# class LegislationTopicsContentView(LoginRequiredMixin, PaymentValidMixinAJAX, AjaxableResponseMixin,
#                                   VerifyAllSpecQuestionsAJAX, View):
class ISOStandardContentView(LoginRequiredMixin, PaymentValidMixinAJAX, AjaxableResponseMixin, View):
    template_name = "legislation/iso-standards-content.html"

    def get(self, request, *args, **kwargs):
        conf = self.request.user.company.get_open_isoproduct()

        isostandards = []
        firstnotfilled = None
        mess = self.request.session.get('validerror', False)
        src = self.request.user.company.gen_iso_standards()
        for iss in src:
            isostandards.append(iss)
            if mess and not firstnotfilled:
                if iss.iss_response_standard.filter(product=conf) == 0:
                    firstnotfilled = len(isostandards)

                for r in iss.iss_response_standard.filter(product=conf):
                    if not r.verify():
                        firstnotfilled = len(isostandards)
                        break
        """
        Clark: Ignore Requirements (from self.request.user.company.req)
        """
        # if self.request.user.company.free:
        #     if len(ltopics) < settings.FREE_LIMIT:
        #         rqcount = settings.FREE_LIMIT - len(ltopics)
        #         if rqcount > 0:
        #             rq = self.request.user.company.req.filter(published=True,
        #                                                       reqpoints__isnull=False).distinct().order_by(
        #                 'name')[:rqcount]
        #             for l in rq:
        #                 ltopics.append(l)
        #
        #                 if mess and not firstnotfilled:
        #                     if l.postopicresponses.filter(position__register=conf).count() == 0:
        #                         firstnotfilled = len(ltopics) + 1
        #
        #                     for r in l.reqreply.filter(position__register=conf):
        #                         if not r.verify():
        #                             firstnotfilled = len(ltopics) + 1
        #                             break;
        #
        #
        # else:
        #     rq = self.request.user.company.req.filter(published=True, reqpoints__isnull=False).distinct().order_by(
        #         'name')
        #     for l in rq:
        #         ltopics.append(l)
        #         if mess and not firstnotfilled:
        #             if l.postopicresponses.filter(position__register=conf).count() == 0:
        #                 firstnotfilled = len(ltopics)
        #
        #             for r in l.reqreply.filter(position__register=conf):
        #                 if not r.verify():
        #                     firstnotfilled = len(ltopics)
        #                     break;

        q_answers = [Q(issresponse__isnull=False) | Q(issresponse__isostandard__isnull=False)]
        answers = ISOStandardKeyPointResponse.objects.filter(issresponse__product=conf, *q_answers)
        progress = conf.get_isostandard_progress()

        # posqanswers = [
        #     Q(req__isnull=True, location__id=request.GET.get('location'), topic__id=request.GET.get('topic')) | Q(
        #         req__isnull=False)]
        #
        # position = None
        # if not mess:
        #     lastposition = conf.legislationpos.filter(*posqanswers).order_by("-topicpos").first()
        #     if lastposition:
        #         position = lastposition.topicpos
        #
        # elif firstnotfilled:
        #     position = firstnotfilled

        position = firstnotfilled  # ???

        if mess:
            del self.request.session['validerror']

        d = {'content': render_to_string(self.template_name,
                                         {'isostandards': isostandards, 'answers': answers, 'position': position,
                                          }, request=request),
             'product_progress': progress.get('product_progress'),
             'all_progress': progress.get('all_progress'),
             'counter': len(isostandards)}
        return JsonResponse(d)


"""
Clark: This store compliance value (YES/NO) for Key Points of Legislation Topic (ISO Standard).
    Key Points change to Requirements.
    This is Ajax request.
    Refactor SetLegistaltionTopicView with SetISOStandardView
"""


class SetISOStandardView(LoginRequiredMixin, PaymentValidMixinAJAX, AjaxableResponseMixin, View):
    def post(self, request, *args, **kwargs):
        today = datetime.now()
        paids = PaymentsPositions.objects.filter(payment__validate__gte=today, payment__date__lte=today,
                                                 payment__company=self.request.user.company)

        if paids.count() == 0:
            return JsonResponse({'error': "You can't do this operation"}, status=400)
        else:

            conf = self.request.user.company.get_open_isoproduct()

            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            reply = data.get('reply', '')
            nc_desc = data.get('nc_desc', '')
            keypoint = data.get('keypoint', None)
            keypoint_note = data.get('keypoint_note', '')
            kp = KeyPoint.objects.get(id=keypoint)
            position = data.get('position', '')

            if kp.isostandard:
                """
                Clark: replace 'legislation' with 'register', ignore LegislationPosition and add product
                """
                # poz, created = LegislationPosition.objects.get_or_create(register=conf, topic=kp.isostandard.topic,
                #                                                          location=kp.isostandard.location)
                # sc, created = ISOStandardResponse.objects.get_or_create(product=conf, isostandard=kp.isostandard)

                iss_response = ISOStandardResponse.objects.filter(isostandard=kp.isostandard, product=conf).first()
                # elif kp.req:
                """
                Clark: replace 'legislation' with 'register' and ignore Requirement (req)
                """
                # poz, created = LegislationPosition.objects.get_or_create(legislation=conf, req=kp.req)
                # poz, created = LegislationPosition.objects.get_or_create(register=conf, req=kp.req)
                #
                # sc, created = ISOStandardResponse.objects.get_or_create(position=poz, req=kp.req)

            else:
                return JsonResponse({'error': "You can't do this operation"}, status=400)

            pos = 0
            if reply == '' or reply == 0:
                pos = 0
            else:
                pos = int(reply)

            kppoz, created = ISOStandardKeyPointResponse.objects.get_or_create(issresponse=iss_response, point=kp)

            kppoz.note = keypoint_note
            kppoz.response = pos
            kppoz.ncnote = nc_desc
            kppoz.save()
            # progress = conf.get_isostandard_progress(data.get('location'), data.get('topic'))
            progress = conf.get_isostandard_progress()

            """
            Clark: position means tab number ( tab = iso standard) and ignore LegislationPosition (legislationpos)
            """
            # if position:
            #     poz.topicpos = position
            #     poz.save()
            #
            #     posqanswers = [Q(req__isnull=True, location__id=data.get('location'), topic__id=data.get('topic')) | Q(
            #         req__isnull=False)]
            #
            #     conf.legislationpos.filter(*posqanswers).exclude(id=poz.id).update(topicpos=1)

            iss_response.status = iss_response.set_status_number()
            iss_response.save()

            return JsonResponse({"status": "OK", 'product_progress': progress.get('product_progress'),
                                 'all_progress': progress.get('all_progress')})


"""
Clark: Refactor LegislationNonConformanceView with ISONCView
"""


class ISONCView(LoginRequiredMixin, PaymentValidMixin, VerifyISOStandard,
                DetailView):
    template_name = 'legislation/iso-nonconformance.html'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        exists = []
        iss = ISOStandardKeyPointResponse.objects.filter(issresponse__product=obj,
                                                         response__in=[0]).distinct()

        if iss.count() == 0:
            ISOStandardNCResponse.objects.filter(issrepsonse__product=obj).delete()
            return super(ISONCView, self).get(request, *args, **kwargs)
        else:
            for answer in iss:
                sc, created = ISOStandardNCResponse.objects.get_or_create(issrepsonse=answer.issresponse,
                                                                          point=answer.point)
                if not sc.ncdesc:
                    sc.ncdesc = answer.ncnote
                    sc.save()
                exists.append(sc.id)
            ISOStandardNCResponse.objects.filter(issrepsonse__product=obj).exclude(
                id__in=exists).delete()
            return super(ISONCView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ISONCView, self).get_context_data(**kwargs)
        obj = self.get_object()
        nonconformance = []
        inner = ISOStandardNCResponse.objects.filter(
            issrepsonse__product=obj).distinct().order_by("started")

        # outer = self.request.user.company.companyouternc.all().distinct().order_by("started")
        outer = []
        for o in inner:
            nonconformance.append(o)

        for o in outer:
            nonconformance.append(o)

        context['nonconformance'] = nonconformance

        context['sourceslegal'] = SourceNC.objects.filter(default=True).order_by("name")
        context['sources'] = SourceNC.objects.filter(defaulto=True).order_by("name")

        return context

    def get_object(self):
        return self.request.user.company.get_open_isoproduct()


class SetNonConformanceView(LoginRequiredMixin, PaymentValidMixinAJAX, AjaxableResponseMixin,
                            VerifyISOStandardAJAX, View):
    def post(self, request, pk, *args, **kwargs):
        conf = self.request.user.company.get_open_isoproduct()
        try:
            obj = ISOStandardNCResponse.objects.get(issrepsonse__product=conf, id=pk)
        except:
            return JsonResponse({"status": "ERROR"}, status=400)

        sc = None
        if request.POST.get('source', None):
            sc = SourceNC.objects.get(id=request.POST.get('source'))

        obj.source = sc
        identified = request.POST.get('identified', '')
        if identified:
            obj.identified_by = self.request.user.company.companyusers.get(id=identified)

        priority = request.POST.get('priority', '')
        if priority:
            obj.priority = priority

        assign = request.POST.get('assign', '')
        if assign:
            assinguser = self.request.user.company.companyusers.get(id=assign)
            if not obj.assign or (obj.assign and obj.assign != assinguser):
                current_site = Site.objects.get_current()
                protocol = settings.IS_HTTPS and "https://" or "http://"
                baseurl = protocol + current_site.domain

                ctx = {'user': assinguser, 'baseurl': baseurl, 'nc': obj}
                content = render_to_string("email/new-nc.html", ctx, request=self.request)

                mail = EmailMessage(subject="New NC has been assigned to you", body=content,
                                    from_email=settings.DEFAULT_FROM_EMAIL, to=[assinguser.email])
                mail.content_subtype = 'html'
                mail.send()

            obj.assign = assinguser

        obj.root = request.POST.get('root', '')
        obj.corrective = request.POST.get('corrective', '')
        revieweddate = request.POST.get('reviewed', '')
        if revieweddate:
            revieweddate = datetime.strptime(revieweddate, "%d.%m.%Y").strftime("%Y-%m-%d")
            obj.revieweddate = revieweddate

        completeddate = request.POST.get('completeddate', '')
        if completeddate:
            completeddate = datetime.strptime(completeddate, "%d.%m.%Y").strftime("%Y-%m-%d")
            obj.completeddate = completeddate

        completed_by = request.POST.get('completed_by', '')
        if completed_by:
            obj.completed_by = self.request.user.company.companyusers.get(id=completed_by)

        reviewed_by = request.POST.get('reviewed_by', '')
        if reviewed_by:
            obj.reviewed_by = self.request.user.company.companyusers.get(id=reviewed_by)

        description = request.POST.get('description', '')
        if description:
            obj.ncdesc = description

        obj.save()
        content = ''
        createnew = request.POST.get('add-new', "0")

        if createnew == '1':
            no = self.request.user.company.companyouternc.all().distinct().count() + ISOStandardNCResponse.objects.filter(
                issrepsonse__product=conf).distinct().count() + 1
            newobj = NCOuterResponse.objects.create(company=self.request.user.company, initialrecord=True,
                                                    no=no)
            start = 0

            nonconformance = []
            inner = []

            if conf:
                inner = ISOStandardNCResponse.objects.filter(
                    issrepsonse__product=conf).distinct().order_by("started")

            outer = self.request.user.company.companyouternc.all().distinct().order_by("started")

            for o in inner:
                nonconformance.append(o)

            for o in outer:
                nonconformance.append(o)

            content = render_to_string("legislation/outer-nc-content.html",
                                       {'nonconformance': nonconformance, 'start': start,
                                        'company': self.request.user.company,
                                        'inittab': len(nonconformance),
                                        'sourceslegal': SourceNC.objects.filter(default=True).order_by("name"),
                                        'sources': SourceNC.objects.filter(defaulto=True).order_by("name"), },
                                       request=request)

        return JsonResponse(
            {"status": "OK", 'verify': obj.verify() and 1 or 0, 'id': obj.id, 'nctype': 'inner', 'content': content})


class FinishView(LoginRequiredMixin, PaymentValidMixin, RedirectView):
    pattern_name = 'product-report'

    def get_redirect_url(self, *args, **kwargs):
        iss_open = self.request.user.company.get_open_isoproduct()
        if iss_open:
            today = datetime.now()
            iss_open.finished = True
            iss_open.finish_date = today
            iss_open.save()
            iss_folder = DocumentFolder.objects.filter(usage=DocumentFolder.TEMPLATES).first()
            for d in Template.objects.all():
                try:
                    cp = ContentFile(d.file.read())
                except:
                    continue

                iss_file = DocumentFile()
                iss_file.folder = iss_folder
                iss_file.name = d.file.name
                iss_file.file = cp
                iss_file.product = iss_open
                iss_file.save()

            for nco in NCOuterResponse.objects.filter(company=self.request.user.company,
                                                      initialrecord=False).order_by('id'):
                nc = NCOuterResponseStates(product=iss_open, source=nco.source,
                                           started=nco.started, updated=nco.updated,
                                           identified=nco.identified,
                                           assigned=nco.assigned, containment=nco.containment,
                                           completion=nco.completion,
                                           root=nco.root, corrective=nco.corrective, cost=nco.cost,
                                           reviewed=nco.reviewed, desc=nco.description,
                                           assign=nco.assign, verified=nco.verified, priority=nco.priority,
                                           identified_by=nco.identified_by,
                                           completeddate=nco.completeddate, completed_by=nco.completed_by,
                                           revieweddate=nco.revieweddate,
                                           reviewed_by=nco.reviewed_by)
                nc.save()

        return super(FinishView, self).get_redirect_url(*args, **kwargs)


"""
Clark: Refactor LegislationListView with ProductListView
"""


class ProductListView(LoginRequiredMixin, PaymentValidMixin, DetailView):
    template_name = 'legislation/product-report.html'

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        iss_open = self.request.user.company.get_open_isoproduct()
        if iss_open is not None:
            context['open_product'] = self.request.user.company.get_open_isoproduct()
            context['open_product_standards'] = iss_open.get_iso_standards()
        finished_products = self.request.user.company.get_finished()
        if finished_products is not None:
            context['finished_products'] = finished_products
        context['docs'] = Template.objects.all()

        return context

    def get_object(self, **kwargs):
        return self.request.user.company


class StartNewView(FinishView):
    pattern_name = 'organization-update'


class LegislationDocView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        doc = get_object_or_404(LegislationDocument, uuid=pk, legislation__company=self.request.user.company)
        fullpath = doc.file.path

        if os.path.exists(fullpath):
            with open(fullpath, 'rb') as fh:
                mimetype, encoding = mimetypes.guess_type(fullpath)
                response = HttpResponse(fh.read(), content_type=mimetype)
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(fullpath)
                return response

        raise Http404


"""
Clark: Refactor LegislationReportView with ISOReportView
"""


class ISOReportView(LoginRequiredMixin, PDFTemplateView):
    template_name = 'pdf/report.html'
    filename = 'my_pdf.pdf'
    show_content_in_browser = True
    object = None
    cmd_options = {
        'orientation': 'landscape',
    }

    def get(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(ISOProduct, uuid=pk, company=self.request.user.company)
        return super(ISOReportView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ISOReportView, self).get_context_data(**kwargs)
        # context['staticroot'] = settings.STATIC_ROOT
        context['staticroot'] = settings.STATICFILES_DIRS
        context['product'] = self.object

        # product_id = self.request.GET.get('product', '')
        # products = self.object.get_products()
        # if product_id:
        #     products = products.filter(id=product_id)
        #
        # ncs = self.object.get_ncs()
        # if product_id:
        #     ncs = ncs.filter(issrepsonse__product__id=product_id)
        #
        # context['products'] = products
        # context['ncs'] = ncs

        return context


class OuterNonConformanceView(LoginRequiredMixin, PaymentValidMixin, TemplateView):
    template_name = 'legislation/outer-nonconformance.html'

    def get(self, request, *args, **kwargs):
        topics = self.request.user.company.companyouternc.all().count()
        if topics == 0:
            t = NCOuterResponse.objects.create(company=self.request.user.company, initialrecord=True)
        return super(OuterNonConformanceView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OuterNonConformanceView, self).get_context_data(**kwargs)
        obj = self.get_object()

        exists = []
        topics = ISOStandardKeyPointResponse.objects.filter(isostandardresponse__position__register=obj,
                                                            response__in=[0]).distinct()
        for answer in topics:
            sc, created = ISOStandardNCResponse.objects.get_or_create(topicreply=answer.isostandardresponse,
                                                                      point=answer.point)
            if not sc.ncdesc:
                sc.ncdesc = answer.ncnote
                sc.save()

            exists.append(sc.id)

        ISOStandardNCResponse.objects.filter(topicreply__position__register=obj).exclude(
            id__in=exists).delete()

        start = 0
        topics = 0
        context['nonconformance'] = []
        inner = []
        no = 1
        if obj:
            for nc in ISOStandardNCResponse.objects.filter(topicreply__position__register=obj).order_by(
                    "started"):
                nc.no = no
                nc.save()
                no += 1

            inner = ISOStandardNCResponse.objects.filter(topicreply__position__register=obj).order_by(
                "started")

        context['start'] = start
        for nc in self.request.user.company.companyouternc.all().order_by("started"):
            nc.no = no
            nc.save()
            no += 1

        outer = self.request.user.company.companyouternc.all().order_by("started")
        context['nonconformance'] = []
        for o in inner:
            context['nonconformance'].append(o)

        for o in outer:
            context['nonconformance'].append(o)

        context['inittab'] = int(1)
        context['company'] = self.request.user.company

        context['sources'] = SourceNC.objects.filter(defaulto=True).order_by("name")
        context['sourceslegal'] = SourceNC.objects.filter(default=True).order_by("name")
        context['nc_open'] = self.request.GET.get('nc-open', None)

        return context

    def get_object(self):
        return self.request.user.company.get_open_isoproduct()


class SetOuterNonConformanceView(LoginRequiredMixin, PaymentValidMixinAJAX, AjaxableResponseMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            obj = NCOuterResponse.objects.get(company=self.request.user.company, id=pk)
        except:
            return JsonResponse({"status": "ERROR"}, status=400)

        sc = None
        if request.POST.get('source', None):
            sc = SourceNC.objects.get(id=request.POST.get('source'))

        obj.source = sc
        identified = request.POST.get('identified', '')
        if identified:
            obj.identified_by = self.request.user.company.companyusers.get(id=identified)

        priority = request.POST.get('priority', '')
        if priority:
            obj.priority = priority

        assign = request.POST.get('assign', '')
        if assign:
            assinguser = self.request.user.company.companyusers.get(id=assign)
            if not obj.assign or (obj.assign and obj.assign != assinguser):
                current_site = Site.objects.get_current()
                protocol = settings.IS_HTTPS and "https://" or "http://"
                baseurl = protocol + current_site.domain

                ctx = {'user': assinguser, 'baseurl': baseurl, 'nc': obj}
                content = render_to_string("email/new-nc.html", ctx, request=self.request)

                mail = EmailMessage(subject="New", body=content,
                                    from_email=settings.DEFAULT_FROM_EMAIL, to=[assinguser.email])
                mail.content_subtype = 'html'
                mail.send()

            obj.assign = assinguser

        obj.root = request.POST.get('root', '')
        obj.corrective = request.POST.get('corrective', '')
        obj.description = request.POST.get('description', '')

        revieweddate = request.POST.get('revieweddate', '')
        if revieweddate:
            revieweddate = datetime.strptime(revieweddate, "%d.%m.%Y").strftime("%Y-%m-%d")
            obj.revieweddate = revieweddate

        completeddate = request.POST.get('completeddate', '')

        if completeddate:
            completeddate = datetime.strptime(completeddate, "%d.%m.%Y").strftime("%Y-%m-%d")
            obj.completeddate = completeddate

        completed_by = request.POST.get('completed_by', '')
        if completed_by:
            obj.completed_by = self.request.user.company.companyusers.get(id=completed_by)

        reviewed_by = request.POST.get('reviewed_by', '')
        if reviewed_by:
            obj.reviewed_by = self.request.user.company.companyusers.get(id=reviewed_by)

        if sc or request.POST.get('reviewed_by', '') or request.POST.get('completed_by', '') or request.POST.get(
                'revieweddate', '') or request.POST.get('completeddate', '') or request.POST.get('identified',
                                                                                                 '') or request.POST.get(
            'assigned', '') or request.POST.get(
            'containment', '') or request.POST.get('completion', '') or request.POST.get('root',
                                                                                         '') or request.POST.get(
            'corrective', '') or request.POST.get('priority', '') or request.POST.get('reviewed',
                                                                                      '') or request.POST.get(
            'description', ''):
            obj.initialrecord = False

        obj.save()

        createnew = request.POST.get('add-new', "0")
        content = ''
        if createnew == '1':
            leg = self.request.user.company.get_open_isoproduct()
            no = self.request.user.company.companyouternc.all().distinct().count() + ISOStandardNCResponse.objects.filter(
                topicreply__position__register=leg).distinct().count() + 1

            newobj = NCOuterResponse.objects.create(company=self.request.user.company, initialrecord=True,
                                                    no=no)
            start = 0

            nonconformance = []
            inner = []
            if leg:
                inner = ISOStandardNCResponse.objects.filter(
                    topicreply__position__register=leg).distinct().order_by("started")

            outer = self.request.user.company.companyouternc.all().distinct().order_by("started")

            for o in inner:
                nonconformance.append(o)

            for o in outer:
                nonconformance.append(o)

            content = render_to_string("legislation/outer-nc-content.html",
                                       {'nonconformance': nonconformance, 'start': start,
                                        'company': self.request.user.company,
                                        'inittab': len(nonconformance),
                                        'sources': SourceNC.objects.filter(defaulto=True).order_by("name"),
                                        'sourceslegal': SourceNC.objects.filter(default=True).order_by("name")},
                                       request=request)

        return JsonResponse(
            {"status": "OK", 'verify': obj.verify() and 1 or 0, 'id': obj.id, 'content': content, 'nctype': 'outer'})


class LegislationDeleteView(LoginRequiredMixin, AjaxableResponseMixin, DeleteView):
    template_name = "legislation/product-delete.html"
    model = ISOProduct
    object = None

    def get_object(self):
        return ISOProduct.objects.get(pk=self.kwargs.get('pk'), company=self.request.user.company)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        ctx = self.get_context_data(*args, **kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = {'pk': self.kwargs.get('pk'), }
        self.object.delete()
        return JsonResponse(data)

    def get_success_url(self):
        pass


class LegislationNCReportView(LoginRequiredMixin, PDFTemplateView):
    template_name = 'pdf/report_nc.html'
    filename = 'my_pdf.pdf'
    show_content_in_browser = True
    object = None
    cmd_options = {
        'orientation': 'landscape',
    }

    def get(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(ISOProduct, uuid=pk, company=self.request.user.company)
        return super(LegislationNCReportView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LegislationNCReportView, self).get_context_data(**kwargs)
        context['staticroot'] = settings.STATIC_ROOT
        context['object'] = self.object
        context['closed'] = []
        context['opened'] = []
        context['company'] = self.request.user.company
        mode = kwargs.get('mode', 'All')
        product = self.request.GET.get('product', None)
        source = self.request.GET.get('source', None)

        if source:
            ncsource = SourceNC.objects.filter(id=source).first()
            if ncsource:
                mode = ncsource.name

        elif mode == 'outer' and not source:
            mode = "All"

        context['mode'] = mode
        opened = []
        closed = []

        if mode == "inner" and product:
            src = ISOStandardNCResponse.objects.filter(topicreply__position__register=self.object,
                                                       topicreply__position__id=product)
            opened = src.filter(verified=False).values_list('source__name', 'ncdesc', 'updated', 'root',
                                                            'corrective', 'no').distinct().order_by("started")
            closed = src.filter(verified=True).values_list('source__name', 'ncdesc', 'updated', 'root',
                                                           'corrective', 'no').distinct().order_by("started")

        elif mode == "inner" and not product:
            src = ISOStandardNCResponse.objects.filter(topicreply__position__register=self.object)
            opened = src.filter(verified=False).values_list('source__name', 'ncdesc', 'updated', 'root',
                                                            'corrective', 'no').distinct().order_by("started")
            closed = src.filter(verified=True).values_list('source__name', 'ncdesc', 'updated', 'root',
                                                           'corrective', 'no').distinct().order_by("started")

        elif mode == "outer" and product:
            src = NCOuterResponse.objects.filter(topicreply__position__id=product)
            opened = src.filter(verified=False, ).values_list('source__name', 'description', 'updated', 'root',
                                                              'corrective', 'no').distinct().order_by("started")
            closed = src.filter(verified=True, ).values_list('source__name', 'description', 'updated', 'root',
                                                             'corrective', 'no').distinct().order_by("started")

        elif mode == "outer" and not product:
            src = NCOuterResponse.objects.all()
            opened = src.filter(verified=False).values_list('source__name', 'description', 'updated', 'root',
                                                            'corrective', ).distinct().order_by("started")
            closed = src.filter(verified=True).values_list('source__name', 'description', 'updated', 'root',
                                                           'corrective', 'no').distinct().order_by("started")

        for o in opened:
            context['opened'].append(o)

        for o in closed:
            context['closed'].append(o)

        context['cnt'] = len(context['closed']) + len(context['opened'])
        return context


class LegislationNCOuterReportView(LoginRequiredMixin, PDFTemplateView):
    template_name = 'pdf/report_nc.html'
    filename = 'my_pdf.pdf'
    show_content_in_browser = True
    object = None
    cmd_options = {
        'orientation': 'landscape',
    }

    def get_context_data(self, **kwargs):
        context = super(LegislationNCOuterReportView, self).get_context_data(**kwargs)
        context['staticroot'] = settings.STATIC_ROOT
        context['closed'] = []
        context['opened'] = []
        context['company'] = self.request.user.company
        source = self.request.GET.get('source', None)
        mode = "All"
        if source:
            ncsource = SourceNC.objects.filter(id=source).first()
            if ncsource:
                mode = ncsource.name

        context['mode'] = mode
        opened = []
        closed = []

        if source:
            src = NCOuterResponse.objects.filter(source__id=source, company=self.request.user.company)
            opened = src.filter(verified=False, ).values_list('source__name', 'description', 'updated', 'root',
                                                              'corrective', 'no').distinct().order_by("started")
            closed = src.filter(verified=True, ).values_list('source__name', 'description', 'updated', 'root',
                                                             'corrective', 'no').distinct().order_by("started")

        else:
            src = NCOuterResponse.objects.filter(company=self.request.user.company)
            opened = src.filter(verified=False).values_list('source__name', 'description', 'updated', 'root',
                                                            'corrective', 'no').distinct().order_by("started")
            closed = src.filter(verified=True).values_list('source__name', 'description', 'updated', 'root',
                                                           'corrective', 'no').distinct().order_by("started")

        for o in opened:
            context['opened'].append(o)

        for o in closed:
            context['closed'].append(o)

        context['cnt'] = len(context['closed']) + len(context['opened'])
        return context


"""
Clark: Don't need in ISO Version.
"""

# class SpecQuestionConfirmationView(LoginRequiredMixin, OrganizationIsActive, TemplateView):
#     template_name = 'legislation/spec-question-confirmation.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(SpecQuestionConfirmationView, self).get_context_data(**kwargs)
#
#         data = self.request.user.company.gen_all_published_products().get('legtopics', [])
#         count = 0
#
#         if len(data) > 0:
#             conf = self.request.user.company.get_open_isoproduct()
#             qargs = [Q(legquestions__isnull=False, legquestions__questionsresponses__response=True,
#                        legquestions__questionsresponses__position__register=conf) | Q(legquestions__isnull=True)]
#             qargs1 = [Q(category__in=self.request.user.company.category.all()) | Q(category__isnull=True)]
#
#             src = ISOStandard.objects.filter(*qargs, *qargs1, published=True, kpoints__isnull=False).distinct()
#
#             count = src.count() + self.request.user.company.req.all().count()
#
#             if self.request.user.company.active and not self.request.user.company.specqgenerated:
#                 self.request.user.company.specqgenerated = True
#                 self.request.user.company.save()
#
#         context['count'] = count
#         return context

"""
Clark: Refactor PlanSpecQuestionConfirmationView with PlanSelectView
"""


class PlanSelectView(LoginRequiredMixin, OrganizationIsActive, PlanCheckFree, TemplateView):
    template_name = 'legislation/plan-select.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.company.active and not self.request.user.company.specqgenerated:
            self.request.user.company.specqgenerated = True
            self.request.user.company.save()
        """
        Clark: Add to create ISO Product
        """
        if not self.request.user.company.get_open_isoproduct():
            ISOProduct.objects.create(company=self.request.user.company)

        return super(PlanSelectView, self).get(request, *args, **kwargs)


"""
Clark: Restore TemplateList View
"""


class TemplateListView(LoginRequiredMixin, DetailView):
    template_name = 'legislation/template-list.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        qargs = [Q(locations__isnull=True, topics__isnull=True, category__isnull=True) | Q(
            locations__in=company.locations.all()) | Q(topics__in=company.topics.all()) | Q(
            category__in=company.category.all())]

        if self.request.user.company.free:
            context['docs'] = Template.objects.filter(free=True, published=True, *qargs).distinct()
        else:
            context['docs'] = Template.objects.filter(published=True, *qargs).distinct()

        return context

    def get_object(self):
        return self.request.user.company


class GuidanceListView(LoginRequiredMixin, DetailView):
    template_name = 'legislation/guidance-list.html'

    def get_context_data(self, **kwargs):
        context = super(GuidanceListView, self).get_context_data(**kwargs)
        company = self.request.user.company
        qargs = [Q(locations__isnull=True, topics__isnull=True, category__isnull=True) | Q(
            locations__in=company.locations.all()) | Q(topics__in=company.topics.all()) | Q(
            category__in=company.category.all())]
        context['docs'] = Guidance.objects.filter(published=True, *qargs).distinct()

        return context

    def get_object(self):
        return self.request.user.company


"""
Clark: ???Not changed topicresponsekeyp with isostandardresponsekeyp yet
"""


class LegUpdateView(LoginRequiredMixin, PaymentValidMixin, View):
    def post(self, request, *args, **kwargs):
        origin = self.request.user.company.get_open_isoproduct()
        newversion = False  # FIXME after versioning
        if not newversion:
            messages.add_message(self.request, messages.ERROR, "Newer version doesn't exist", )
            return HttpResponseRedirect(reverse_lazy("product-report"))

        new = False
        if not origin:
            origin = self.request.user.company.get_last_isoproduct()
            new = True

        if origin:
            conf = ISOProduct.objects.get(id=origin.id)
            if new:
                conf.pk = None
                conf.save()
                conf.finished = False
                conf.finish_date = None
                conf.uuid = str(uuid.uuid4())

            conf.version = newversion
            conf.save()

            for originpos in origin.legislationpos.all():
                pos = origin.legislationpos.get(id=originpos.id)
                if new:
                    pos.pk = None
                    pos.save()
                    pos.register = conf

                pos.save()

                for originsq in originpos.specquerypos.all():
                    sq = originpos.specquerypos.get(id=originsq.id)
                    if new:
                        sq.pk = None
                        sq.save()
                        sq.position = pos

                    sqfirst = Question.objects.filter(legtopic__version=newversion,
                                                      parent=originsq.question).first()
                    if sqfirst:
                        sq.question = sqfirst

                    sq.save()

                for origintp in originpos.postopicresponses.all():
                    sq = originpos.postopicresponses.get(id=origintp.id)
                    if new:
                        sq.pk = None
                        sq.save()
                        sq.position = pos

                    if origintp.isostandard:
                        sqfirst = ISOStandard.objects.filter(version=newversion,
                                                             parent=origintp.isostandard).first()
                        if sqfirst:
                            sq.isostandard = sqfirst

                    sq.save()

                    for isostandardresponsekeyp in origintp.isostandardresponsekeyp.all():
                        kp = origintp.isostandardresponsekeyp.get(id=isostandardresponsekeyp.id)

                        kpfirst = KeyPoint.objects.filter(legtopic__version=newversion,
                                                          parent=isostandardresponsekeyp.point).first()
                        if new:
                            kp.pk = None
                            kp.isostandardresponse = sq
                            kp.save()

                        if kpfirst:
                            kp.point = kpfirst

                        kp.save()

                    if new:
                        for isostandardresponsenc in origintp.topicnon.all():
                            kp = origintp.topicnon.get(id=isostandardresponsenc.id)
                            kp.pk = None
                            kp.save()
                            kp.topicreply = sq
                            kp.save()

            self.request.user.company.version = newversion
            self.request.user.company.save()

            messages.add_message(self.request, messages.SUCCESS,
                                 'The update has been completed to %s version' % newversion.version, )

        else:
            messages.add_message(self.request, messages.ERROR, 'No legislative process', )

        return HttpResponseRedirect(reverse_lazy("product-report"))


class SetDiscountView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        nx = request.POST.get('next', 'cc-update')

        if request.session.has_key('dcode'):
            del request.session['dcode']
            messages.add_message(self.request, messages.SUCCESS, 'The discount has been removed')
            return HttpResponseRedirect(reverse_lazy(nx))
        else:

            code = request.POST.get('discount-code', None)
            if not code:
                messages.add_message(self.request, messages.ERROR, "Discount code is empty", )
                return HttpResponseRedirect(reverse_lazy(nx))

            qargs = [Q(multiple=False, used=False) | Q(multiple=True)]

            try:
                dcode = DiscountCodes.objects.get(active=True, code=code, *qargs)
            except:
                messages.add_message(self.request, messages.ERROR, "Discount code does't exist or is inactive", )
                return HttpResponseRedirect(reverse_lazy(nx))

            request.session['dcode'] = dcode.id

            messages.add_message(self.request, messages.SUCCESS, 'The discount has been calculated')

            return HttpResponseRedirect(reverse_lazy(nx))


class ManagementSystemView(LoginRequiredMixin, TemplateView):
    template_name = "legislation/manage-system.html"

    # fullpath = "%s/" % settings.MEDIA_ROOT

    def get(self, request, *args, **kwargs):
        return super(ManagementSystemView, self).get(request, *args, **kwargs)


class ManagementSystemGetView(LoginRequiredMixin, AjaxableResponseMixin, View):

    def post(self, request, **kwargs):
        parentId = self.request.POST.get('level')
        action = self.request.POST.get('action')
        product = self.request.user.company.get_open_isoproduct()
        # rename folder
        if action == 'rename_folder':
            value = self.request.POST.get('value')
            targetId = self.request.POST.get('id')
            if parentId == "0":
                parentId = None
            if targetId == "0":
                folder = DocumentFolder()
                folder.product = product
                folder.parent_id = parentId
                folder.user = self.request.user
                folder.name = value
                folder.created_by_admin = False
                folder.save()
                targetId = folder.id
            else:
                folder = get_object_or_404(DocumentFolder, pk=targetId)
                folder.name = value
                folder.save()
            return JsonResponse({"status": True, "id": targetId}, status=200)
        # rename file
        if action == 'rename_file':
            value = self.request.POST.get('value')
            file = get_object_or_404(DocumentFile, pk=parentId)
            file.name = value
            file.save()
            return JsonResponse({"status": True}, status=200)
        # delete folder by id with all subfolders and sub files
        if action == 'delete_folder':
            folder = get_object_or_404(DocumentFolder, pk=parentId)
            exists = []
            exists = folder.recursive(folder, exists)
            DocumentFolder.objects.filter(
                id__in=exists).delete()
            DocumentFile.objects.filter(folder__id__in=exists).delete()
            return JsonResponse({"status": True}, status=200)
        # delete file only
        if action == 'delete_file':
            file = get_object_or_404(DocumentFile, pk=parentId)
            file.delete()
            return JsonResponse({"status": True}, status=200)
        # get parent folder's
        if action == 'parent':
            parentFolder = get_object_or_404(DocumentFolder, pk=parentId)
            if parentFolder.parent is None:
                parentId = "0"
            else:
                parentId = parentFolder.parent.id
        fPriFolder = Q(user=None)
        fMyFolder = Q(user=self.request.user)
        if parentId == "0" or parentId == None:
            fParent = Q(parent=None)
            fFolder = Q(folder=None)
        else:
            fParent = Q(parent__id=parentId)
            fFolder = Q(folder__id=parentId)

        qsFolder = DocumentFolder.objects.filter((fPriFolder | fMyFolder) & fParent)
        qsFile = DocumentFile.objects.filter(fFolder)
        if product is not None:
            qsFolder = qsFolder.filter((fPriFolder | Q(product=product)))
            qsFile = qsFile.filter(Q(product=product))
        else:
            qsFolder = qsFolder.filter((fPriFolder & Q(product=None)))
            qsFile = qsFile.filter(Q(product=None))
        qsFolder = qsFolder.order_by('user').order_by('created_at')
        folders = list(qsFolder.values())
        files = list(qsFile.values())

        return JsonResponse({"status": True, "folder": folders, "file": files, "parent": parentId}, status=200)


class ManagementSystemFileUploadView(LoginRequiredMixin, AjaxableResponseMixin, View):
    def post(self, request, **kwargs):
        try:
            folderId = self.request.POST.get('level')
            fileId = self.request.POST.get('fileId')
            fileName = self.request.POST.get('fileName')
            product = self.request.user.company.get_open_isoproduct()
            documentFile = DocumentFile()
            if self.request.FILES is None:
                return JsonResponse({"status": False, "msg": "File Required"}, status=200)
            file = request.FILES.get('upload')
            documentFile.product = product
            documentFile.file = file
            if folderId != "0" and folderId is not None:
                documentFolder = get_object_or_404(DocumentFolder, pk=folderId)
                documentFile.folder = documentFolder
            documentFile.name = fileName
            documentFile.user = request.user
            documentFile.save()
            return JsonResponse({"status": True}, status=200)
        except ():
            return JsonResponse({"status": False}, status=200)


class PlanView(LoginRequiredMixin, TemplateView):
    template_name = "legislation/plans.html"
    model = Plan

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['items'] = list(Plan.objects.filter(published=True))
        # context['year_items'] = list(Plan.objects.filter(period=Plan.ANNUAL))
        return context


class PdfView(TemplateView):
    template_name = 'pdf/report.html'

