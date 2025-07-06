from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for sessions

def init_db():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()

    # Create contacts table with proper constraints and data types
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,   -- Ensuring unique email
            phone TEXT NOT NULL UNIQUE,   -- Ensuring unique phone number
            state TEXT NOT NULL,
            CHECK (state IN ('California', 'Texas', 'New York', 'Florida'))  -- Example constraint on states
        )
    ''')

    # Create users table for login with proper constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,  -- Ensure unique username
            password TEXT NOT NULL
        )
    ''')

    # Optional: insert a default user (only if table is empty)
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin123'))

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET','POST'])
def add_contact():
    if request.method=='POST':
        name=request.form['name']
        phone=request.form['phone']
        email=request.form['email']
        state=request.form['state']
        conn=sqlite3.connect('contacts.db')
        cursor=conn.cursor()
        cursor.execute('INSERT INTO contacts (name, phone, email, state) VALUES (?, ?, ?, ?)', (name, phone, email, state))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_contact(id):
    conn=sqlite3.connect('contacts.db')
    cursor=conn.cursor()
    if request.method=='POST':
        name=request.form['name']
        phone=request.form['phone']
        email=request.form['email']
        state=request.form['state']
        cursor.execute('UPDATE contacts SET name=?, phone=?, email=?, state=? WHERE id=?', (name, phone, email, state, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    cursor.execute('SELECT * FROM contacts WHERE id=?', (id,))
    contact=cursor.fetchone()
    conn.close()
    return render_template('update.html', contact=contact)

@app.route('/delete/<int:id>')
def delete_contact(id):
    conn=sqlite3.connect('contacts.db')
    cursor=conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR state LIKE ?", ('%' + keyword + '%', '%' + keyword + '%'))
        results = cursor.fetchall()
        conn.close()
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
