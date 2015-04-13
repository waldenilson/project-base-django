from django.contrib.auth.decorators import login_required, permission_required,\
    user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext, Context
from project.core.models import AuthUser, AuthPermission, DjangoContentType
from django.http import HttpResponseRedirect
from django.contrib import messages
from project.core.util.functions import relatorio_ods_base_header, relatorio_ods_base
from project.core.util.functions import verificar_permissao_grupo
from django.http import HttpResponse
from odslib import ODS
from project import settings
from django import conf
import os
from django.template.defaultfilters import join
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.files.base import File
import django
from django.core.files import storage
from django.db.models import  Q

nome_relatorio      = "relatorio_permissao"
response_consulta  = "/permissao/consulta/"
titulo_relatorio    = "Relatorio Permissoes"
planilha_relatorio  = "Permissoes"

@permission_required('sicop.permissao_consulta', login_url='/excecoes/permissao_negada/')
def consulta(request):
    lista = AuthPermission.objects.all()
    if request.method == "POST":
        nome = request.POST['nome']
        lista = AuthPermission.objects.filter( name__icontains=nome )
        lista = lista.order_by( 'name' )
    
#gravando na sessao o resultado da consulta preparando para o relatorio/pdf
    request.session[nome_relatorio] = lista
    return render_to_response('core/admin/permissao/consulta.html' ,{'lista':lista}, context_instance = RequestContext(request))

@permission_required('permissao_cadastro', login_url='/excecoes/permissao_negada/')
def cadastro(request):
    content = DjangoContentType.objects.all()#.filter( tbdivisao__id = AuthUser.objects.get( pk = request.user.id ).tbdivisao.id ).order_by('nmtipocaixa')
       
    if request.method == "POST":
        next = request.GET.get('next', '/')
        if validacao(request):
            f_permissao = AuthPermission(
                              name = request.POST['nome'],
                              codename = request.POST['codenome'],
                              content_type = DjangoContentType.objects.get(pk = request.POST['content'])
                              )
            f_permissao.save()
            if next == "/":
                return HttpResponseRedirect(response_consulta)
            else:    
                return HttpResponseRedirect(next)
    return render_to_response('core/admin/permissao/cadastro.html',{"content":content}, context_instance = RequestContext(request))

@permission_required('permissao_consulta', login_url='/excecoes/permissao_negada/')
def edicao(request, id):
    content = DjangoContentType.objects.all()#.filter( tbdivisao__id = AuthUser.objects.get( pk = request.user.id ).tbdivisao.id ).order_by('nmtipocaixa')
    instance = get_object_or_404(AuthPermission, id=id)
    if request.method == "POST":

        if not request.user.has_perm('sicop.permissao_edicao'):
            return HttpResponseRedirect('/excecoes/permissao_negada/') 

        if validacao(request):
            f_permissao = AuthPermission(
                              id = instance.id,
                              name = request.POST['nome'],
                              codename = request.POST['codenome'],
                              content_type = DjangoContentType.objects.get(pk = request.POST['content'])
                              )
            f_permissao.save()
 
        return HttpResponseRedirect("/permissao/edicao/"+str(id)+"/")
    
    return render_to_response('core/admin/permissao/edicao.html', {"permissao":instance,"content":content}, context_instance = RequestContext(request))


@permission_required('permissao_consulta', login_url='/excecoes/permissao_negada/')
def relatorio_ods(request):

    # montar objeto lista com os campos a mostrar no relatorio/pdf
    lista = request.session[nome_relatorio]
    
    if lista:
        ods = ODS()
        sheet = relatorio_ods_base_header(planilha_relatorio, titulo_relatorio, ods)
        
        # subtitle
        sheet.getCell(0, 1).setAlignHorizontal('center').stringValue( 'Nome' ).setFontSize('14pt')
        sheet.getCell(1, 1).setAlignHorizontal('center').stringValue( 'Tipo' ).setFontSize('14pt')
        sheet.getRow(1).setHeight('20pt')
        
    #TRECHO PERSONALIZADO DE CADA CONSULTA
        #DADOS
        x = 0
        for obj in lista:
            sheet.getCell(0, x+2).setAlignHorizontal('center').stringValue(obj.nmlocalarquivo)
            sheet.getCell(1, x+2).setAlignHorizontal('center').stringValue(obj.tbtipocaixa.nmtipocaixa)    
            x += 1
        
    #TRECHO PERSONALIZADO DE CADA CONSULTA     
       
        relatorio_ods_base(ods, planilha_relatorio)
        # generating response
        response = HttpResponse(mimetype=ods.mimetype.toString())
        response['Content-Disposition'] = 'attachment; filename='+nome_relatorio+'.ods'
        ods.save(response)
    
        return response
    else:
        return HttpResponseRedirect( response_consulta )

def validacao(request_form):
    warning = True
    if request_form.POST['nome'] == '':
        messages.add_message(request_form,messages.WARNING,'Informe um nome para a permissao')
        warning = False
    if request_form.POST['codenome'] == '':
        messages.add_message(request_form,messages.WARNING,'Informe um codenome para a permissao')
        warning = False
    return warning
