#! /usr/bin/env python3

""" For deployment on ix under CGI """

import site
site.addsitedir("/home/users/hedong/public_html/cis322/htbin/proj3-ajax/env/lib/python3.4/site-packages")

import cgitb
cgitb.enable()

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)