from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

urlpatterns = patterns(
  'registration.views',
  #url(r'^activate/complete/$','complete',name='registration_activation_complete'),
  url(r'^activate/(\w+)/$','activate',name='registration_activate'),
  url(r'^register/$','register',name='registration_register'),
  url(r'^register/complete/$',
      TemplateView.as_view(template_name='registration/registration_complete.html'),
      name='registration_complete'),
  url(r'^register/closed/$',
      TemplateView.as_view(template_name='registration/registration_closed.html'),
      name='registration_disallowed'),
  (r'', include('registration.auth_urls')),
)
