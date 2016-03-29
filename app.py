# coding=utf-8
from flask import Flask, render_template, request, redirect, g
import oursql


app = Flask(__name__)


@app.before_request
def before_request():
    g.db = oursql.connect(db='bookmarks', user='root', passwd='1')
    g.cursor = g.db.cursor()


@app.teardown_request
def teardown_request(exc):
    g.cursor.close()
    g.db.close()


@app.route('/', methods=['get', 'post'])
def index():
    if request.method == "POST":
        if request.form['login'] and request.form['pwd']:
            g.cursor.execute("select id, login from user where login='{}' "
                             "and passwd='{}'".format(
                request.form['login'],
                request.form['pwd']
            ))
            user = g.cursor.fetchone()
            if user is not None:
                user_id, user_name = user
            return redirect('/links/{}'.format(user_name))
    return render_template('index.html')


@app.route('/register', methods=['get', 'post'])
def register():
    message = ''
    if request.method == 'POST':
        if request.form['login'] and \
            request.form['email'] and \
            request.form['pwd1'] and \
            request.form['pwd1'] == request.form['pwd2']:
            g.cursor.execute(
                "insert into user (login, email, passwd) values ('{}', '{}', '{}')"
                .format(request.form['login'], request.form['email'], request.form['pwd1'])
            )
            return redirect('/')
        else:
            message = "Invalid registration"
    return render_template('registration.html', message=message)


@app.route('/links/<name>')
def links(name):
    return render_template("links.html", name=name)


if __name__ == '__main__':
    app.run(debug=True)
