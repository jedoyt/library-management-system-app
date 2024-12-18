from datetime import datetime, timedelta, timezone
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import Unauthorized, BadRequest, Forbidden

from app.auth import login_required
from app.db import get_db
from app.objects import badge, book_status_list


bp = Blueprint('book_log', __name__)

@bp.route('/')
def index():
    db = get_db()
    
    book_logs = db.execute(
        "SELECT book_log.id, datetime_log, remarks, book_status, user_id, book_id, full_name, title, author"
        " FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id"
        " ORDER BY datetime_log DESC"
    ).fetchall()
    # Pagination objects
    page = request.args.get('page', 1, type=int)
    per_page = 5
    paginated_results = paginate_results(book_logs, page, per_page)
    total_pages = len(book_logs) // per_page + (len(book_logs) % per_page > 0)

    return render_template(
        'book_log/index.html', book_logs=paginated_results, 
        total_pages=total_pages, current_page=page, badge=badge
        )

# Helper for pagination
def paginate_results(results, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    # print([r for r in results][:5])
    return [r for r in results][start:end]

# Helper for getting book details
# def get_book_details(book_id):
#     book = get_db().execute(
#         'SELECT id, isbn, title, author, category, book_desc'
#         ' FROM book WHERE id = ?', (book_id,)
#     ).fetchone()

#     if book is None:
#         abort(404, f"Book id {book_id} doesn't exist.")
#     return book

# Helper for user authentication on borrow and return
def last_book_log(book_id):
    last_log = get_db().execute(
        "SELECT book_log.id, book_status, MAX(datetime_log), user_id FROM book_log"
        " WHERE book_id = ?"
        " GROUP BY book_id"
        " ORDER BY MAX(book_log.id) DESC;", (book_id,)
    ).fetchone()
    # print(f"Last Book Log: {dict(last_log)}")
    return last_log

def convert_current_utc_dt(delta_hour):
    # Convert string to datetime object
    dt = datetime.now().astimezone(timezone.utc)
    dt_strf = dt.strftime("%d/%m/%Y, %H:%M:%S")
    dt_strp = datetime.strptime(dt_strf, "%d/%m/%Y, %H:%M:%S")
    
    # Apply timedelta to shift from UTC to UTC+<delta_hour>
    utc_delta_hour = dt_strp + timedelta(hours=delta_hour)

    return utc_delta_hour

@bp.route('/borrow/<int:book_id>', methods=('GET', 'POST'))
@login_required
def borrow_book(book_id):
    # Check if book's last log is in "Available" status
    last_log = last_book_log(book_id=book_id)
    if last_log['book_status'] != 'Available':
        raise BadRequest
    
    book_info = get_db().execute(
        "SELECT * FROM book WHERE id = ?", (book_id,)
    ).fetchone()

    # Convert from UTC to UTC+8:00
    datetime_log = convert_current_utc_dt(delta_hour=8)

    db = get_db()
    db.execute(
        'INSERT INTO book_log (datetime_log, book_status, user_id, book_id) VALUES (?, ?, ?, ?)',
        (datetime_log, "Borrowed", session['user_id'], book_info['id'])
    )
    db.commit()
    
    return redirect(url_for('book.view_book_details', book_id=book_id))

@bp.route('/return/<int:book_id>', methods=('GET', 'POST'))
@login_required
def return_book(book_id):
    # Check if book's last log is in "Borrowed" status
    last_log = last_book_log(book_id=book_id)
    if last_log['book_status'] != 'Borrowed':
        raise BadRequest
    # Check if current user is the one who borrowed the book
    if last_log['user_id'] != session['user_id']:
        raise BadRequest

    # Convert from UTC to UTC+8:00
    datetime_log = convert_current_utc_dt(delta_hour=8)

    book_info = get_db().execute(
        "SELECT * FROM book WHERE id = ?", (book_id,)
    ).fetchone()
        
    db = get_db()
    db.execute(
        'INSERT INTO book_log (datetime_log, book_status, user_id, book_id) VALUES (?, ?, ?, ?)',
        (datetime_log, "Returned", session['user_id'], book_info['id'])
    )
    db.commit()
    
    return redirect(url_for('book.view_book_details', book_id=book_id))

@bp.route('/log_entry/<int:book_id>', methods=('GET', 'POST'))
@login_required
def enter_log(book_id):
    if not g.user['library_staff']:
        raise Unauthorized
    book_info = get_db().execute(
        "SELECT * FROM book WHERE id = ?", (book_id,)
    ).fetchone()
    if request.method == 'POST':
        # Convert from UTC to UTC+8:00
        datetime_log = convert_current_utc_dt(delta_hour=8)
        
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
                'INSERT INTO book_log (datetime_log, remarks, book_status, user_id, book_id) VALUES (?, ?, ?, ?, ?)',
                (datetime_log, book_remarks, book_status, g.user['id'], book_info['id'])
            )
            db.commit()
            return redirect(url_for('book.browse_books'))

    return render_template('book_log/log_entry.html', book_info=book_info, book_status_list=book_status_list)

@bp.route('/edit_log/<int:log_id>', methods=('GET', 'POST'))
@login_required
def edit_log(log_id):
    if not g.user['library_staff']:
        raise Unauthorized
    log_info = get_db().execute(
        "SELECT book_log.id, datetime_log, remarks, book_status, user_id, book_id, title, author, full_name"
        " FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id"
        " WHERE book_log.id = ?", (log_id,)
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
                'UPDATE book_log SET book_status = ? , remarks = ? WHERE book_log.id = ?;',
                (book_status, book_remarks, log_id)
            )
            db.commit()
            return redirect(url_for('book_log.index'))

    return render_template(
        'book_log/edit_log.html', log_info=log_info, 
        book_status_list=book_status_list, badge=badge
        )

@bp.route('/dashboard')
@login_required
def dashboard():
    # This page is only for library staff accounts
    if not g.user['library_staff']:
        raise Forbidden
    
    return render_template('book_log/dashboard.html')

@bp.route('/dashboard/borrowed')
@login_required
def get_all_borrowed():
    # This page is only for library staff accounts
    if not g.user['library_staff']:
        raise Forbidden
    borrowed_books = get_db().execute(
        'SELECT MAX(book_log.id), book_status, datetime_log, book_id, title, author, category, user_id, full_name, email, contact_number'
        ' FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id'
        ' GROUP BY book_id'
        ' ORDER BY MAX(book_log.id)'
    ).fetchall()

    borrowed_list = [dict(row) for row in borrowed_books if row['book_status'] == "Borrowed"]
    print(borrowed_list)
    for row in borrowed_list:
        print(f"datetime_log: {row['datetime_log']} | datatype: {type(row['datetime_log'])}")
        row['borrowed_days'] = (convert_current_utc_dt(delta_hour=8) - row['datetime_log']).days
        # try:
        #     row['borrowed_days'] = (convert_current_utc_dt(delta_hour=8) - row['datetime_log']).days
        # except Exception as e:
        #     # print(f"{e}\nNow using datetime.datetime.now() as current time.")
        #     row['borrowed_days'] = (datetime.now() - row['datetime_log']).days
    # print(borrowed_list[0])    

    return render_template('book_log/dashboard.html', borrowed_books=borrowed_list)

@bp.route('/dashboard/returned')
@login_required
def get_all_returned():
    # This page is only for library staff accounts
    if not g.user['library_staff']:
        raise Forbidden
    returned_books = get_db().execute(
        'SELECT MAX(book_log.id), book_status, datetime_log, book_id, title, author, category, user_id, full_name, email, contact_number'
        ' FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id'
        ' GROUP BY book_id'
        ' ORDER BY MAX(book_log.id) ASC'
    ).fetchall()

    returned_list = [dict(row) for row in returned_books if row['book_status'] == "Returned"]

    return render_template('book_log/dashboard.html', returned_books=returned_list)

@bp.route('/dashboard/users')
@login_required
def get_all_users():
    # This page is only for library staff accounts
    if not g.user['library_staff']:
        raise Forbidden
    users = get_db().execute(
        'SELECT * FROM user;'
    ).fetchall()

    return render_template('book_log/dashboard.html', users=users)