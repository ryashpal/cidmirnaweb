#!/bin/bash
ps aux | grep gunicorn | grep cidmirnaweb | awk '{ print $2 }' | xargs kill -HUP

