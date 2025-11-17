# Library Management System App

A Flask-based library management system for tracking books, users, and book activity logs.

## Prerequisites

Before you get started, make sure you have the following installed:

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd library-management-system-app
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install flask
   ```

## Database Setup

### Initialize the Database

Before running the application for the first time, you need to initialize the database with the required tables.

**Option 1: Using Flask CLI (Recommended)**

Run the following command:

```bash
flask --app app init-db
```

This command will:
- Create the SQLite database file (`app_db.sqlite`)
- Create the necessary tables: `user`, `book`, and `book_log`
- Clear any existing data from previous runs

**Option 2: Using Python Script**

Alternatively, you can run the `db_actions.py` script:

```bash
python db_actions.py
```

This script will:
- Initialize the database with all required tables
- Provide feedback on whether initialization was successful

**Note**: Both methods clear all existing data. Only run them when you want to start fresh.

## Running the Application

To start the development server:

```bash
flask --app app run --debug
```

The application will be available at `http://localhost:5000`

The `--debug` flag enables:
- Automatic server reloading on code changes
- Interactive debugger for error handling
- Enhanced error messages

## Project Structure

- `app/` - Main application package
  - `__init__.py` - App factory and blueprint registration
  - `db.py` - Database connection and initialization logic
  - `auth.py` - Authentication blueprint
  - `book.py` - Book management blueprint
  - `book_log.py` - Book activity log blueprint
  - `schema.sql` - Database schema definitions
  - `templates/` - HTML templates for the web interface
- `main.py` - Entry point for the application
- `db_actions.py` - Database utility functions
- `library_catalogue.csv` - Sample library data

## Database Schema

### Tables

- **user** - Stores user information
  - `id` - User ID
  - `email` - User email (unique)
  - `user_password` - Hashed password
  - `full_name` - User's full name
  - `contact_number` - Contact information
  - `library_staff` - Boolean flag for staff status

- **book** - Stores book information
  - `id` - Book ID
  - `title` - Book title
  - `author` - Author name
  - `category` - Book category
  - `ean_isbn13` - EAN/ISBN-13 code
  - `upc_isbn10` - UPC/ISBN-10 code
  - `book_desc` - Book description
  - `publisher` - Publisher name
  - `date_published` - Publication date
  - `date_added` - Date when book was added to system
  - `pages` - Number of pages

- **book_log** - Tracks book activity
  - `id` - Log entry ID
  - `datetime_log` - Timestamp of the activity
  - `remarks` - Additional notes
  - `book_status` - Current status of the book
  - `user_id` - Reference to user
  - `book_id` - Reference to book

## Quick Start Guide

1. Activate your virtual environment
2. Run `flask --app app init-db` to initialize the database
3. Run `flask --app app run --debug` to start the server
4. Open your browser and navigate to `http://localhost:5000`
5. Visit `http://localhost:5000/hello` to verify the app is running

## Troubleshooting

- **"No such command 'init-db'"**: Make sure you're running the command from the project root directory and Flask is properly installed
- **Database locked error**: Close any other instances of the app and try again
- **Port 5000 already in use**: The port is occupied by another service. You can specify a different port with: `flask --app app run --debug --port 5001`

## Contributing

When making changes to the database schema, update `app/schema.sql` and reinitialize the database with `flask --app app init-db`.
