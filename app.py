from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('partners.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the 'partners' table if it doesn't exist
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            resources TEXT,
            contact TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Create the 'partners' table when the app starts
create_table()

# Home route - Displays all partners
@app.route('/')
def index():
    conn = get_db_connection()
    partners = conn.execute('SELECT * FROM partners').fetchall()
    conn.close()
    return render_template('index.html', partners=partners)

# Search route - Allows searching for partners
# Search route - Allows searching for partners
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        conn = get_db_connection()
        partners = conn.execute(
            'SELECT * FROM partners WHERE name LIKE ?',
            ('%' + search_term + '%',)
        ).fetchall()
        conn.close()
        return render_template('index.html', partners=partners)
    
    # For GET requests or initial page load
    return redirect(url_for('index'))


# Add partner route - Displays form to add a new partner
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        partner_type = request.form['type']
        resources = request.form['resources']
        contact = request.form['contact']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO partners (name, type, resources, contact) VALUES (?, ?, ?, ?)',
            (name, partner_type, resources, contact)
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))

    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True)
