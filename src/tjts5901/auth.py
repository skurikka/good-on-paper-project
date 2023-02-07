import functools

from passlib.hash import pbkdf2_sha256

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from mongoengine import errors

from .models import User


bp = Blueprint('auth', __name__, url_prefix='/auth')

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
        terms = request.form.get('terms', False)

        error = None

        if not email:
            error = 'Error: Email is required.'
        elif not password:
            error = 'Error: Password is required.'
        elif password != password2:
            error = 'Error: Passwords do not match.'
        elif not terms:
            error = 'Error: You must agree to the terms.'

        if error is None:
            try:
                user = User(
                    email = email,
                    password = pbkdf2_sha256.encrypt(password)
                )

                user.save()

            # TODO better error messages?
            except Exception as exc:
                error = f"Error creating user: {exc!s}"
            else:
                return redirect(url_for("auth.login"))

        print("Could not register user:", error)
        flash(error)

    return render_template('auth/register.html')


@bp.route("/login")
def login():
    """
    Login page.

    """
    return render_template('auth/login.html')

@bp.route("/logout")
def logout() -> None:
    """
    Logout page.

    """