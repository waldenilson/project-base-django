1-	Configuração para colocar em produção sistema em servidor/PC linux/Debian-Ubuntu
	
	1.1-	Para projetos na versão Django 1.5.1
		Utilizar arquivo httpd_1_5_1.conf, substituindo o httpd.conf do apache2.
		Adição e substituição do arquivo wsgi_django_1_5_1.py para wsgi.py.

	1.2-	Para projetos na versão Django 1.3.1
		Utilizar arquivo httpd_1_3_1.conf, substituindo o httpd.conf do apache2.
		Adição e substituição do arquivo wsgi_django_1_3_1.py para wsgi.py.

	Obs1.: Substituir os caminhos dos projetos dentro do(s) arquivo(s).
	Obs2.: Apache2 com mod_wsgi instalado.
