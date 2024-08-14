from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint('book_log', __name__)

@bp.route('/')
def index():
    badge = {
        'Available': 'success',
        'Borrowed': 'warning',
        'Returned': 'info',
        'Damaged': 'secondary',
        'Lost': 'dark',
    }
    db = get_db()
    
    book_logs = db.execute(
        "SELECT book_log.id, datetime_log, remarks, book_status, user_id, book_id, full_name, title, author"
        " FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id"
        " ORDER BY datetime_log DESC"
    ).fetchall()
    # Pagination objects
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(book_logs) + per_page - 1) // per_page

    return render_template(
        'book_log/index.html', book_logs=book_logs[start:end], 
        badge=badge, total_pages=total_pages, page=page
        )

def get_book_details(book_id):
    book = get_db().execute(
        'SELECT id, isbn, title, author, category, book_desc'
        ' FROM book WHERE id = ?', (book_id,)
    ).fetchone()

    if book is None:
        abort(404, f"Book id {book_id} doesn't exist.")
    return book

@bp.route('/borrow/<int:book_id>', methods=('GET', 'POST'))
@login_required
def borrow_book(book_id):
    book_info = get_db().execute(
        "SELECT * FROM book WHERE id = ?", (book_id,)
    ).fetchone()
    
    db = get_db()
    db.execute(
        'INSERT INTO book_log (book_status, user_id, book_id) VALUES (?, ?, ?)',
        ("Borrowed", session['user_id'], book_info['id'])
    )
    db.commit()
    return redirect(url_for('book.view_book_details', book_id=book_id))

@bp.route('/return/<int:book_id>', methods=('GET', 'POST'))
@login_required
def return_book(book_id):
    book_info = get_db().execute(
        "SELECT * FROM book WHERE id = ?", (book_id,)
    ).fetchone()
    
    db = get_db()
    db.execute(
        'INSERT INTO book_log (book_status, user_id, book_id) VALUES (?, ?, ?)',
        ("Returned", session['user_id'], book_info['id'])
    )
    db.commit()
    return redirect(url_for('book.view_book_details', book_id=book_id))

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