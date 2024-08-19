from flask import Blueprint, render_template


bp = Blueprint('error_handlers', __name__)

@bp.app_errorhandler(400)
def bad_request(error):
    error_str = "HTTP Error 400: Bad Request"
    return render_template('error_page.html', error_str=error_str), 400

@bp.app_errorhandler(401)
def unauthorized(error):
    error_str = "HTTP Error 401: Unauthorized"
    return render_template('error_page.html', error_str=error_str), 401

@bp.app_errorhandler(403)
def access_forbidden(error):
    error_str = "HTTP Error 403: Access Forbidden"
    return render_template('error_page.html', error_str=error_str), 403

@bp.app_errorhandler(404)
def page_not_found(error):
    error_str = "HTTP Error 404: Page Not Found"
    return render_template('error_page.html', error_str=error_str), 404

@bp.app_errorhandler(500)
def internal_server_error(error):
    error_str = "HTTP Error 500: Internal Server Error"
    return render_template('error_page.html', error_str=error_str), 500

@bp.app_errorhandler(502)
def bad_gateway(error):
    error_str = "HTTP Error 502: Bad Gateway"
    return render_template('error_page.html', error_str=error_str), 502

@bp.app_errorhandler(503)
def service_unavailable(error):
    error_str = "HTTP Error 503: Service Unavailable"
    return render_template('error_page.html', error_str=error_str), 503
