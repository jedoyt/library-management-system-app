from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort, Unauthorized, Forbidden


from app.auth import login_required
from app.db import get_db
from app.objects import categories, badge

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
    
    if not g.user['library_staff']:
        raise Unauthorized

    return render_template('book/add_book.html', categories=categories)

@bp.route('/new_books', methods=('GET', 'POST'))
@login_required
def new_books():
    if not g.user['library_staff']:
        raise Forbidden

    search_results = list()
    search_results_header = "Search Results"

    if request.method == 'POST':
        title = request.form['book_title']
        author = request.form['book_author']
        category = request.form['book_category']

        search_results = get_db().execute(
            'SELECT * FROM book WHERE book.id NOT IN (SELECT book_id FROM book_log)'
            ' AND title LIKE "%" || ? || "%"'
            ' AND author LIKE "%" || ? || "%"'
            ' AND category LIKE "%" || ? || "%"', (title, author, category)
        ).fetchall()
        print([(book['title'], book['author'], book['category']) for book in search_results])

        search_results_header = f"Search Results for Title:'{title}' Author:'{author}' Category:'{category}'"

        return render_template(
            'book/new_books.html', search_results=search_results,
            search_results_header=search_results_header, categories=categories
            )

    return render_template(
        'book/new_books.html', search_results=search_results,
        search_results_header=search_results_header, categories=categories
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
    
    if not g.user['library_staff']:
        raise Unauthorized

    return render_template('book/edit_book.html', book=book, categories=categories)

# Helper for pagination of browse_books
def paginate_results(results, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    # print([r for r in results][:5])
    return [r for r in results][start:end]

@bp.route('/books', methods=('GET', 'POST'))
@login_required
def browse_books():
    if request.method == 'POST':
        title = request.form['book_title']
        author = request.form['book_author']
        category = request.form['book_category']

        search_results = get_db().execute(
            'SELECT MAX(book_log.id), datetime_log, book_status, user_id, book_id, full_name, title, author, category'
            ' FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id'
            ' WHERE title LIKE "%" || ? || "%"'
            ' AND author LIKE "%" || ? || "%"'
            ' AND category LIKE "%" || ? || "%"'
            ' GROUP BY book_id'
            ' ORDER BY MAX(book_log.id) DESC', (title, author, category)
        ).fetchall()
        
        search_results_header = f"Search results for Title: '{title}' Author: '{author}' Category: '{category}'"

        if search_results:
            # Convert SQLite Row objects to dictionaries
            # Limit search results to 50 hits
            results = [dict(row) for row in search_results][:50]

            #Format datetime object
            for row in results:
                row['datetime_log'] = row['datetime_log'].strftime('%B %-d, %Y %-I:%M %p')

            # Store the search results in the session
            session['results'] = results
            session['results_header'] = search_results_header
            return redirect(url_for('book.browse_books'))
        else:
            # No results found
            return render_template('book/books.html', search_results_header="No results found!", categories=categories)
    else:
        # Retrieve the search results from the session, if any
        results = session.get('results')
        search_results_header = session.get('results_header')
        if results:
            # Paginate the search results
            page = request.args.get('page', 1, type=int)
            per_page = 5
            paginated_results = paginate_results(results, page, per_page)
            total_pages = len(results) // per_page + (len(results) % per_page > 0)

            return render_template(
                'book/books.html', search_results_header=search_results_header, search_results=paginated_results, 
                total_pages=total_pages, current_page=page, badge=badge, categories=categories,
            )
        else:
            # Render the initial search page
            return render_template('book/books.html', categories=categories)

@bp.route('/delete/<int:book_id>', methods=('GET', 'POST'))
@login_required
def delete_book(book_id):
    if not g.user['library_staff']:
        raise Unauthorized
    get_book_details(book_id=book_id)
    db = get_db()
    db.execute('DELETE FROM book WHERE id = ?', (book_id,))
    db.commit()
    return redirect(url_for('book.browse_books'))