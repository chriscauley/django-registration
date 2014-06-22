from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from .forms import RegistrationForm
from .models import RegistrationProfile
from db.utils import get_or_none

def register(request,form=RegistrationForm):
    form = form(request,request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('registration_complete'))
    values = { 'form': form }
    return TemplateResponse(request,'registration/registration_form.html',values)

def activate(request,activation_key):
    profile, activated = RegistrationProfile.objects.get_and_activate(activation_key)
    if activated: # success! login
        user = profile.user
        user.backend='django.contrib.auth.backends.ModelBackend'
        login(request,user)
    values = {
        'profile': profile,
        'activated': activated,
    }
    return TemplateResponse(request,'registration/activate.html',values)
