# coding=utf-8
from flask import (Flask, render_template,
                   request, redirect, g, make_response)
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
                resp = make_response(redirect('/links/{}'.format(user_name)))
                resp.set_cookie('user_id', str(user_id))
                return resp
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
    user_id = int(request.cookies['user_id'])
    g.cursor.execute("select id, title, descr, link, count"
                     " from link where user={}".format(user_id))
    return render_template(
        "links.html",
        name=name,
        links=g.cursor.fetchall()
    )


@app.route('/add', methods=['get', 'post'])
def add():
    if request.method == 'POST':
        user_id = int(request.cookies['user_id'])
        g.cursor.execute("insert into link (user, title, descr, link)"
                         " values ({},'{}', '{}', '{}')".format(
            user_id,
            request.form['title'],
            request.form['descr'],
            request.form['link']
        ))
        g.cursor.execute('select login from user where id={}'.format(user_id))
        user_name = g.cursor.fetchone()[0]
        return redirect("/links/{}".format(user_name))
    return render_template("add.html")


if __name__ == '__main__':
    app.run(debug=True)
