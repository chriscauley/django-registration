from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite
from django import forms
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _

from .models import RegistrationProfile

#! need to test settings
# view https://docs.djangoproject.com/en/1.6/topics/testing/tools/#overriding-settings
EXTRA_FIELDS = getattr(settings,"REGISTRATION_EXTRA_FIELDS",['password2'])

class RegistrationForm(forms.Form):
    """
    A form to create inactive users and create a registration profile. Uses the following settings:

    REGISTRATION_EXTRA_FIELDS - a list with 'pasword2' and/or 'tos'

    REGISTRATION_UNIQUE_EMAIL - if True, clean_email will validate whether or not a users email is unique

    REGISTRATION_NO_FREE_EMAIL - if True, clean email will reject emails using free email services

    REGISTRATION_IGNORE_DOTS - if True, clean email with detect a.b.c@gmail.com as being the same as abc@gmail.com
    """
    required_css_class = 'required'
    _e = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")}
    username = forms.RegexField(regex=r'^[\w.@+-]+$',max_length=30,label=_("Username"),error_messages=_e)
    email = forms.EmailField(label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput,label=_("Password"))
    if 'password2' in EXTRA_FIELDS: #! needs test
        password2 = forms.CharField(widget=forms.PasswordInput,label=_("Password (again)"))
    if 'tos' in EXTRA_FIELDS: #! needs test
        tos = forms.BooleanField(widget=forms.CheckboxInput,
                                 label=_(u'I have read and agree to the Terms of Service'),
                                 error_messages={'required': _("You must agree to the terms to register")})

    def __init__(self,request,*args,**kwargs):
        if not isinstance(request,HttpRequest):
            raise ValueError("The RegistrationForm must take a request as it's first argument")
        self.request = request
        return super(RegistrationForm,self).__init__(*args,**kwargs)

    def clean_email(self):
        User = get_user_model()
        e = _("This email address is already in use. Please supply a different email address.")
        if getattr(settings,"REGISTRATION_UNIQUE_EMAIL",False): #! needs test
            if User.objects.filter(email__iexact=self.cleaned_data['email']):
                raise forms.ValidationError(e)

        if getattr(settings,"REGISTRATION_IGNORE_DOTS",False): #! needs test
            name,domain = self.cleaned_data['email'].split('@')
            name = name.lower().replace('.','')
            for user in User.objects.filter(email__iendswith=domain):
                if name == user.email.split('@')[0].lower().replace('.',''):                 
                    raise forms.ValidationError(e)

        if getattr(settings,"REGISTRATION_NO_FREE_EMAIL",False): #! needs test
            bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
                           'googlemail.com', 'hotmail.com', 'hushmail.com',
                           'msn.com', 'mail.ru', 'mailinator.com', 'live.com',
                           'yahoo.com']
            email_domain = self.cleaned_data['email'].split('@')[1]
            e = _("Registration using free email addresses is prohibited. Please supply a different email address.")
            if email_domain in bad_domains:
                raise forms.ValidationError(e)

        return self.cleaned_data['email']

    def clean_username(self):
        User = get_user_model()
        if User.objects.filter(username__iexact=self.cleaned_data['username']):
            raise forms.ValidationError(_("A user with that username already exists."))
        return self.cleaned_data['username']

    def clean_password2(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data.get('password2','')

    def save(self):
        d = self.cleaned_data
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        RegistrationProfile.objects.create_inactive_user(d['username'],d['email'],d['password1'],site)
