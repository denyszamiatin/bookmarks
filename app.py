# coding=utf-8
import urllib
import hashlib
import random
import datetime
import re
from oursql import IntegrityError

import validators

from flask import (Flask, render_template,
                   request, redirect, g, make_response, abort)
import oursql


app = Flask(__name__)
app.jinja_env.autoescape = False


def _get_cursor():
    g.cursor.close()
    g.cursor = g.db.cursor()
    return g.cursor


def _get_user_id():
    session_id = request.cookies.get('id', '')
    # if not re.match('[0-9a-f]{128}', session_id):
    #     return 0
    cursor = _get_cursor()
    cursor.execute("select user, csrf_token from session where session_id='{}'"
                     " and expires > now()".format(session_id))
    user = cursor.fetchone()
    if user is not None:
        g.csrf_token = user[1]
    return int(user[0]) if user is not None else 0


def get_user_id():
    return g.user_id


def get_user_name():
    user_id = get_user_id()
    cursor = _get_cursor()
    cursor.execute('select login from user where id={}'.format(user_id))
    return cursor.fetchone()[0]


def check_passwd(passwd, hash_passwd):
    salt, pwd = hash_passwd[:64], hash_passwd[64:]
    return _make_passwd(salt, passwd) == hash_passwd


def _make_passwd(salt, passwd):
    h = hashlib.sha256(salt + passwd)
    return salt + h.hexdigest()


def make_passwd(passwd):
    r = hashlib.sha256(str(random.random()))
    return _make_passwd(r.hexdigest(), passwd)


@app.before_request
def before_request():
    g.db = oursql.connect(db='bookmarks', user='root', passwd='1')
    g.cursor = g.db.cursor()
    g.user_id = _get_user_id()


@app.teardown_request
def teardown_request(exc):
    g.cursor.close()
    g.db.close()


def login(resp, user_id):
    cursor = _get_cursor()
    cursor.execute("delete from session where user={}".format(user_id))
    cursor = _get_cursor()
    session_id = hashlib.sha512(str(random.random())).hexdigest()
    csrf_token = hashlib.sha512(str(random.random())).hexdigest()
    cursor.execute("insert into session (user, session_id, expires, csrf_token) "
                     "values ({}, '{}', '{}', '{}')".format(user_id, session_id,
                                                   str(datetime.datetime.now() +
                                                   datetime.timedelta(1)),
                                                   csrf_token))
    resp.set_cookie('id', session_id, httponly=True)


@app.route('/', methods=['get', 'post'])
def index():
    if request.method == "POST":
        if request.form['login'] and request.form['pwd']:

            cursor = _get_cursor()
            cursor.execute("select id, login, passwd from user where login=?",
                           (request.form['login'], )
            )
            user = cursor.fetchone()
            if user is not None:
                user_id, user_name, passwd = user
                if check_passwd(request.form['pwd'], passwd):
                    print "Ok"
                    resp = make_response(redirect('/links/{}'.format(user_name)))
                    login(resp, user_id)
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
            try:
                cursor = _get_cursor()
                cursor.execute(
                    "insert into user (login, email, passwd) values ('{}', '{}', '{}')"
                    .format(request.form['login'], request.form['email'],
                            make_passwd(request.form['pwd1']))
                )
            except IntegrityError:
                message = "Invalid registration"
            else:
                return redirect('/')
        else:
            message = "Invalid registration"
    return render_template('registration.html', message=message)


@app.route('/links/<name>')
def links(name):
    cursor = _get_cursor()
    cursor.execute("select link.id, title, descr, link, count"
                     " from link, user where link.user=user.id and user.login='{}'"
                     " order by id"
                     .format(name))
    return render_template(
        "links.html",
        name=name,
        links=cursor.fetchall(),
        editable=(name == get_user_name())
    )


@app.route('/add', methods=['get', 'post'])
def add():
    title = descr = link = ""
    if request.method == 'POST':
        title, descr, link = request.form['title'], request.form['descr'], request.form['link']
        if request.form.get('csrf_token', '') != g.csrf_token:
            abort(400)
        if title and descr and validators.url(link) is True:
            user_id = get_user_id()
            cursor = _get_cursor()
            cursor.execute("insert into link (user, title, descr, link)"
                             " values ({},'{}', '{}', '{}')".format(
                user_id,
                request.form['title'],
                request.form['descr'],
                request.form['link']
            ))
            return redirect("/links/{}".format(get_user_name()))
    return render_template("add.html", title=title, descr=descr, link=link,
                           csrf_token=g.csrf_token)


@app.route('/redirect/<name>/<link_id>')
def redir(name, link_id):
    cursor = _get_cursor()
    cursor.execute("select link.id, link.link from user, link where login='{}' "
                     "order by id limit {}, 1"
                     .format(name, link_id))
    link_id, url = cursor.fetchone()
    cursor = _get_cursor()
    cursor.execute("update link set count=count+1"
                     " where id='{}'".format(link_id))
    return render_template("warning.html", url=urllib.unquote(url))


@app.route('/delete/<link_id>')
def delete(link_id):
    user_id = get_user_id()
    cursor = _get_cursor()
    cursor.execute("select id from link where user={} limit {}, 1".format(
        user_id,
        link_id
    ))
    link_id = int(cursor.fetchone()[0])
    cursor = _get_cursor()
    cursor.execute("delete from link where id={}".format(link_id))
    return redirect("/links/{}".format(get_user_name()))


if __name__ == '__main__':
    app.run(debug=True)
