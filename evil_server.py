# coding=utf-8
from flask import Flask, request

app = Flask(__name__)

app.config.update(SERVER_NAME='localhost:5002')


@app.route('/')
def index1():
    print request.args['q']
    return ''

app.run(debug=True)