# Create your views here.
from django.template.context import RequestContext
from django.shortcuts import render, render_to_response
import sys

def home(request):
    return render_to_response('core/web/index.html' ,{}, context_instance = RequestContext(request))

def page(request,name):
	print 'nome da pagina: '+name
	return render_to_response('core/index.html' ,{}, context_instance = RequestContext(request))
