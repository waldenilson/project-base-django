# Create your views here.
from django.template.context import RequestContext
from django.shortcuts import render, render_to_response
import sys

def pagina_nao_encontrada(request):
    return render(request, "core/excecao/pagina_nao_encontrada.html")

def permissao_negada(request):
    return render(request, "core/excecao/permissao_negada.html")

def erro_servidor(request):
    
    #t = loader.get_template(template_name) # You need to create a 500.html template.
    ltype,lvalue,ltraceback = sys.exc_info()
    sys.exc_clear() #for fun, and to point out I only -think- this hasn't happened at 
                    #this point in the process already

    return render_to_response('core/excecao/erro_servidor.html' ,{'type':ltype,'value':lvalue}, context_instance = RequestContext(request))

