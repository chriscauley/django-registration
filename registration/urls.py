from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView

from models import RegistrationProfile
import views
import auth_urls

def resend_activation(target):
  def wrapper(request,*args,**kwargs):
    data = request.POST or request.GET
    model = get_user_model()
    if data.get('username',None):
      try:
        if hasattr(model.objects,"keyword_search"):
          user = model.objects.keyword_search(data.get('username'),force_active=False)[0]
        else:
          user = model.objects.get(username=data.get("username"))
        if not user.is_active and user.check_password(data.get("password","")[:200]):
          messages.error(request,"Your account is inactive. Please check your email (%s) for an activation link. If you no longer have access to this email address, please contact %s"%(user.email,settings.MEMBERSHIP_EMAIL))
          if Site._meta.installed:
            site = Site.objects.get_current()
          else:
            site = RequestSite(request)
          RegistrationProfile.objects.create(user=user).send_activation_email(site)
          return HttpResponseRedirect(request.path)
      except (model.DoesNotExist,IndexError):
        pass
    return target(request,*args,**kwargs)
  return wrapper

urlpatterns = [
  url(r'^activate/(\w+)/$',views.activate,name='registration_activate'),
  url(r'^register/$',views.register,name='registration_register'),
  url(r'^register/complete/$',
      TemplateView.as_view(template_name='registration/registration_complete.html'),
      name='registration_complete'),
  url(r'^register/closed/$',
      TemplateView.as_view(template_name='registration/registration_closed.html'),
      name='registration_disallowed'),
  url(r'^login/$',resend_activation(auth_urls.auth_views.login),name="login"),
  url(r'', include(auth_urls)),
]
