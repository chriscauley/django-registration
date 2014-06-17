from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from .forms import RegistrationForm
from .models import RegistrationProfile

def register(request,form=RegistrationForm):
    form = form(request,request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('registration_complete'))
    values = { 'form': form }
    return TemplateResponse(request,'registration/registration_form.html',values)

def activate(request,activation_key):
    new_user = RegistrationProfile.objects.activate_user(activation_key)
    if new_user: # success! login
        new_user.backend='django.contrib.auth.backends.ModelBackend'
        login(request,new_user)
    values = {
        'new_user': new_user,
    }
    return TemplateResponse(request,'registration/activate.html',values)
    
