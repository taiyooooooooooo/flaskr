import sqlite3
from flask import Flask,request,session,\
                  g,redirect,url_for,abort,render_template,flash
from contextlib import closing

#config
DATABASE = '/tmp/flask.db'
DEBUG = True
SECRET_KEY = 'develepment key'
USERNAME = 'admin'
PASSWORD = 'default'

#init
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

if __name__ == '__main__':
    app.run()

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(res):
    g.db.close
    return res

@app.route('/')
def show_entries():
    cur = g.db.execute('SELECT title,text FROM entries ORDER BY id DESC')
    entries = [dict(title = row[0],text = row[1])] for row in cur.fetchall()]
    return render_template('show_entries.html',entries = entries)

@app.route('/add',methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO entries (title,text) VALUES(?,?)',
                 [request.form[title],request.form['text']]
    g.db.commit()
    flash('New entries was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.methods == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You are logged in')
            return redirect(url_for('show_entries'))
    return render_template('login/html',error = error)

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect('show_entries')
