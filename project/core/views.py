# Create your views here.
from django.template.context import RequestContext
from django.shortcuts import render, render_to_response
import sys

def home(request):
    return render_to_response('core/index.html' ,{}, context_instance = RequestContext(request))

def creditos(request):
    return render_to_response('core/web/creditos.html' ,{}, context_instance = RequestContext(request))
