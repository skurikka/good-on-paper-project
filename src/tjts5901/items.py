from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime, timedelta


from .auth import login_required
from .models import Bid, Item

import logging
from typing import Optional

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

bp = Blueprint('items', __name__)

logger = logging.getLogger(__name__)

MIN_BID_INCREMENT = 1

def get_item(id):
    try:
        item = Item.objects.get_or_404(id=id)
    except Exception as exc:
        print("Error getting item:", exc)
        abort(404)

    if item.seller == current_user:
        return item
    
    abort(403)

def get_winning_bid(item: Item) -> Optional[Bid]:
    """
    Return the (currently) winning bid for the given item.

    If there are no bids, or the item is not yet closed, return None.

    :param item: The item to get the winning bid for.
    :return: The winning bid, or None.
    """

    winning_bid = None
    try:
        winning_bid = Bid.objects(item=item) \
            .filter(created_at__lt=item.closes_at) \
            .order_by('-amount') \
            .first()
    except Exception as exc:
        logger.warning("Error getting winning bid: %s", exc, exc_info=True, extra={
            'item_id': item.id,
        })

    return winning_bid


def get_item_price(item: Item) -> int:
    """
    Return the current price of the given item.

    If there are no bids, return the starting bid.

    :param item: The item to get the price for.
    :return: The current price.
    """

    winning_bid = get_winning_bid(item)
    if winning_bid:
        return winning_bid.amount + MIN_BID_INCREMENT
    else:
        return item.starting_bid



@bp.route("/", defaults={'page': 1})
@bp.route("/items/<int:page>")
def index(page=1):
    """
    Index page for items on sale.

    Lists only items that are currently sale, with pagination.
    """

    # Function used on propaedeutic
    #items = Item.objects.all()

    # Fetch items that are on sale currently, and paginate
    # See: http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/custom_queryset.html
    items = Item.objects.filter(closes_at__gt=datetime.utcnow()) \
        .order_by('-closes_at') \
        .paginate(page=page, per_page=9)

    return render_template('items/index.html', items=items)


@bp.route('/sell', methods=('GET', 'POST'))
@login_required
def sell():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        starting_bid = int(request.form['starting_bid'])
        error = None

        if not title:
            error = 'Title is required.'
        if not starting_bid or starting_bid < 1:
            error = 'Starting bid must be greater than 0.'

        if error is None:
            try:
                item = Item(
                    title=title,
                    description=description,
                    starting_bid=starting_bid,
                    seller=current_user,
                    closes_at=datetime.utcnow() + timedelta(days=1)

                )
                item.save()
            except Exception as exc:
                error = f"Error creating item: {exc!s}"
            else:
                return redirect(url_for('items.index'))

            print(error)
            flash(error, 'error')

    return render_template('items/sell.html')

@bp.route('/item/<id>')
def view(id):
    """
    Item view page.

    Displays the item details, and a form to place a bid.
    """

    item = Item.objects.get_or_404(id=id)

    # Set the minumum price for the bid form from the current winning bid
    winning_bid = get_winning_bid(item)
    min_bid = get_item_price(item)
    bid_history = Bid.objects.filter(item = id).order_by('-created_at')

    if item.closes_at < datetime.utcnow() and winning_bid.bidder == current_user:
        flash("Congratulations! You won the auction!")
    elif item.closes_at < datetime.utcnow() + timedelta(hours=1):
        # Dark pattern to show enticing message to user

        flash("This item is closing soon! Act now! Now! Now!")

    return render_template('items/view.html', item=item, min_bid=min_bid, winning_bid=winning_bid.amount, bid_history=bid_history)




@bp.route('/item/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    item = get_item(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        try:
            item.title = title
            item.description = description
            item.save()
        except Exception as exc:
            error = f"Error updating item: {exc!s}"
        else:
            flash("Item updated successfully!", 'success')
            return redirect(url_for('items.index'))

        print(error)
        flash(error, 'error')

    return render_template('items/update.html', item=item)

@bp.route('/item/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    item = get_item(id)
    try:
        item.delete()
    except Exception as exc:
        error = f"Error deleting item: {exc!s}"
        print(error)
        flash(error, 'error')
    else:
        flash("Item deleted successfully!", 'success')
    return redirect(url_for('items.index'))

@bp.route('/item/<id>/bid', methods=('POST',))
@login_required
def bid(id):
    """
    Bid on an item.

    If the bid is valid, create a new bid and redirect to the item view page.
    Otherwise, display an error message and redirect back to the item view page.

    :param id: The id of the item to bid on.
    :return: A redirect to the item view page.
    """

    item = Item.objects.get_or_404(id=id)
    min_amount = get_item_price(item)
    amount = int(request.form['amount'])

    if amount < min_amount:
        flash(f"Bid must be at least {min_amount}")
        return redirect(url_for('items.view', id=id))

    if item.closes_at < datetime.utcnow():
        flash("This item is no longer on sale.")
        return redirect(url_for('items.view', id=id))

    try:
        # Notice: if you have integrated the flask-login extension, use current_user
        # instead of g.user
        bid = Bid(
            item=item,
            bidder=current_user,
            amount=amount,
        )
        bid.save()
    except Exception as exc:
        flash(f"Error placing bid: {exc!s}", 'error')
    else:
        flash("Bid placed successfully!", 'success')

    return redirect(url_for('items.view', id=id))
