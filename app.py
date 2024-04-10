from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_talisman import Talisman
import csv

app = Flask(__name__)
Talisman(app)
app.secret_key = 'your_secret_key'

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
            email TEXT NOT NULL,
            number TEXT NOT NULL     
        )
    ''')
    conn.commit()
    conn.close()

# Create the 'partners' table when the app starts
create_table()
users = {
    'admin': 'LASAdmin90@',
    'student': 'LAStudent90@'
}

# Login route - Displays login form
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
        
        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

# Logout route - Clears session
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Home route - Displays all partners
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    conn = get_db_connection()
    
    if user == 'admin' or user == 'student':
        partners = conn.execute('SELECT * FROM partners').fetchall()
        conn.close()
        return render_template('index.html', partners=partners, user=user, check_if_user_is_admin=check_if_user_is_admin)

    return render_template('index.html', user=user, check_if_user_is_admin=check_if_user_is_admin)



# Search route - Allows searching for partners (for both admin and student)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        search_term = request.form['search']
        conn = get_db_connection()
        partners = conn.execute(
            'SELECT * FROM partners WHERE name LIKE ?',
            ('%' + search_term + '%',)
        ).fetchall()
        conn.close()
        return render_template('index.html', partners=partners, user=session['user'], check_if_user_is_admin=check_if_user_is_admin)
    else:
        # Handle GET request, just render the search template
        return render_template('index.html', user=session['user'], check_if_user_is_admin=check_if_user_is_admin)


# Add partner route - Displays form to add a new partner (only for admin)
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        partner_type = request.form['type']
        resources = request.form['resources']
        email = request.form['email']
        number = request.form['number']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO partners (name, type, resources, email, number) VALUES (?, ?, ?, ?, ?)',
            (name, partner_type, resources, email, number)
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))

    return render_template('add.html', user=session['user'])

# Delete partner route - Deletes a partner from the database
@app.route('/delete/<int:partner_id>', methods=['POST'])
def delete(partner_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Delete the partner with the specified id
    conn.execute('DELETE FROM partners WHERE id = ?', (partner_id,))
    conn.commit()

    # Retrieve all remaining partners after deletion
    remaining_partners = conn.execute('SELECT * FROM partners').fetchall()

    # Reorder the ids starting from 1
    for index, partner in enumerate(remaining_partners, start=1):
        conn.execute('UPDATE partners SET id = ? WHERE id = ?', (index, partner['id']))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/edit/<int:partner_id>', methods=['GET', 'POST'])
def edit(partner_id):
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    partner = conn.execute('SELECT * FROM partners WHERE id = ?', (partner_id,)).fetchone()

    if partner is None:
        flash('Partner not found', 'error')
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Retrieve updated details from the form
        name = request.form['name']
        partner_type = request.form['type']
        resources = request.form['resources']
        email = request.form['email']
        number = request.form['number']

        # Update partner details in the database
        conn.execute(
            'UPDATE partners SET name = ?, type = ?, resources = ?, email = ?, number = ? WHERE id = ?',
            (name, partner_type, resources, email, number, partner_id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    conn.close()

    return render_template('edit.html', partner=partner)
# Delete all partners route - Deletes all partners from the database
@app.route('/delete_all', methods=['POST'])
def delete_all():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Retrieve all partners to be deleted
    partners_to_delete = conn.execute('SELECT * FROM partners').fetchall()

    # Save the partners to be deleted in the session
    session['deleted_partners'] = [{ 'name': partner['name'], 'type': partner['type'], 'resources': partner['resources'], 'email': partner['email'], 'number': partner['number'] } for partner in partners_to_delete]

    # Delete all partners from the table
    conn.execute('DELETE FROM partners')
    conn.commit()

    conn.close()

    return redirect(url_for('index'))


def undo_deleted_partners():
    deleted_partners = session.pop('deleted_partners', None)
    if deleted_partners:
        conn = get_db_connection()
        for partner in deleted_partners:
            conn.execute(
                'INSERT INTO partners (name, type, resources, email, number) VALUES (?, ?, ?, ?, ?)',
                (partner['name'], partner['type'], partner['resources'], partner['email'], partner['number'])
            )
        conn.commit()
        conn.close()

@app.route('/undo', methods=['GET'])
def undo():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    undo_deleted_partners()

    return redirect(url_for('index'))
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        try:    # Assuming you have a function to process the CSV and add data to the database
            process_csv(file)
            return redirect(url_for('index'))
        except Exception as e:
            return f'Error uploading file: {str(e)}'

def process_csv(csv_file):
    # Implement your CSV processing logic here
    # Example: Read the CSV file and add data to the database
    conn = sqlite3.connect('partners.db')
    c = conn.cursor()
    
    csv_data = csv_file.stream.read().decode("utf-8")
    csv_reader = csv.reader(csv_data.splitlines())
    
    try:
        for row in csv_reader:
            # Check if the row contains the expected number of fields (5)
            if len(row) != 5:
                raise Exception("Invalid row format: Expected 5 fields")
            
            name, member_type, resources, email, number = row
            c.execute("INSERT INTO partners (name, type, resources, email, number) VALUES (?, ?, ?, ?, ?)", (name, member_type, resources, email, number))
    except csv.Error as e:
        # If an error occurs during CSV parsing, raise an exception
        raise Exception(f'CSV parsing error: {str(e)}')
    finally:
        conn.commit()
        conn.close()

def check_if_user_is_admin():
    return session['user'] != 'student'

if __name__ == '__main__':
    app.run(debug=True)
