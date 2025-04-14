from flask import Flask, render_template, request,redirect,url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()
@app.route('/')
def index():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts')
    contacts = cursor.fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['GET','POST'])
def add_contact():
    if request.method=='POST':
        name=request.form['name']
        phone=request.form['phone']
        email=request.form['email']
        conn=sqlite3.connect('contacts.db')
        cursor=conn.cursor()
        cursor.execute('INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)', (name, phone, email))
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
        cursor.execute('UPDATE contacts SET name=?, phone=?, email=? WHERE id=?', (name, phone, email, id))
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
    c=conn.cursor()
    c.execute('DELETE FROM contacts WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,port=5001)