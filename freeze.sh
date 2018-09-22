#!/bin/bash
pip freeze -r requirements.txt > requirements_temp.txt
grep -v django-extensions requirements_temp.txt | grep -v "pkg-resources" | grep -v "nplusone" | grep -v "blinker" | grep -v "django-debug-toolbar" | grep -v "sqlparse" | grep -v "django-map-widget" | grep -v "add #egg=PackageName to the URL to avoid this warning" > requirements2.txt
cat requirements2.txt > requirements.txt

rm requirements2.txt
cat requirements_temp.txt > requirements_local.txt
rm requirements_temp.txt 
