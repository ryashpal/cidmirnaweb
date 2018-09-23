#!/bin/bash
gunicorn --workers 2 --bind unix:/tmp/cidmirnaweb.sock cidmirnaweb.wsgi --daemon --log-file logs/gunicorn_proper_log_$(date -Idate).txt >> logs/gunicorn_out.txt 2>> logs/gunicorn_err.txt
