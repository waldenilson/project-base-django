#!/usr/bin/python
import sys, os

# Add a custom Python path. (optional)
sys.path.insert(0, "YOUR_HOME")

sys.path.insert(1,'YOUR_HOME/public_html/sistema/SISTEMA/project')

# Switch to the directory of your project.
os.chdir("YOUR_HOME/public_html/sistema/SISTEMA/project")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "project.settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
