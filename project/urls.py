# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf.urls.defaults import patterns, url, include
admin.autodiscover()

project = 'project'

handler404 = project+'.core.views_excecoes.pagina_nao_encontrada'
handler403 = project+'.core.views_excecoes.permissao_negada'
handler500 = project+'.core.views_excecoes.erro_servidor'

urlpatterns = patterns('',
    # Examples:

	#urls web
    url(r'^$', 'project.core.views.home', name='home'),
    url(r'^web/(?P<name>.*)/', 'project.core.views.page', name='page'),

    #urls webservice
    url(r'^ws/usuarios', 'project.core.ws.views.usuarios', name='usuarios'),

    #urls admin
    url(r'^grupo/consulta/', 'project.core.admin.grupo.consulta'),
    url(r'^grupo/cadastro/', 'project.core.admin.grupo.cadastro'),
    url(r'^grupo/edicao/(?P<id>\d+)/', 'project.core.admin.grupo.edicao'),
    
    url(r'^permissao/consulta/', 'project.core.admin.permissao.consulta'),
    url(r'^permissao/cadastro/', 'project.core.admin.permissao.cadastro'),
    url(r'^permissao/edicao/(?P<id>\d+)/', 'project.core.admin.permissao.edicao'),

    url(r'^usuario/consulta/', 'project.core.admin.usuario.consulta'),
    url(r'^usuario/cadastro/', 'project.core.admin.usuario.cadastro'),
    url(r'^usuario/edicao/(?P<id>\d+)/', 'project.core.admin.usuario.edicao'),
    url(r'^usuario/relatorio/ods/', 'project.core.admin.usuario.relatorio_ods'),
    url(r'^usuario/relatorio/pdf/', 'project.core.admin.usuario.relatorio_pdf'),

    # CONTROLE AUTENTICACAO
    url(r'^login/', 'django.contrib.auth.views.login', {"template_name":"core/index.html"}),
    url(r'^logout/', 'django.contrib.auth.views.logout_then_login', {"login_url":"/"}),
    url(r'^admin/', include(admin.site.urls)),
)
