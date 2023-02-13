import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
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

from passlib.hash import pbkdf2_sha256

from .models import User


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

    login_manager.init_app(app)

    logger.debug("Initialized authentication")


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
        special_characters = '!@#$%&()-_[]{};:"./<>?'

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif password != password2:
            error = 'Passwords do not match.'
            """
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
        """
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
