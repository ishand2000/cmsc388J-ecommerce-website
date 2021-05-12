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

store = Blueprint("store", __name__)




@store.route("/", methods=["GET", "POST"])
def index():

    return render_template("index.html")



@store.route("/about")
def about():
    return render_template("about.html")

@store.route("/setup")
def setup():
    
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
    
    


@store.route("/shop")
def shop():

    items_available = Item.objects(status=0)


    return render_template("shop.html", items_for_sale=items_available)




@store.route("/items/<id>", methods=["GET", "POST"])
def item_detail(id):

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

    items_added_to_cart = Item.objects(added_to_cart_by=current_user._get_current_object())

    form = RemoveFromCartForm()

    form2 = PlaceOrderForm()
    if form2.validate_on_submit():
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
    
    return render_template("order_confirmation.html")


@store.route("/user/orders", methods=["GET", "POST"])
def user_orders():
    i_ordered = Item.objects(ordered_by=current_user._get_current_object())

    return render_template("orders.html", i_ordered=i_ordered)


