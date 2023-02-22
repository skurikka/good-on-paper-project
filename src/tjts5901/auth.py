import logging
import re

from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_babel import _


from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, abort
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from sentry_sdk import set_user


from mongoengine import DoesNotExist
from mongoengine.queryset.visitor import Q

from passlib.hash import pbkdf2_sha256

from pyisemail import is_email
from email_validator import validate_email, EmailNotValidError

from .models import AccessToken, User, Item


bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)


def init_auth(app):
    """
    Integrate authentication into the application.
    """
    app.register_blueprint(bp)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.user_loader(load_logged_in_user)

    app.config['AUTH_HEADER_NAME'] = 'Authorization'
    login_manager.request_loader(load_user_from_request)

    login_manager.init_app(app)

    logger.debug("Initialized authentication")

def load_user_from_request(request):
    """
    Load a user from the request.

    This function is used by Flask-Login to load a user from the request.
    """
    api_key = request.headers.get("Authorization")

    if api_key:
        api_key = api_key.replace("Bearer ", "", 1)
        try:
            token = AccessToken.objects.get(token=api_key)
            if token.expires and token.expires < datetime.utcnow():
                logger.warning("Token expired: %s", api_key)
                return None
            # User is authenticated

            token.last_used_at = datetime.utcnow()
            token.save()
            logger.debug("User authenticated via token: %r", token.user.email, extra={
                "user": token.user.email,
                "user_id": str(token.user.id),
                "token": token.token,
            })
            return token.user
        except DoesNotExist:
            logger.error("Token not found: %s", api_key)

    return None

def load_logged_in_user(user_id):
    """
    Load a user from the database, given the user's id.
    """
    try:
        user = User.objects.get(id=user_id)
        set_user({"id": str(user.id), "email": user.email})

    except DoesNotExist:
        logger.error("User not found: %s", user_id)
        return None

    return user

def get_user_by_email(email: str) -> User:
    """
    Get a user from the database, given the user's email.

    If the email is 'me', then the current user is returned.

    :param email: The email of the user to get.
    """

    if email is None:
        abort(404)

    if email == "me" and current_user.is_authenticated:
        email = current_user.email

    try:
        user = User.objects.get_or_404(email=email)
    except DoesNotExist:
        logger.error("User not found: %s", email)
        abort(404)

    return user


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    User registeration page.

    """
    if request.method == 'POST':
        print("Registering user")
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['conf-password']
        birthday = request.form.get('birthday', False)
        terms = request.form.get('terms', False)

        error = None
        bool_result_with_dns = is_email(email, check_dns=True)
        is_new_account = True # False for login pages

        try:
            validation = validate_email(email, check_deliverability=is_new_account)
            email = validation.email
        except EmailNotValidError as error_message:
            error = str(error_message)

        special_characters = '!@#$%&()-_[]{};:"./<>?'

        if not bool_result_with_dns:
            error = 'E-mail is not valid'
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif password != password2:
            error = 'Passwords do not match.'
        elif len(password) < 7 :
            error = 'Password must be atleast 7 characters long'
        elif len(password) > 30 :
            error = 'Password must be equals or shorter than 30 characters'
        elif not re.search("[a-z]", password):
            error = 'Password must be between letters [a-z]'
        elif not re.search("[A-Z]", password):
            error = 'Password must contain one uppercase letter'
        elif not re.search("[0-9]", password):
            error = 'Password must contain one number'
        elif not any(map(lambda x: x in password, special_characters)):
            error = 'Password must contain atleast one special character: ' + special_characters
        elif not terms:
            error = 'You must agree to the terms.'
     
        if not birthday:
            error = 'Day of birth is required.'
        else:
            date = datetime.strptime(birthday, '%Y-%m-%d')
            today = datetime.now()
            past_date = today - relativedelta(years=18)

            if date > past_date:
                error = 'You have to be 18 years old to register.'

        if error is None:
            try:
                user = User(
                    email=email,
                    password=pbkdf2_sha256.hash(password),
                    birthday=birthday
                )

                user.save()

            # TODO better error messages?
            except Exception as exc:
                error = f"Error creating user: {exc!s}"
            else:
                flash("Registration successful", 'success')
                return redirect(url_for("auth.login"))

        print("Could not register user:", error)
        flash(error, 'error')

    return render_template('auth/register.html')


@bp.route("/login", methods=('GET', 'POST'))
def login():
    """
    Login page.

    """
    print("Entered login")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        user = None
        print("requested email:", email)
        print("requested password:", password)
        try:
            user = User.objects.get(email=email)
        except DoesNotExist:
            error = 'Incorrect email.'

        if user is None:
            error = 'Incorrect email.'
        elif not pbkdf2_sha256.verify(password, user['password']):
            error = 'Incorrect password.'

        if error is None:
            remember_me = bool(request.form.get("remember-me", False))
            if login_user(user, remember=remember_me):

                flash(f"Hello {email}, You have been logged in.", 'success')

                next = request.args.get('next')
                # Better check that the user actually clicked on a relative link
                # or else they could redirect you to a malicious website!
                if next is None or not next.startswith('/'):
                    next = url_for('items.index')

                return redirect(next)
            else:
                error = "Error logging in."

        logger.info("Error logging user in: %r: Error: %s", email, error)
        flash(error, 'error')
    return render_template('auth/login.html')


@bp.route("/logout")
@login_required
def logout():
    """
    Log out the current user.

    Also removes the "remember me" cookie.
    """
    logout_user()
    flash("You have been logged out.", 'success')
    return redirect(url_for('auth.login'))

@bp.route('/profile/<email>')
@login_required
def profile(email):
    """
    Show the user's profile page for the given email.

    If the email is 'me', then the current user's profile is shown.
    """
    if email == 'me':
        email = current_user.email

    user: User = User.objects.get_or_404(email=email)

    # List the items user has created
    items = Item.objects(seller=user).all()

    return render_template('auth/profile.html', user=user, items=items)

@bp.route('/profile/<email>/token', methods=('GET', 'POST'), defaults={'email': 'me'})
@login_required
def user_access_tokens(email):
    """
    Show the user's tokens page for the given email.
    """

    user: User = get_user_by_email(email)
     # Fetch all the user tokens that are active or have no expire date
    tokens = AccessToken.objects(Q(expires__gte=datetime.now()) | Q(expires=None), user=user).all()

    token = None
    if request.method == 'POST':
        try:
            name = request.form['name']

            if expires := request.form.get('expires'):
                expires = datetime.fromisoformat(expires)
            else:
                expires = None


            token = AccessToken(
                user=user,
                name=name,
                expires=expires,
            )
            token.save()
        except KeyError as exc:
            logger.debug("Missing required field: %s", exc)
            flash(_("Required field missing"), 'error')
        except Exception as exc:
            logger.exception("Error creating token: %s", exc)
            flash(_("Error creating token: %s") % exc, 'error')
        else:
            flash(_("Created token: %s") % token.name, 'success')

    return render_template('auth/tokens.html', user=user, tokens=tokens, token=token)


@bp.route('/profile/<email>/token/<id>', methods=('POST',))
def delete_user_access_token(email, id):
    """
    Delete an access token.
    """
    user = get_user_by_email(email)
    token = AccessToken.objects.get_or_404(id=id)

    if token.user != user:
        logger.warning("User %s tried to delete token %s", user.email, token.name, extra={
            "user": user.email,
            "token": str(token.id),
            "token_user": token.user.email,
        })
        abort(403)

    token.delete()

    flash(f"Deleted token {token.name}")
    return redirect(url_for('auth.user_access_tokens'))
