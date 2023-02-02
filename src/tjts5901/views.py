"""
Basic views for Application
===========================
"""

from flask import Blueprint, render_template, send_from_directory

# Main blueprint.
bp = Blueprint('views', __name__)

# Blueprint for documentation.
docs_bp = Blueprint('docs', __name__)

@bp.route("/")
def index() -> str:
    """
    Index page.

    """

    # Render template file. Template file is using Jinja2 syntax, and can be passed an arbitrary number
    # of arguments to be used in the template. The template file is located in the templates directory.
    html = render_template("index.html.j2", title="TJTS5901 Example. It's changed nowqqqq.")
    return html

@bp.route("/test")
def test_item_adding() -> None:
    """
    Test item adding
    """
    from .models import Item, User
    
    #New user
    user = User()
    user.save()
    
    #New item
    item = Item()
    item.title ="Test item"
    item.description = "Test item description"
    item.starting_bid = 100
    item.seller = user
    item.save()
    
    return "OK"
