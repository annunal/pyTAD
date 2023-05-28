import dash as dash
#import dash_core_components as dcc
from dash import Dash, dcc, html
#from dash import dcc
#import dash_html_components as html
from flask import Flask, redirect
import flask as flask
import urllib as urllib

from dash.dependencies import Input, Output, State

import socket,platform,os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','technip.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

appserver=app.server

app.config.suppress_callback_exceptions = True

import datetime

#def printLog(*a):
#  try:
#    fnameLog='logApp.txt'
#    f=open(fnameLog,'a')
#    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#    f.write(now+': '+  str(a)[1:][:-1] +'\n')
#    f.close()
#    print(*a)
#  except:
#    print(*a)






