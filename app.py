# coding=utf-8
from flask import (Flask, render_template,
                   request, redirect, g, make_response)
import oursql


app = Flask(__name__)


def get_user_name():
    user_id = int(request.cookies['user_id'])
    g.cursor.execute('select login from user where id={}'.format(user_id))
    return g.cursor.fetchone()[0]


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
    g.cursor.execute("select link.id, title, descr, link, count"
                     " from link, user where link.user=user.id and user.login='{}'"
                     .format(name))
    return render_template(
        "links.html",
        name=name,
        links=g.cursor.fetchall(),
        editable=(name == get_user_name())
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
        return redirect("/links/{}".format(get_user_name()))
    return render_template("add.html")


@app.route('/redirect/<name>')
def redir(name):
    g.cursor.execute("select id from user where login='{}'".format(name))
    user_id = g.cursor.fetchone()[0]
    g.cursor.execute("update link set count=count+1"
                     " where link='{}' and user={}".format(
        request.args['url'],
        user_id
    ))
    return redirect(request.args['url'])


@app.route('/delete/<link_id>')
def delete(link_id):
    g.cursor.execute("delete from link where id={}".format(link_id))
    return redirect("/links/{}".format(get_user_name()))


if __name__ == '__main__':
    app.run(debug=True)
