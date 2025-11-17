import functools
from app.objects import badge, default_reset_password
from werkzeug.exceptions import Unauthorized


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    When the user visits the /auth/register URL, the register view will return HTML with a form for them to fill out. 
    When they submit the form, it will validate their input and either show the form again with an error message or 
    create the new user and go to the login page.
    """
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        contact_number = request.form['contact_number']
        library_staff = False
        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not full_name:
            error = 'Full name is required.'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (email, user_password, full_name, contact_number, library_staff) VALUES (?, ?, ?, ?, ?)", 
                    (email, generate_password_hash(password), full_name, contact_number, library_staff),
                )
                db.commit()
            except db.IntegrityError:
                error = "Email is already registered."
                session['registration_error'] = error
                return render_template('auth/register.html', error=session['registration_error'])
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register.html')



@bp.route('/register/8bd92a815a5652d90006da9afd13e6f064e2b662', methods=('GET', 'POST'))
def register_staff():
    """
    This view is restricted to account registration of library staff
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        contact_number = request.form['contact_number']
        library_staff = True
        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not full_name:
            error = 'Full name is required.'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (email, user_password, full_name, contact_number, library_staff) VALUES (?, ?, ?, ?, ?)", 
                    (email, generate_password_hash(password), full_name, contact_number, library_staff),
                )
                db.commit()
            except db.IntegrityError:
                error = "Email is already registered."
                session['registration_error'] = error
                return render_template('auth/register_staff.html', error=session['registration_error'])
            else:
                return redirect(url_for("auth.login"))
        flash(error)

    return render_template('auth/register_staff.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    This view follows the same pattern as the register view above.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()

        if user is None:
            error = 'Incorrect email or password'
        elif not check_password_hash(user['user_password'], password=password):
            error = 'Incorrect email or password'

        if error:
            session['login_error'] = error
            return render_template('auth/login.html', error=session['login_error'])

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('book_log.index'))
        flash(error)
    return render_template('auth/login.html')

def login_required(view):
    """
    Require Authentication in Other Views
    Creating, editing, and deleting blog posts will require a user to be logged in. 
    This decorator can be used to check this for each view it’s applied to.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    """
    bp.before_app_request() registers a function that runs before the view function, 
    no matter what URL is requested. load_logged_in_user checks 
    if a user id is stored in the session and gets that user’s data from the database, 
    storing it on g.user, which lasts for the length of the request. 
    If there is no user id, or if the id doesn’t exist, g.user will be None.
    """
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

@bp.route('/user/<int:user_id>', methods=('GET', 'POST'))
@login_required
def user_page(user_id):
    if session['user_id'] != user_id:
        raise Unauthorized
    error = ""
    if request.method == 'POST':
        db = get_db()
        registered_emails = db.execute('SELECT email FROM user').fetchall()
        registered_names = db.execute('SELECT full_name from user').fetchall()
        email = request.form['email']
        full_name = request.form['full_name']
        contact_number = request.form['contact_number']

        # Check for changes in email and full name
        if email != g.user['email']:
            if email in registered_emails:
                error += " That email is already registered!"
        if full_name != g.user['full_name']:
            if full_name in registered_names:
                error += " That name is already taken!"

        if error == "":
            try:
                db.execute(
                    'UPDATE user SET email = ?, full_name = ?, contact_number = ? WHERE user.id = ?',
                    (email, full_name, contact_number, user_id)
                )
                db.commit()
            except db.IntegrityError:
                flash(error)
                return render_template('auth/user_page.html', error=error)
            else:
                return redirect(url_for('auth.user_page', user_id=session['user_id']))
    else:
        user_logs = get_db().execute(
            'SELECT book_log.id, datetime_log, book_status, user_id, book_id, full_name, title, author, category'
            ' FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id'
            ' WHERE user_id = ?'
            ' ORDER BY datetime_log DESC', (user_id,)
        ).fetchall()
        
        session['user_logs'] = [dict(log) for log in user_logs][:50]
        # Paginate the search results
        page = request.args.get('page', 1, type=int)
        per_page = 5
        paginated_results = paginate_results(session.get('user_logs'), page, per_page)
        total_pages = len(session['user_logs']) // per_page + (len(session.get('user_logs')) % per_page > 0)

        return render_template(
            'auth/user_page.html', error=error, user_logs=paginated_results,
            badge=badge, total_pages=total_pages, current_page=page
            )
    
# Helper for pagination
def paginate_results(results, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    # print([r for r in results][:5])
    return [r for r in results][start:end]

@bp.route('/logout')
def logout():
    """
    To log out, you need to remove the user id from the session.
    Then load_logged_in_user won’t load a user on subsequent requests.
    """
    session.clear()
    return redirect(url_for('auth.login'))

@bp.route('/user_settings/<int:user_id>', methods=('GET', 'POST'))
@login_required
def user_settings(user_id):
    # This page is only for library staff accounts
    if not g.user['library_staff']:
        raise Unauthorized
    
    # Load user details
    user = get_db().execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()

    # Display user logs
    user_logs = get_db().execute(
            'SELECT book_log.id, datetime_log, book_status, user_id, book_id, full_name, title, author, category'
            ' FROM book_log JOIN user ON book_log.user_id = user.id JOIN book ON book_log.book_id = book.id'
            ' WHERE user_id = ?'
            ' ORDER BY datetime_log DESC', (user_id,)
        ).fetchall()
        
    session['user_logs'] = [dict(log) for log in user_logs][:50]
    # Paginate the user logs
    page = request.args.get('page', 1, type=int)
    per_page = 5
    paginated_results = paginate_results(session.get('user_logs'), page, per_page)
    total_pages = len(session['user_logs']) // per_page + (len(session.get('user_logs')) % per_page > 0)

    if request.method == 'POST':
        # Radio Button Input
        role = request.form.get('roleRadio')

        if role == "Library Staff":
            library_staff = True
        else:
            library_staff = False

        db = get_db()
        db.execute(
            'UPDATE user SET library_staff = ? WHERE id = ?',
            (library_staff, user_id)
            )
        db.commit()

        return redirect(url_for('book_log.get_all_users'))
    
    return render_template(
        '/auth/user_settings.html', user=user, user_id=user_id, user_logs=paginated_results,
        badge=badge, total_pages=total_pages, current_page=page
        )

@bp.route('/change_password/<int:user_id>', methods=('GET', 'POST'))
@login_required
def change_password(user_id):
    if session['user_id'] != user_id:
        raise Unauthorized
    error = ""
    session['change_pw_status'] = error
    # Load user details
    user_password_hash = get_db().execute(
        'SELECT user_password FROM user WHERE id = ?', (user_id,)
    ).fetchone()['user_password']

    if request.method == 'POST':
        old_password = request.form['oldpassword']
        new_password = request.form['newpassword']
        if old_password and new_password:
            if check_password_hash(user_password_hash, old_password):
                db = get_db()
                db.execute(
                    "UPDATE user SET user_password = ? WHERE id = ?;",
                    (generate_password_hash(new_password), user_id)
                )
                db.commit()
                error = "Password changed successfully!"
                return render_template('auth/change_password.html', user_password_hash=user_password_hash, error=error)
            else:
                error = "Incorrect old password!"
                return render_template('auth/change_password.html', user_password_hash=user_password_hash, error=error)
    
    return render_template('auth/change_password.html', user_password_hash=user_password_hash, error=error)

@bp.route('/reset_password/<int:user_id>')
def reset_password(user_id):
    # This page is only for library staff accounts
    if not g.user['library_staff']:
        raise Unauthorized
    password = default_reset_password

    db = get_db()
    db.execute(
        "UPDATE user SET user_password = ? WHERE id = ?;", 
        (generate_password_hash(password), user_id),
    )
    db.commit()
    return redirect(url_for('auth.user_settings', user_id=user_id))

