# encoding: utf-8

from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.http import HttpResponseRedirect
from django.contrib.sites.models import get_current_site
from project import settings
from decouple import config

def login_form(request):
    
        # if the top login form has been posted
        if request.method == 'POST' and 'is_top_login_form' in request.POST:

            # validate the form
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():

                login(request, form.get_user())

                # if this is the logout page, then redirect to /
                # so we don't get logged out just after logging in
                if '/account/logout/' in request.get_full_path():
                    return HttpResponseRedirect('/')

        else:
            form = AuthenticationForm(request)    
    
        return {'login_form': form}

def init(request):
    return {
                'LINK':settings.STATIC_LINK,
                'STATIC_URL':config('STATIC_URL',default='/static/'),
                'REDIRECT_LOGIN':config('REDIRECT_LOGIN',default='/'),
                'THEME':config('THEME_DEFAULT',default='default'),
                'NOME_PROJETO':config('NOME_PROJETO',default='NOME DO PROJETO'),
                'VERSAO_PROJETO':config('VERSAO_PROJETO',default='VERSAO DO PROJETO'),
                'ANO_PROJETO':config('ANO_PROJETO',default='ANO DO PROJETO')
            }
