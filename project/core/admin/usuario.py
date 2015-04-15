from django.contrib.auth.decorators import login_required, user_passes_test,\
    permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template.context import RequestContext
from django.contrib import messages
from project.core.models import AuthUser, AuthGroup, AuthUserGroups
import datetime
import hashlib
import json
from collections import OrderedDict
from django.http import HttpResponse
from project.core.util.functions import relatorio_ods_base_header, relatorio_ods_base
from odslib import ODS
from project.core.util.functions import verificar_permissao_grupo

nome_relatorio      = "relatorio_usuario"
response_consulta  = "/usuario/consulta/"
titulo_relatorio    = "Relatorio Usuarios"
planilha_relatorio  = "Usuarios"


@permission_required('controle_usuario', login_url='/excecoes/permissao_negada/')
def consulta(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        email = request.POST['email']
        lista = AuthUser.objects.all().filter( first_name__icontains=first_name, email__icontains=email )
    else:
        lista = AuthUser.objects.all()

    lista = lista.order_by( 'username' )
    #gravando na sessao o resultado da consulta preparando para o relatorio/pdf
    request.session['relatorio_usuario'] = lista
    return render_to_response('core/admin/usuario/consulta.html' ,{'lista':lista,'request':request}, context_instance = RequestContext(request))

@permission_required('controle_usuario', login_url='/excecoes/permissao_negada/')
def cadastro(request):
    
    grupo = AuthGroup.objects.all().order_by('name')
    
    result = {}
    for obj in grupo:
        result.setdefault(obj.name, False)
    result = sorted(result.items())

    
    ativo = False
    if request.POST.get('is_active',False):
        ativo = True
    
    if request.method == "POST":
        if validacao(request, 'cadastro'):            
            usuario = AuthUser(
                                   password = hashlib.md5(request.POST['password']).hexdigest,
                                   first_name = request.POST['first_name'],
                                   last_name = request.POST['last_name'],
                                   email = request.POST['email'],
                                   username = request.POST['username'],
                                   is_superuser = False,
                                   is_staff = True,
                                   is_active = ativo,
                                   last_login = datetime.datetime.now(),
                                   date_joined = datetime.datetime.now()
                                   )
            usuario.save()
            
            for obj in grupo:
                if request.POST.get(obj.name, False):
                    #verificar se esse grupo ja esta ligado ao usuario
                        # inserir ao authusergroups
                    ug = AuthUserGroups( user = AuthUser.objects.get( pk = usuario.id ),
                                          group = AuthGroup.objects.get( pk = obj.id ) )
                    ug.save()
            
            return HttpResponseRedirect("/usuario/consulta/") 
    
    return render_to_response('core/admin/usuario/cadastro.html',{'result':result,'grupo':grupo}, context_instance = RequestContext(request))


@permission_required('controle_usuario', login_url='/excecoes/permissao_negada/')
def edicao(request, id):
    
    grupo = AuthGroup.objects.all().order_by('name')
    userGrupo = AuthUserGroups.objects.all().filter( user = id )
    
    result = {}
    for obj in grupo:
        achou = False
        for obj2 in userGrupo:
            if obj.id == obj2.group.id:
                result.setdefault(obj.name,True)
                achou = True
                break
        if not achou:
            result.setdefault(obj.name, False)
    result = sorted(result.items())
            
    user_obj = get_object_or_404(AuthUser, id=id)

    if request.method == "POST":
        
#        if not request.user.has_perm('usuario_edicao'):
#            return HttpResponseRedirect('/excecoes/permissao_negada/') 

        # verificando os grupos do usuario
        for obj in grupo:
            if request.POST.get(obj.name, False):
                #verificar se esse grupo ja esta ligado ao usuario
                res = AuthUserGroups.objects.all().filter( user = id, group = obj.id )
                if not res:
                    # inserir ao authusergroups
                    ug = AuthUserGroups( user = AuthUser.objects.get( pk = id ),
                                          group = AuthGroup.objects.get( pk = obj.id ) )
                    ug.save()
                    #print obj.name + ' nao esta ligado a este usuario'
            else:
                #verificar se esse grupo foi desligado do usuario
                res = AuthUserGroups.objects.all().filter( user = id, group = obj.id )
                if res:
                    # excluir do authusergroups
                    for aug in res:
                        aug.delete()
                    #print obj.name + ' desmarcou deste usuario'
                    
        if validacao(request, 'edicao'):
            
            ativo = False
            if request.POST.get('is_active',False):
                ativo = True
            
            # tratar o campo senha
            senha_digitada = request.POST['password']
            senha_atual = user_obj.password
            if len(senha_digitada) > 2:
                senha_atual = hashlib.md5( senha_digitada ).hexdigest()
            
            usuario = AuthUser(
                                   id = user_obj.id,
                                   password = senha_atual,
                                   first_name = request.POST['first_name'],
                                   last_name = request.POST['last_name'],
                                   email = request.POST['email'],
                                   username = request.POST['username'],
                                   is_superuser = user_obj.is_superuser,
                                   is_staff = user_obj.is_staff,
                                   is_active = ativo,
                                   last_login = user_obj.last_login,
                                   date_joined = user_obj.date_joined
                                   )
            usuario.save()
            return HttpResponseRedirect("/usuario/consulta/")
    
    return render_to_response('core/admin/usuario/edicao.html', 
                              {'result':result,'grupo':grupo,'usergrupo':userGrupo,'user_obj':user_obj}, context_instance = RequestContext(request))


@login_required
def edicao_usuario_logado(request, id):
    
    if str(request.user.id) == str(id):
    
        grupo = AuthGroup.objects.all()
        #servidor = Tbservidor.objects.all()
        userGrupo = AuthUserGroups.objects.all().filter( user = id )
        
        result = {}
        for obj in grupo:
            achou = False
            for obj2 in userGrupo:
                if obj.id == obj2.group.id:
                    result.setdefault(obj.name,True)
                    achou = True
                    break
            if not achou:
                result.setdefault(obj.name, False)
        result = sorted(result.items())
        
        ativo = False
        if request.POST.get('is_active',False):
            ativo = True
            
        user_obj = get_object_or_404(AuthUser, id=id)
    
        if request.method == "POST":
            
            if request.user.has_perm('usuario_grupo_edicao'):
                # verificando os grupos do usuario
                for obj in grupo:
                    if request.POST.get(obj.name, False):
                        #verificar se esse grupo ja esta ligado ao usuario
                        res = AuthUserGroups.objects.all().filter( user = id, group = obj.id )
                        if not res:
                            # inserir ao authusergroups
                            ug = AuthUserGroups( user = AuthUser.objects.get( pk = id ),
                                                  group = AuthGroup.objects.get( pk = obj.id ) )
                            ug.save()
                            #print obj.name + ' nao esta ligado a este usuario'
                    else:
                        #verificar se esse grupo foi desligado do usuario
                        res = AuthUserGroups.objects.all().filter( user = id, group = obj.id )
                        if res:
                            # excluir do authusergroups
                            for aug in res:
                                aug.delete()
                            #print obj.name + ' desmarcou deste usuario'
                        
            if validacao(request, 'edicao'):
                
                # tratar o campo senha
                senha_digitada = request.POST['password']
                senha_atual = user_obj.password
                if len(senha_digitada) > 2:
                    senha_atual = hashlib.md5( senha_digitada ).hexdigest()
                
                usuario = AuthUser(
                                       id = user_obj.id,
                                       password = senha_atual,
                                       first_name = request.POST['first_name'],
                                       last_name = request.POST['last_name'],
                                       email = request.POST['email'],
                                       username = request.POST['username'],
                                       is_superuser = user_obj.is_superuser,
                                       is_staff = user_obj.is_staff,
                                       is_active = ativo,
                                       last_login = user_obj.last_login,
                                       date_joined = user_obj.date_joined
                                       )
                usuario.save()
                return HttpResponseRedirect("/usuario/edicao/usuario/"+str(id)+"/")
        
        return render_to_response('core/admin/usuario/edicao.html', 
                                  {'result':result,'grupo':grupo,'usergrupo':userGrupo,'user_obj':user_obj}, context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect("/usuario/edicao/"+str(id)+"/")


@permission_required('controle_usuario', login_url='/excecoes/permissao_negada/')
def relatorio_ods(request):

    global nome_relatorio
    # montar objeto lista com os campos a mostrar no relatorio/pdf
    lista = request.session[nome_relatorio]
    
    #GERACAO
    nome_rel = "relatorio-encomendas"
    titulo_relatorio    = "RELATORIO DE USUARIOS"
    planilha_relatorio  = "Usuarios"
    ods = ODS()
    sheet = relatorio_ods_base_header(planilha_relatorio, titulo_relatorio, len(lista), ods)
        
    # TITULOS DAS COLUNAS
    sheet.getCell(0, 6).setAlignHorizontal('center').stringValue( 'Nome' ).setFontSize('14pt').setBold(True).setCellColor("#ccff99")
    sheet.getCell(1, 6).setAlignHorizontal('center').stringValue( 'Email' ).setFontSize('14pt').setBold(True).setCellColor("#ccff99")
    sheet.getRow(1).setHeight('20pt')
    sheet.getRow(2).setHeight('20pt')
    sheet.getRow(6).setHeight('20pt')
        
    sheet.getColumn(0).setWidth("1in")
    sheet.getColumn(1).setWidth("2.5in")

    #DADOS DA CONSULTA
    x = 5
    for obj in lista:
        sheet.getCell(0, x+2).setAlignHorizontal('center').stringValue(obj.username)
        sheet.getCell(1, x+2).setAlignHorizontal('center').stringValue(obj.email)
        x += 1

    relatorio_ods_base(ods, planilha_relatorio)
    # generating response
    response = HttpResponse(mimetype=ods.mimetype.toString())
    response['Content-Disposition'] = 'attachment; filename='+nome_rel+'.ods'
    ods.save(response)
    
    return response


def validacao(request_form, acao):
    warning = True
    if request_form.POST['first_name'] == '':
        messages.add_message(request_form,messages.WARNING,'Informe o Nome')
        warning = False
    if request_form.POST['last_name'] == '':
        messages.add_message(request_form,messages.WARNING,'Informe o Sobrenome')
        warning = False
    if request_form.POST['username'] == '':
        messages.add_message(request_form,messages.WARNING,'Informe o Login')
        warning = False
    
#    result = AuthUser.objects.filter( username = request_form.POST['username'], id = request_form.user.id )
#    if result:
#        messages.add_message(request_form,messages.WARNING,'Login usado por outro usuario. Informe um login diferente.')
#        warning = False
    
#    result = AuthUser.objects.filter( first_name = request_form.POST['first_name'], id = request_form.user.id )
#    if result:
#        messages.add_message(request_form,messages.WARNING,'Nome usado por outro usuario. Informe um nome diferente.')
#        warning = False
    
    if acao == 'cadastro':
        if request_form.POST['password'] == '':
            messages.add_message(request_form,messages.WARNING,'Informe a Senha')
            warning = False
        warning = False
    return warning
