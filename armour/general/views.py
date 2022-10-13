import mimetypes
import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView, View
from django.views.generic.edit import FormView

from armour.general.mixins import AjaxableResponseMixin
from .forms import ContactForm
from .models import Tip
from ..general.mixins import CCardRequireMixin, OrganizationIsActive
from ..legislation.models import Guidance, Template, ISOStandardNCResponse


class TMPView(LoginRequiredMixin, TemplateView):
    template_name = 'general/templates.html'


def home_redirect(request):
    if settings.DEBUG:
        return HttpResponseRedirect(reverse_lazy("login"))
    else:
        return  redirect('https://www.armour.ai')


class HomeView(TemplateView):
    template_name = 'landing/home.html'


class PaneView(LoginRequiredMixin, OrganizationIsActive, CCardRequireMixin,  TemplateView):
    template_name = 'general/panel.html'

    def get_context_data(self, **kwargs):
        context = super(PaneView, self).get_context_data(**kwargs)
        company = self.request.user.company
        context['company'] = company
        payments = company.gen_price_pos()
        context['paymentsall'] = len(payments)
        context['payments'] = payments[:5]
        context['nectversions'] = None  # FIXME after versioning
        context['open'] = company.get_open_isoproduct()
        finshed = company.get_finished()
        context['finshed'] = finshed[:5]
        context['finshedcount'] = len(finshed)
        guidance = Guidance.objects.all()
        context['guidance'] = guidance[:5]
        context['guidancecount'] = len(guidance)

        if company.free:
            docs = Template.objects.filter(free=True)
        else:
            docs = Template.objects.all()

        context['templates'] = docs[:5]
        context['templatescount'] = len(docs)

        nc = []
        outer = []
        outersrc = self.request.user.company.ncouterresponse_company.all().distinct()
        outercnt = outersrc.count()
        for o in outersrc.order_by("-started")[:5]:
            outer.append(o)
        inner = []
        innercnt = 0
        if len(outer) < 5:
            opened = self.request.user.company.get_open_isoproduct()
            if opened:
                innersrc = ISOStandardNCResponse.objects.filter(issrepsonse__product=opened).distinct()
                innercnt = innersrc.count()
                for o in innersrc.order_by("-started")[:5-len(outer)]:
                    inner.append(o)
        nc = []
        idx = outercnt + innercnt

        for o in outer+inner:
            nc.append({"idx": idx, "ncobj": o})
            idx -= 1

        context['nc']=nc
        context['nccnt'] = outercnt + innercnt
        return context

class ContactView(AjaxableResponseMixin, FormView):
    form_class = ContactForm
    template_name = "landing/contact-form.html"
    object = None

    def get(self, request, *args, **kwargs):
        ctx = super(ContactView, self).get_context_data(*args, **kwargs)
        d = {'content': render_to_string(self.template_name, ctx, request=request)}
        return JsonResponse(d)

    def form_valid(self, form):
        response = super(ContactView, self).form_valid(form)

        if settings.EMAIL_CONTACT_ADMINS:
            message = render_to_string("email/contact.txt",
                                       {'data': form.cleaned_data}, )

            mail = EmailMessage(subject="Contact message", body=message,
                                from_email=settings.DEFAULT_FROM_EMAIL, to=settings.EMAIL_CONTACT_ADMINS)

            mail.send()

        initd = dict()
        ctx = self.get_context_data()
        ctx['form'] = self.form_class(**initd)
        data = {'content': render_to_string(self.template_name, ctx, request=self.request)}
        return JsonResponse(data)

    def get_success_url(self):
        pass


class TipDetailView(LoginRequiredMixin, DetailView):
    template_name = 'general/tip.html'
    model = Tip


class TipsListView(LoginRequiredMixin, ListView):
    template_name = 'general/tips_list.html'
    model = Tip
    paginate_by = 10


class PrivateDocView(LoginRequiredMixin, View):
    def get(self, request, path, *args, **kwargs):
        fullpath = "%s/%s" % (settings.MEDIA_ROOT, path)

        if os.path.exists(fullpath):
            with open(fullpath, 'rb') as fh:
                mimetype, encoding = mimetypes.guess_type(fullpath)
                response = HttpResponse(fh.read(), content_type=mimetype)
                response['Content-Disposition'] = 'filename=' + os.path.basename(fullpath)
                return response

        raise Http404
