# coding=utf-8
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def index():
    if request.method == "POST":
        print request.form['login']
        return redirect('/links')
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('registration.html')


@app.route('/links')
def links():
    return "Links"


app.run(debug=True)