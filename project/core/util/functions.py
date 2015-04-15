# encoding: utf-8

from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponse
from project.core.models import AuthUserGroups, AuthGroupPermissions
import datetime

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
    sheet.getCell(0, 0).setAlignHorizontal('center').stringValue( titulo_planilha ).setFontSize('20pt').setBold(True).setCellColor("#ccff99")
    sheet.getRow(0).setHeight('25pt')
    sheet.getColumn(0).setWidth('10cm')
    
    data_geracao = datetime.datetime.now()
    data_extenso = str(data_geracao.day)+' de '+mes_do_ano_texto(data_geracao.month)+" de "+str(data_geracao.year) 
        
    sheet.getCell(0,1).setAlignHorizontal('center').stringValue( 'Data: ' ).setFontSize('16pt').setBold(True)
    sheet.getCell(1,1).stringValue( str( data_extenso ) ).setFontSize('14pt')

    sheet.getCell(0,2).setAlignHorizontal('center').stringValue( 'Total: ' ).setFontSize('16pt').setBold(True)
    sheet.getCell(1,2).stringValue( str(total_registro) ).setFontSize('14pt')
                
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
