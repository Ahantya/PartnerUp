from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_talisman import Talisman
import csv
import traceback

app = Flask(__name__)
Talisman(app)
app.secret_key = 'your_secret_key'

soumik = []
aaron = ""

import csv
from flask import Flask, render_template, request, make_response

@app.route('/generate_report', methods=['GET'])
def generate_report():
    search_term = request.args.get('search', '')  # Get the search term from the query string

    conn = get_db_connection()

    # Retrieve partners based on the search term
    partners = conn.execute(
        'SELECT * FROM partners WHERE name LIKE ? OR address LIKE ? OR description LIKE ? OR category LIKE ?',
        ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%',)
    ).fetchall()

    conn.close()

    # Create a CSV string with the partner data
    csv_data = "Category,Name,Description,Size,Street,City,Zip,Phone,Website\n"
    for partner in partners:
        # Unpack the partner data
        category, name, description, size, address, phone, website = partner['category'], partner['name'], partner['description'], partner['size'], partner['address'], partner['phone'], partner['website']

        # Split address into street, city, and zip
        if address:
            address_parts = address.split(', ')
            if len(address_parts) >= 3:
                street, city, zip_code = address_parts[0], address_parts[1], address_parts[2]
            else:
                street, city, zip_code = address_parts[0], '', ''

        # Format the website URL if needed
        if website and not website.startswith("http://") and not website.startswith("https://"):
            website = "https://" + website

        # Create the CSV row
        csv_data += f"{category},{name},{description},{size},{street},{city},{zip_code},{phone},{website}\n"

    # Create a response with the CSV as a file attachment
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=partners_report.csv'

    return response


 
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
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            size TEXT NOT NULL,
            address TEXT,
            phone TEXT,
            website TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Create the 'partners' table when the app starts
create_table()
users = {
    'admin': ['LASAdmin90@', 'yes'],
    'student': ['LAStudent90@', 'no']
}

@app.route('/create', methods = ['GET','POST'])
def create():
    if request.method == 'POST':
        # Get data from the request
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin')

        # Add new entry to users dictionary
        users[username] = [password, is_admin]
    print(users)
    return render_template('create.html')

@app.route('/about')
def about():
    return render_template('about.html', check_if_user_is_admin=check_if_user_is_admin)

# Login route - Displays login form
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match
        if username in users and users[username][0] == password:
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
@app.route('/index', methods=['GET', 'POST'])
def index():
    global aaron

    if not check_if_user_is_admin:
        return redirect(url_for('login'))

    user = session['user']
    conn = get_db_connection()

    search_term = request.args.get('search', '')  # Get the search term from the query string
    aaron = search_term
    if request.method == 'POST':
        search_term = request.form['search']
        aaron = search_term;
        
        # Perform the search query as before

    # Retrieve partners based on the search term
    partners = conn.execute(
        'SELECT * FROM partners WHERE name LIKE ? OR address LIKE ? OR description LIKE ? OR category LIKE ?',
        ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%',)
    ).fetchall()

    conn.close()

    # Pass the search term and partners to the template
    return render_template('index.html', partners=partners, user=user, check_if_user_is_admin=check_if_user_is_admin, search_term=search_term)





# Search route - Allows searching for partners (for both admin and student)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))
    

    if request.method == 'POST':
        search_term = request.form['search']
        conn = get_db_connection()
        # Updated query to search by name, address, description, or category
        partners = conn.execute(
            'SELECT * FROM partners WHERE name LIKE ? OR address LIKE ? OR description LIKE ? OR category LIKE ?',
            ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%',)
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
        category = request.form['category']
        name = request.form['name']
        description = request.form['description']
        size = request.form['size']
        address = request.form['address']
        phone = request.form['phone']
        website = request.form['website']
        if not website.startswith("http://") and not website.startswith("https://") and len(website)!=0:
            website = "https://" + website


        conn = get_db_connection()
        conn.execute(
            'INSERT INTO partners (category, name, description, size, address, phone, website) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (category, name, description, size, address, phone, website)
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    error_message = session.pop('error_message', None)

    return render_template('add.html', user=session['user'], error_message=error_message)

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
    

    conn = get_db_connection()
    partner = conn.execute('SELECT * FROM partners WHERE id = ?', (partner_id,)).fetchone()
    search_term = request.args.get('search')

    if check_if_user_is_admin() == False:
        return render_template('studentView.html', partner=partner)

    if partner is None:
        flash('Partner not found', 'error')
        conn.close()
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Retrieve updated details from the form
        category = request.form['Category']
        name = request.form['name']
        description = request.form['description']
        size = request.form['size']
        address = request.form['address']
        phone = request.form['phone']
        website = request.form['website']
        if not website.startswith("http://") and not website.startswith("https://") and len(website)!=0:
            website = "https://" + website
    
        
        conn.execute(
            'UPDATE partners SET category = ?, name = ?, description = ?, size = ?, address = ?, phone = ?, website = ? WHERE id = ?',
            (category, name, description, size, address, phone, website, partner_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    

    conn.close()  # Get the search term from the URL
    return render_template('edit.html', partner=partner, aaron=aaron)

# Delete all partners route - Deletes all partners from the database
@app.route('/delete_all', methods=['POST'])
def delete_all():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Retrieve all partners to be deleted
    partners_to_delete = conn.execute('SELECT * FROM partners').fetchall()
    

    # Save the partners to be deleted in the session
    global soumik
    soumik = [{'category': partner['category'], 'name': partner['name'], 'description': partner['description'], 'size': partner['size'], 'address': partner['address'], 'phone': partner['phone'], 'website': partner['website'] } for partner in partners_to_delete]

    
    # Delete all partners from the table
    conn.execute('DELETE FROM partners')
    conn.commit()

    conn.close()

    return redirect(url_for('index'))


def undo_deleted_partners():

    deleted_partners = session.pop('deleted_partners', None)
    # print(soumik)
    if soumik:
        conn = get_db_connection()
        for partner in soumik:
            conn.execute(
                'INSERT INTO partners (category, name, description, size, address, phone, website) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (partner['category'], partner['name'], partner['description'], partner['size'], partner['address'], partner['phone'], partner['website'])
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
        session['error_message'] = "No file part"
        return redirect(url_for('add'))

    file = request.files['file']

    if file.filename == '':
        session['error_message'] = "No selected file"
        return redirect(url_for('add'))

    if file:
        try:
            process_csv(file)
            session['success_message'] = "File processed successfully!"
            return redirect(url_for('index'))
        except Exception as e:
            session['error_message'] = "An error occurred while processing the file."
            # Optional: You can log the exception for debugging
            traceback.print_exc()

    return redirect(url_for('add'))
def process_csv(csv_file):
    # Implement your CSV processing logic here
    # Example: Read the CSV file and add data to the database
    conn = sqlite3.connect('partners.db')
    c = conn.cursor()
    
    csv_data = csv_file.stream.read().decode("utf-8")
    csv_reader = csv.reader(csv_data.splitlines())

    # Skip the header row
    next(csv_reader, None)
    
    try:
        for row in csv_reader:
            # Check if the row contains the expected number of fields (5)
            if len(row) != 9:
                raise Exception("Invalid row format: Expected 9 fields")
            
            category, name, description, size, street, city, zip, phone, website = row
            if not website.startswith("http://") and not website.startswith("https://") and len(website) > 0:
                website = "https://" + website
            address = f"{street}, {city}, {zip}"
            c.execute("INSERT INTO partners (category, name, description, size, address, phone, website) VALUES (?, ?, ?, ?, ?, ?, ?)", (category, name, description, size, address, phone, website))
    except csv.Error as e:
        # If an error occurs during CSV parsing, raise an exception
        raise Exception(f'CSV parsing error: {str(e)}')
    finally:
        conn.commit()
        conn.close()


def check_if_user_is_admin():
    return session['user'][1] == 'no'

if __name__ == '__main__':
    app.run(debug=True)