1-	Configuração para colocar em produção sistema na hospedagem hostgator - Plano M

	Django 1.3.1
	Python 2.6.6
	fcgi

2- padrão do ambiente:

	site.com/
		project/
			core/
			odslib/
			reportlab/
			html5lib/
			xhtml2pdf/
			six.py
			decouple.py
		static/
		media/
		index.fcgi
		.htaccess
		.env

3-	observações
		reportlab==2.7
		xhtml2pdf==0.0.6