from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

import views
import auth_urls

urlpatterns = [
  url(r'^activate/(\w+)/$',views.activate,name='registration_activate'),
  url(r'^register/$',views.register,name='registration_register'),
  url(r'^register/complete/$',
      TemplateView.as_view(template_name='registration/registration_complete.html'),
      name='registration_complete'),
  url(r'^register/closed/$',
      TemplateView.as_view(template_name='registration/registration_closed.html'),
      name='registration_disallowed'),
  url(r'', include(auth_urls)),
]
