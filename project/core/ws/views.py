# Create your views here.
# coding: utf-8
from django.template.context import RequestContext
from django.shortcuts import render, render_to_response
from django.core import serializers
from project.core.util.functions import ws
from project.core.models import AuthUser
import sys

def usuarios(request):
	retorno = ws(request)
	if retorno == 'ok':
		objs = AuthUser.objects.all()
		if objs:
			retorno = serializers.serialize('json', objs)
		else:
			retorno = '03'
	return render_to_response('core/base/webservice.html' ,{"retorno":retorno}, context_instance = RequestContext(request))
