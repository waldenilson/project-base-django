# encoding: utf-8
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader,Context
from project.core.models import AuthUserGroups, AuthGroupPermissions
import datetime, os
import settings as configuracao
import smtplib, ConfigParser
from xhtml2pdf import pisa
from os.path import abspath, join, dirname
from decouple import config

def ws(requisicao):
    if requisicao.GET.get('key', False):
        key = requisicao.GET['key']
        if key == 'chave':
            return 'ok'
        else:
            return '02' 
    else:
        return '01'

def verificar_permissao_grupo(usuario, grupos):
    if usuario:
        permissao = False
        obj_usuarios = AuthUserGroups.objects.filter( user = usuario.id )
        for obj in obj_usuarios:
            for obj_g in grupos:
                if obj.user.id == usuario.id and obj.group.name == str(obj_g):
                    permissao = True
        return permissao
    return False

def verificar_permissoes(grupo, permissoes):
    if grupo:
        permissao = False
        obj_grupos = AuthGroupPermissions.objects.filter( group = grupo.id )
        for obj in obj_grupos:
            for obj_g in permissoes:
                if obj.group.id == grupo.id and obj.permission.id == obj_g.id:
                    permissao = True
        return permissao
    return False

def relatorio_ods_base_header( nome_planilha, titulo_planilha, total_registro, ods):
    # sheet title
    sheet = ods.content.getSheet(0)
    sheet.setSheetName( nome_planilha )
    
    # title
    sheet.getCell(0, 0).setAlignHorizontal('center').stringValue( titulo_planilha ).setFontSize('14pt').setBold(True).setCellColor("#79bbff")
    sheet.getRow(0).setHeight('18pt')
    sheet.getColumn(0).setWidth('10cm')
    
    data_geracao = datetime.datetime.now()
    data_extenso = str(data_geracao.day)+' de '+mes_do_ano_texto(data_geracao.month)+" de "+str(data_geracao.year) 
        
    sheet.getCell(0,1).setAlignHorizontal('center').stringValue( 'Data: ' ).setFontSize('12pt').setBold(True)
    sheet.getCell(1,1).stringValue( str( data_extenso ) ).setFontSize('10pt')

    sheet.getCell(0,2).setAlignHorizontal('center').stringValue( 'Total: ' ).setFontSize('12pt').setBold(True)
    sheet.getCell(1,2).stringValue( str(total_registro) ).setFontSize('10pt')
                
    ods.content.mergeCells(0,0,7,1)
    ods.content.mergeCells(1,1,2,1)
    ods.content.mergeCells(1,2,2,1)
    
    return sheet

def relatorio_ods_base(ods, titulo):
    # generating response
    response = HttpResponse(mimetype=ods.mimetype.toString())
    response['Content-Disposition'] = 'attachment; filename='+str(titulo)+'".ods"'
    ods.save(response)    
    return response

def mes_do_ano_texto(inteiro):
    mes_texto = ""
    
    if inteiro == 1: mes_texto = "Janeiro"
    elif inteiro == 2: mes_texto = "Fevereiro"
    elif inteiro == 3: mes_texto = "Marco"
    elif inteiro == 4: mes_texto = "Abril"
    elif inteiro == 5: mes_texto = "Maio"
    elif inteiro == 6: mes_texto = "Junho"
    elif inteiro == 7: mes_texto = "Julho"
    elif inteiro == 8: mes_texto = "Agosto"
    elif inteiro == 9: mes_texto = "Setembro"
    elif inteiro == 10: mes_texto = "Outubro"
    elif inteiro == 11: mes_texto = "Novembro"
    elif inteiro == 12: mes_texto = "Dezembro"
    
    return mes_texto

def formatDataToText( formato_data ):
    if formato_data:
        if len(str(formato_data.day)) < 2:
            dtaberturaprocesso = '0'+str(formato_data.day)+"/"
        else:
            dtaberturaprocesso = str(formato_data.day)+"/"
        if len(str(formato_data.month)) < 2:
            dtaberturaprocesso += '0'+str(formato_data.month)+"/"
        else:
            dtaberturaprocesso += str(formato_data.month)+"/"
        dtaberturaprocesso += str(formato_data.year)
        return str( dtaberturaprocesso )
    else:
        return "";

def gerar_pdf(request, template_path, data, name):
    t = loader.get_template(template_path)
    c = Context(data)
    html =  t.render(c)
    file = open(os.path.join(configuracao.MEDIA_ROOT+'/tmp', name), "w+b")
    pisaStatus = pisa.CreatePDF(html, dest=file)
    file.seek(0)
    pdf = file.read()
    file.close()            # Don't forget to close the file handle
    return HttpResponse(pdf, mimetype='application/pdf')

def link_callback(uri, rel):
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                    'media URI must start with %s or %s' % \
                    (sUrl, mUrl))
    return path

def send_smtp(to, user, pwd, smtp, assunto, msg):
    try:
        smtpserver = smtplib.SMTP_SSL(smtp)
        smtpserver.login(user, pwd)
        header = 'To:' + to + '\n' + 'From: ' + user + '\n' + 'Subject:'+assunto+' \n'
        msg = header + msg
        smtpserver.sendmail(gmail_user, to, msg)
        smtpserver.close()
        return True
    except:
        return False

def translate(section, key):
    file_ini = ConfigParser.ConfigParser()
    file_ini.read( abspath(join(dirname(__file__), '../../../translation/'+config('TRANSLATION',default='default')+'.ini')) )
    print file_ini.get(section,key)