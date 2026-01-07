from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import date
import os

app = Flask(__name__)
app.secret_key = "gym_2026_key"
DB_NAME = 'gym_database.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS members 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT NOT NULL, 
                       password TEXT NOT NULL,
                       contact TEXT, 
                       plan TEXT,
                       join_date TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if role == "admin" and username == "admin" and password == "admin123":
        session['user'], session['role'] = "Admin", "admin"
        return redirect(url_for('admin_dashboard'))
    
    elif role == "member":
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE name=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'], session['role'] = user[1], "member"
            return redirect(url_for('member_dashboard'))
    return "Invalid! <a href='/'>Try Again</a>"

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session['role'] != "admin": return redirect('/')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    conn.close()
    return render_template('admin.html', members=members)

@app.route('/add', methods=['POST'])
def add():
    name, pwd = request.form.get('name'), request.form.get('password')
    contact, plan = request.form.get('contact'), request.form.get('plan')
    today = date.today().strftime("%d-%m-%Y")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (name, password, contact, plan, join_date) VALUES (?, ?, ?, ?, ?)", 
                   (name, pwd, contact, plan, today))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete/<int:id>')
def delete_member(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/member_dashboard')
def member_dashboard():
    if 'user' not in session: return redirect('/')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE name=?", (session['user'],))
    m = cursor.fetchone()
    conn.close()
    return render_template('member.html', m=m)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
