from django.contrib.auth.decorators import login_required, permission_required,\
    user_passes_test
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from project.core.models import AuthGroup, AuthPermission,\
    AuthGroupPermissions, AuthUser, DjangoContentType
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from project.core.util.functions import verificar_permissao_grupo
from project.core.util.functions import relatorio_ods_base_header, relatorio_ods_base
from odslib import ODS

nome_relatorio      = "relatorio_grupo"
response_consulta  = "/grupo/consulta/"
titulo_relatorio    = "Relatorio Grupos"
planilha_relatorio  = "Grupos"


@permission_required('grupo_consulta', login_url='/excecoes/permissao_negada/')
def consulta(request):
    if request.method == "POST":
        nome = request.POST['name']
        lista = AuthGroup.objects.all().filter( name__icontains=nome )
    else:
        lista = AuthGroup.objects.all()
    lista = lista.order_by( 'name' )
    #gravando na sessao o resultado da consulta preparando para o relatorio/pdf
    request.session['relatorio_grupo'] = lista
    return render_to_response('core/admin/grupo/consulta.html' ,{'lista':lista}, context_instance = RequestContext(request))

@permission_required('grupo_cadastro', login_url='/excecoes/permissao_negada/')
def cadastro(request):
    if request.method == "POST":
        next = request.GET.get('next', '/')    
        if validacao(request):
            f_grupo = AuthGroup(
                                        name = request.POST['nome']
                                      )
            f_grupo.save()
            if next == "/":
                return HttpResponseRedirect("/grupo/consulta/")
            else:    
                return HttpResponseRedirect( next ) 
    return render_to_response('core/admin/grupo/cadastro.html',{}, context_instance = RequestContext(request))
    
@permission_required('grupo_consulta', login_url='/excecoes/permissao_negada/')
def edicao(request, id):

    permissao = AuthPermission.objects.all().order_by('content_type')
    grupoPermissao = AuthGroupPermissions.objects.all().filter( group = id )

    contenttype = DjangoContentType.objects.all().order_by('name')

    result = {}
    for obj in permissao:
        achou = False
        for obj2 in grupoPermissao:
            if obj.id == obj2.permission.id:
                result.setdefault(obj, True)
                achou = True
                break
        if not achou:
            result.setdefault(obj, False)
    result = sorted(result.items())
    
    instance = get_object_or_404(AuthGroup, id=id)
    if request.method == "POST":
        
        if not request.user.has_perm('grupo_edicao'):
            return HttpResponseRedirect('/excecoes/permissao_negada/') 


        # verificando os grupos do usuario
        for obj in permissao:
            if request.POST.get(obj.name, False):
                #verificar se esse grupo ja esta ligado ao usuario
                res = AuthGroupPermissions.objects.all().filter( group = id, permission = obj.id )
                if not res:
                    # inserir ao authusergroups
                    ug = AuthGroupPermissions( group = AuthGroup.objects.get( pk = id ),
                                          permission = AuthPermission.objects.get( pk = obj.id ) )
                    ug.save()
                    #print obj.name + ' nao esta ligado a este usuario'
            else:
                #verificar se esse grupo foi desligado do usuario
                res = AuthGroupPermissions.objects.all().filter( group = id, permission = obj.id )
                if res:
                    # excluir do authusergroups
                    for aug in res:
                        aug.delete()
                    #print obj.name + ' desmarcou deste usuario'        
        
        if validacao(request):
            f_grupo = AuthGroup(
                                        id = instance.id,
                                        name = request.POST['nome']
                                      )
            f_grupo.save()
            return HttpResponseRedirect("/grupo/edicao/"+str(id)+"/")
    return render_to_response('core/admin/grupo/edicao.html', {'content':contenttype,"grupo":instance,'result':result,'permissao':permissao,'grupopermissao':grupoPermissao}, context_instance = RequestContext(request))

@permission_required('grupo_consulta', login_url='/excecoes/permissao_negada/')
def relatorio_ods(request):

    # montar objeto lista com os campos a mostrar no relatorio/pdf
    lista = request.session[nome_relatorio]
    
    if lista:
        ods = ODS()
        sheet = relatorio_ods_base_header(planilha_relatorio, titulo_relatorio, ods)
        
        # subtitle
        sheet.getCell(0, 1).setAlignHorizontal('center').stringValue( 'Nome' ).setFontSize('14pt')
        sheet.getRow(1).setHeight('20pt')
        
    #TRECHO PERSONALIZADO DE CADA CONSULTA
        #DADOS
        x = 0
        for obj in lista:
            sheet.getCell(0, x+2).setAlignHorizontal('center').stringValue(obj.name)
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
        messages.add_message(request_form,messages.WARNING,'Informe o nome do grupo')
        warning = False
    return warning
