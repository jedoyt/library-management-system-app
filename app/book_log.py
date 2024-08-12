from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint('book_log', __name__)

@bp.route('/')
def index():
    db = get_db()
    book_logs = db.execute(
        "SELECT book_log.id, datetime_log, remarks, book_status, user_id, book_id, full_name, title, author"
        " FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id"
        " ORDER BY datetime_log DESC"
    ).fetchall()
    return render_template('book_log/index.html', book_logs=book_logs)

@bp.route('/add_book', methods=('GET', 'POST'))
@login_required
def add_book():
    if request.method == 'POST':
        book_dict = {
            'ISBN': request.form['book_isbn'],
            'Title': request.form['book_title'],
            'Author': request.form['book_author'],
            'Category': request.form['book_category'],
        }
        
        error = None
        for detail, form_field in book_dict.items():
            if not form_field:
                error = f"{detail} is required. Put 'N/A' if data not available."

        book_desc = request.form['book_desc']
        # print(f"Captured entries: {request.form}")
        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Add book
            db.execute(
                "INSERT INTO book (isbn, title, author, category, book_desc) VALUES (?, ?, ?, ?, ?)", 
                (book_dict['ISBN'], book_dict['Title'], book_dict['Author'], book_dict['Category'], book_desc,)
            )
            db.commit()
            
            return redirect(url_for('book_log.index'))
    return render_template('book_log/add_book.html')

def get_book_details(book_id):
    book = get_db().execute(
        'SELECT id, isbn, title, author, category, book_desc'
        ' FROM book WHERE id = ?', (book_id,)
    ).fetchone()

    if book is None:
        abort(404, f"Book id {book_id} doesn't exist.")
    return book

@bp.route('/edit_book_details/<int:book_id>', methods=("GET", "POST"))
@login_required
def edit_book_details(book_id):
    book = get_book_details(book_id)
    
    if request.method == "POST":
        book_dict = {
            'ISBN': request.form['book_isbn'],
            'Title': request.form['book_title'],
            'Author': request.form['book_author'],
            'Category': request.form['book_category'],
        }
        
        error = None
        for detail, form_field in book_dict.items():
            if not form_field:
                error = f"{detail} is required. Put 'N/A' if data not available."

        book_desc = request.form['book_desc']
        # print(f"Captured entries: {request.form}")
        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Add book
            db.execute(
                "UPDATE book SET isbn = ?, title = ?, author = ?, category = ?, book_desc = ? WHERE book.id = ?",
                (book_dict['ISBN'], book_dict['Title'], book_dict['Author'], book_dict['Category'], book_desc, book_id)
            )
            db.commit()
            return redirect(url_for('book_log.list_books'))

    return render_template('book_log/edit_book.html', book=book)

@bp.route('/books')
def list_books():
    all_books = get_db().execute(
        'SELECT * FROM book'
    ).fetchall()

    return render_template('book_log/books.html', all_books=all_books)

@bp.route('/log_entry/<int:book_id>', methods=('GET', 'POST'))
@login_required
def enter_log(book_id):
    book_info = get_db().execute(
        "SELECT * FROM book WHERE id = ?", (book_id,)
    ).fetchone()
    if request.method == 'POST':
        book_status = request.form['book_status']
        book_remarks = request.form['book_remarks']
        
        error = None
        if not book_status:
            error = "Status is required."
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO book_log (remarks, book_status, user_id, book_id) VALUES (?, ?, ?, ?)',
                (book_remarks, book_status, g.user['id'], book_info['id'])
            )
            db.commit()
            return redirect(url_for('book_log.index'))

    return render_template('book_log/log_entry.html', book_info=book_info)