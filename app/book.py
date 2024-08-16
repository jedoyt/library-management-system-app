from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db
from app.objects import categories, badge #required_dict, nullables_dict

bp = Blueprint('book', __name__)

@bp.route('/add_book', methods=('GET', 'POST'))
@login_required
def add_book():
    if request.method == 'POST':
        # Form dictionaries for adding/editing of books
        required_dict = {
                    'Title': request.form['book_title'],
                    'Category': request.form['book_category'],
                }

        nullables_dict = {
                    'Author': request.form['book_author'],
                    'EAN_ISBN13': request.form['ean_isbn13'],
                    'UPC_ISBN10': request.form['upc_isbn10'],
                    'Book_Desc': request.form['book_desc'],
                    'Publisher': request.form['publisher'],
                    'Date_Published': request.form['date_published'],
                    'Date_Added': request.form['date_added'],
                    'Pages': request.form['pages']
                }
        error = None
        for detail, form_field in required_dict.items():
            if not form_field:
                error = f"{detail} is required."
        
        print(f"[add_book] Captured form entries: {request.form}")
        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Add book
            db.execute(
                "INSERT INTO book (title, category, author, ean_isbn13, upc_isbn10, book_desc, publisher, date_published, date_added, pages)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (required_dict['Title'], required_dict['Category'], nullables_dict['Author'], 
                 nullables_dict['EAN_ISBN13'], nullables_dict['UPC_ISBN10'], nullables_dict['Book_Desc'], nullables_dict['Publisher'], 
                 nullables_dict['Date_Published'], nullables_dict['Date_Added'], nullables_dict['Pages'])
            )
            recent_id = db.execute(
                "SELECT MAX(id) FROM book;"
            ).fetchone()
            print(f"Recent ID: {recent_id}")
            db.commit()
            
            # Create first log of newly added book
            # log_new_book(book_id=recent_id)
            
            return redirect(url_for('book.new_books'))
    return render_template('book/add_book.html', categories=categories)

@bp.route('/new_books', methods=('GET',))
@login_required
def new_books():
    book_ids_queried = get_db().execute('SELECT id FROM book;')
    book_ids = book_ids_queried.fetchall()

    logged_book_ids_queried = get_db().execute(
        'SELECT book_id FROM book_log'
        ' GROUP BY book_id ORDER BY MAX(datetime_log) DESC;'
    )
    logged_book_ids = logged_book_ids_queried.fetchall()

    unlogged_book_ids = list()

    for book in book_ids:
        try:
            if book['id'] not in [book_log['book_id'] for book_log in logged_book_ids]:
                unlogged_book_ids.append(book['id'])
            else:
                continue
        except Exception as e:
            print("No logs present on book_log table")
            unlogged_book_ids.append(book['id'])
        
    unlogged_books = [get_book_details(id) for id in unlogged_book_ids]

    # Pagination objects
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(unlogged_books) + per_page - 1) // per_page

    return render_template(
        'book/new_books.html', unlogged_books=unlogged_books[start:end],
        total_pages=total_pages, page=page
        )

def get_book_details(book_id):
    book = get_db().execute('SELECT * FROM book WHERE id = ?', (book_id,)).fetchone()

    if book is None:
        abort(404, f"Book id {book_id} doesn't exist.")
    return book

@bp.route('/book_details/<int:book_id>', methods=('GET','POST'))
@login_required
def view_book_details(book_id):
    book = get_book_details(book_id=book_id)
    db = get_db()
    book_logs = db.execute(
        "SELECT book_log.id, datetime_log, remarks, book_status, user_id, book_id, full_name, title, author"
        " FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id"
        " WHERE book_id = ?"
        " ORDER BY datetime_log DESC", (book_id,)
    ).fetchall()
    try:
        latest_log = book_logs[0]
    except Exception as e:
        print(f"No existing logs. Possible new book. Enter initial log.\n{e}")
        # Need to enter initial log
        return redirect(url_for('book_log.enter_log', book_id=book_id))

    # Pagination objects
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(book_logs) + per_page - 1) // per_page

    return render_template(
        'book/book_details.html', book=book, book_logs=book_logs[start:end], latest_log=latest_log, 
        badge=badge, total_pages=total_pages, page=page
        )

@bp.route('/edit_book_details/<int:book_id>', methods=("GET", "POST"))
@login_required
def edit_book_details(book_id):
    book = get_book_details(book_id)

    if request.method == "POST":
        # Form dictionaries for adding/editing of books
        required_dict = {
                    'Title': request.form['book_title'],
                    'Category': request.form['book_category'],
                }

        nullables_dict = {
                    'Author': request.form['book_author'],
                    'EAN_ISBN13': request.form['ean_isbn13'],
                    'UPC_ISBN10': request.form['upc_isbn10'],
                    'Book_Desc': request.form['book_desc'],
                    'Publisher': request.form['publisher'],
                    'Date_Published': request.form['date_published'],
                    'Date_Added': request.form['date_added'],
                    'Pages': request.form['pages']
                }
        error = None
        for detail, form_field in required_dict.items():
            if not form_field:
                error = f"{detail} is required."

        print(f"[edit_book_details] Captured form entries: {request.form}")

        # if no date inputs
        if request.form['date_published'] == "":
            nullables_dict['Date_Published'] = book['date_published']
        if request.form['date_added'] == "":
            nullables_dict['Date_Added'] = book['date_added']

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # Update book details
            db.execute(
                "UPDATE book SET title = ?, category = ?, author = ?, ean_isbn13 = ?, upc_isbn10 = ?,"
                " book_desc = ?, publisher = ?, date_published = ?, date_added = ?, pages = ?"
                " WHERE book.id = ?",
                (required_dict['Title'], required_dict['Category'], nullables_dict['Author'], 
                 nullables_dict['EAN_ISBN13'], nullables_dict['UPC_ISBN10'], nullables_dict['Book_Desc'], nullables_dict['Publisher'], 
                 nullables_dict['Date_Published'], nullables_dict['Date_Added'], nullables_dict['Pages'], book_id)
            )
            db.commit()
            return redirect(url_for('book.view_book_details', book_id=book_id))

    return render_template('book/edit_book.html', book=book, categories=categories)

@bp.route('/books')
def browse_books():
    all_books = get_db().execute(
        'SELECT book_log.id, MAX(datetime_log), book_status, user_id, book_id, full_name, title, author, category'
        ' FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id'
        ' GROUP BY book_id'
        ' ORDER BY MAX(datetime_log) DESC'
    ).fetchall()
    # Pagination objects
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(all_books) + per_page - 1) // per_page

    return render_template(
        'book/books.html', all_books=all_books[start:end], badge=badge,
        total_pages=total_pages, page=page
        )

@bp.route('/delete/<int:book_id>', methods=('GET', 'POST'))
@login_required
def delete_book(book_id):
    get_book_details(book_id=book_id)
    db = get_db()
    db.execute('DELETE FROM book WHERE id = ?', (book_id,))
    db.commit()
    return redirect(url_for('book.browse_books'))