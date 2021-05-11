
'''
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user
'''
#from .. import movie_client
from ..forms import AddToCartForm, RemoveFromCartForm, PlaceOrderForm
from ..models import User, Item
from ..utils import current_time


# New Python Package
import requests



# 3rd-party packages
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Blueprint,
    session,
    g,
)
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from flask_app import db
from werkzeug.utils import secure_filename

# stdlib
from datetime import datetime
import io
import base64
'''
# local
from . import bcrypt, movie_client
from .forms import (
    SearchForm,
    MovieReviewForm,
    RegistrationForm,
    LoginForm,
    UpdateUsernameForm,
)
from .models import User, Review, load_user
from .utils import current_time
'''
store = Blueprint("store", __name__)





""" ************ View functions ************ """


@store.route("/", methods=["GET", "POST"])
def index():
    '''
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)
    @movies.route("/user/<username>")
    '''
    return render_template("index.html")



@store.route("/about")
def about():
    return render_template("about.html")

@store.route("/setup")
def setup():
    '''
    item1 = Item (
        item_id="1",
        title = "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
        price = "109.99",
        description = "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
        image = "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
        status = 0
        count = "1"

    )
    item1.save()


    item2 = Item (
        item_id="1",
        title = "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
        price = "109.99",
        description = "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve, your everyday",
        image = "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
        status = 0
        count = "1"

    )
    item1.save()
    
    '''
    
    Item.drop_collection()
    
    res = requests.get("https://fakestoreapi.com/products")
    res_json = res.json()
    for i in res_json:
        item = Item (
            item_id = str(i["id"]),
            title = i["title"],
            price = str(i["price"]),
            description = i["description"],
            image = i["image"],
            status = 0,
            count = "1"

        )
        item.save()
    
    
    return redirect(url_for("store.shop"))
    
    #return "saved"


@store.route("/shop")
def shop():
    '''
    r = requests.get("https://fakestoreapi.com/products")
    
    t = r.text
    r_json = r.json()
    print("Size of request")
    print(len(r_json))
    '''

    items_available = Item.objects(status=0)

    #return render_template("shop.html", info=t)
    return render_template("shop.html", items_for_sale=items_available)#, products=t)



# similar to movie detail
@store.route("/items/<id>", methods=["GET", "POST"])
def item_detail(id):
    '''
    render a item template depending on the item_id
    -Display all info about item
    -
    '''
    i = Item.objects.get(item_id=id)
    
    form = AddToCartForm()
    if form.validate_on_submit():
        i_id = Item.objects(item_id=id).get()
        i_id.update(added_to_cart_by=current_user._get_current_object())
        i_id.save()
        


    return render_template("item_detail.html", item=i, form=form)


@store.route("/user/cart", methods=["GET", "POST"])
def user_cart():
    form = RemoveFromCartForm()
    form2 = PlaceOrderForm()

    items_added_to_cart = Item.objects(added_to_cart_by=current_user._get_current_object())

    return render_template("cart.html", items_in_cart=items_added_to_cart, form=form, form2=form2)



#@store.route("/user/<username>/cart")
#def user_cart(username):
@store.route("/user/cart/remove-all", methods=["GET", "POST"])
def user_cart_remove():

    
    items_added_to_cart = Item.objects(added_to_cart_by=current_user._get_current_object())

    form = RemoveFromCartForm()
    
    if form.validate_on_submit():
        i_atc = Item.objects(added_to_cart_by=current_user._get_current_object())
        for i in i_atc:
            i.update(added_to_cart_by=None)
            i.save()

    form2 = PlaceOrderForm()

    return render_template("cart.html", items_in_cart=items_added_to_cart, form=form, form2=form2)




@store.route("/user/cart/place-order", methods=["GET", "POST"])
def user_cart_place_order():
    '''
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    return render_template("user_detail.html", username=username, reviews=reviews)
    '''
    items_added_to_cart = Item.objects(added_to_cart_by=current_user._get_current_object())

    form = RemoveFromCartForm()

    form2 = PlaceOrderForm()
    if form2.validate_on_submit():
        #i_atc = Item.objects(added_to_cart_by=current_user._get_current_object())
        #i_atc = Item.objects(status=0)
        for i in items_added_to_cart:
            i.update(status=1)
            i.update(ordered_by=current_user._get_current_object())
            i.update(count="0")
            i.update(added_to_cart_by=None)


        

        # Redirect to order page
        return redirect(url_for("store.user_order_confirmation"))
    

    return render_template("cart.html", items_in_cart=items_added_to_cart, form=form, form2=form2)




@store.route("/user/order-confirmation", methods=["GET", "POST"])
def user_order_confirmation():

    # Add the email order feature
    #i_ordered = Item.objects(ordered_by=current_user._get_current_object())
    #i_ordered = Item.objects(ordered_by=current_user._get_current_object())

    return render_template("order_confirmation.html")


@store.route("/user/orders", methods=["GET", "POST"])
def user_orders():

    # Add the email order feature
    #i_ordered = Item.objects(ordered_by=current_user._get_current_object())
    i_ordered = Item.objects(ordered_by=current_user._get_current_object())

    return render_template("orders.html", i_ordered=i_ordered)









'''
@movies.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = movie_client.search(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("movies.index"))

    return render_template("query.html", results=results)


@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    try:
        result = movie_client.retrieve_movie_by_id(movie_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("users.login"))

    form = MovieReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.title,
        )
        review.save()

        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)

    return render_template(
        "movie_detail.html", form=form, movie=result, reviews=reviews
    )


@movies.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    return render_template("user_detail.html", username=username, reviews=reviews)

'''

