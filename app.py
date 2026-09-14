from flask import Flask, render_template, request, redirect, session , url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import random
import re
from datetime import datetime, timedelta
import razorpay


app = Flask(__name__)

app.secret_key = "handmade_blooms_secret_key"

ORDERS_FILE = "orders.json"
NOTIFICATIONS_FILE = "notifications.json"
REVIEWS_FILE = "reviews.json"
USERS_FILE = "users.json"
CONTACTS_FILE = "contacts.json"

ADMIN_PASSWORD = "HBadmin123"

# =========================================
# RAZORPAY TEST MODE
# =========================================
# Paste your Razorpay TEST Key ID and TEST Key Secret here.
# Never share the Key Secret with anyone.
RAZORPAY_KEY_ID = "rzp_test_TbY41mYXGAlvtb"
RAZORPAY_KEY_SECRET = "26rGTCXWiE51ipz4tBPZrR43"
print("KEY =", RAZORPAY_KEY_ID)
print("SECRET =", RAZORPAY_KEY_SECRET)

razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)


# =========================================
# COUPONS
# =========================================

COUPONS = {
    "BLOOMS10": {
        "type": "percent",
        "value": 10
    },
    "BLOOMS50": {
        "type": "fixed",
        "value": 50
    }
}


# =========================================
# PRODUCTS
# =========================================

PRODUCTS = [

    {
        "id": "rose",
        "name": "Rose",
        "price": 150,
        "sizes": {
            "M": 150
        },
        "image": "rose.png",
        "description": "Beautiful handmade rose."
    },

    {
        "id": "lavender",
        "name": "Lavender",
        "price": 120,
        "sizes": {
            "M": 120
        },
        "image": "lavender.png",
        "description": "Beautiful handmade lavender flower."
    },

    {
        "id": "daisy",
        "name": "Daisy",
        "price": 79,
        "sizes": {
            "M": 79,
            "L": 120
        },
        "image": "daisy.png",
        "description": "Beautiful handmade daisy flower."
    },

    {
        "id": "lotus",
        "name": "Lotus",
        "price": 110,
        "sizes": {
            "M": 110,
            "L": 160
        },
        "image": "lotus.jpeg",
        "description": "Beautiful handmade lotus flower."
    },

    {
        "id": "simple_lily",
        "name": "Simple Lily",
        "price": 79,
        "sizes": {
            "S": 79,
            "M": 120,
            "L": 160
        },
        "image": "simple_lily.png",
        "description": "Beautiful handmade simple lily."
    },

    {
        "id": "tulip",
        "name": "Tulip",
        "price": 79,
        "sizes": {
            "M": 79,
            "L": 120
        },
        "image": "tulip.jpeg",
        "description": "Beautiful handmade tulip flower."
    },

    {
        "id": "sunflower",
        "name": "Sunflower",
        "price": 100,
        "sizes": {
            "M": 100,
            "L": 150
        },
        "image": "sunflower.png",
        "description": "Bright and cheerful handmade sunflower."
    },

    {
        "id": "lily",
        "name": "Lily",
        "price": 120,
        "sizes": {
            "M": 120,
            "L": 160
        },
        "image": "lily.png",
        "description": "Elegant handmade lily."
    },

    {
        "id": "mix_shade_lily",
        "name": "Mix Shade Lily",
        "price": 120,
        "sizes": {
            "M": 120,
            "L": 160
        },
        "image": "mix_shade_lily.png",
        "description": "Beautiful handmade mix shade lily."
    }

]


# =========================================
# VALIDATION HELPERS
# =========================================

def is_valid_email(email):

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(re.match(pattern, email))


def clean_text(value, max_length):

    value = str(value or "").strip()

    if len(value) > max_length:
        value = value[:max_length]

    return value


def safe_integer(value, default=0):

    try:
        return int(value)

    except (ValueError, TypeError):

        return default


def get_logged_in_user():

    return session.get("user")


def safe_next_url(next_page):

    next_page = str(next_page or "").strip()

    if not next_page:
        return ""

    if (
        next_page.startswith("/")
        and not next_page.startswith("//")
    ):
        return next_page

    return ""


# =========================================
# USER FILE FUNCTIONS
# =========================================

def load_users():

    if not os.path.exists(USERS_FILE):
        return []

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        FileNotFoundError,
        OSError
    ):

        return []


def save_users(users):

    try:

        with open(
            USERS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                users,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError:

        return False


# =========================================
# CONTACT FILE FUNCTIONS
# =========================================

def load_contacts():

    if not os.path.exists(CONTACTS_FILE):
        return []

    try:

        with open(
            CONTACTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        FileNotFoundError,
        OSError
    ):

        return []


def save_contacts(contacts):

    try:

        with open(
            CONTACTS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                contacts,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError:

        return False


# =========================================
# ORDER FILE FUNCTIONS
# =========================================

def load_orders():

    if not os.path.exists(ORDERS_FILE):
        return []

    try:

        with open(
            ORDERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        FileNotFoundError,
        OSError
    ):

        return []


def save_orders(orders):

    try:

        with open(
            ORDERS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                orders,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError:

        return False


# =========================================
# NOTIFICATION FUNCTIONS
# =========================================

def load_notifications():

    if not os.path.exists(NOTIFICATIONS_FILE):
        return []

    try:

        with open(
            NOTIFICATIONS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        FileNotFoundError,
        OSError
    ):

        return []


def save_notifications(notifications):

    try:

        with open(
            NOTIFICATIONS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                notifications,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError:

        return False


def add_notification(
    notification_type,
    title,
    message,
    order_id
):

    notifications = load_notifications()

    notification = {

        "id": (
            "notification_" +
            str(random.randint(100000, 999999)) +
            "_" +
            str(random.randint(1000, 9999))
        ),

        "type": notification_type,

        "title": title,

        "message": message,

        "order_id": order_id,

        "date": datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        ),

        "read": False
    }

    notifications.insert(0, notification)

    notifications = notifications[:100]

    save_notifications(notifications)


# =========================================
# REVIEW FUNCTIONS
# =========================================

def load_reviews():

    if not os.path.exists(REVIEWS_FILE):
        return []

    try:

        with open(
            REVIEWS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        FileNotFoundError,
        OSError
    ):

        return []


def save_reviews(reviews):

    try:

        with open(
            REVIEWS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                reviews,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError:

        return False


def is_review_approved(review):

    return review.get("approved", True) is True


def get_product_reviews(product_id):

    all_reviews = load_reviews()

    product_reviews = []

    for review in all_reviews:

        if str(
            review.get("product_id", "")
        ) == str(product_id):

            if is_review_approved(review):

                product_reviews.append(review)

    product_reviews.reverse()

    return product_reviews


def get_product_rating(product_id):

    reviews = get_product_reviews(product_id)

    if not reviews:
        return 0, 0

    total_rating = 0
    valid_reviews = 0

    for review in reviews:

        rating = safe_integer(
            review.get("rating", 0),
            0
        )

        if 1 <= rating <= 5:

            total_rating += rating
            valid_reviews += 1

    if valid_reviews == 0:
        return 0, 0

    average_rating = round(
        total_rating / valid_reviews,
        1
    )

    return average_rating, valid_reviews


def get_all_product_ratings():

    ratings = {}

    for product in PRODUCTS:

        average_rating, review_count = (
            get_product_rating(product["id"])
        )

        ratings[product["id"]] = {
            "average": average_rating,
            "count": review_count
        }

    return ratings


# =========================================
# VERIFIED PURCHASE
# =========================================

def verify_product_purchase(
    product_id,
    order_id,
    mobile
):

    order_id = str(order_id).strip().upper()
    mobile = str(mobile).strip()

    if not order_id or not mobile:
        return False

    orders = load_orders()

    for order in orders:

        existing_order_id = str(
            order.get("order_id", "")
        ).strip().upper()

        existing_mobile = str(
            order.get("mobile", "")
        ).strip()

        if (
            existing_order_id == order_id
            and existing_mobile == mobile
        ):

            if order.get("status", "") != "Delivered":
                return False

            items = order.get("items", [])

            if not isinstance(items, list):
                return False

            for item in items:

                item_id = str(
                    item.get(
                        "product_id",
                        item.get("id", "")
                    )
                )

                if item_id == str(product_id):

                    if (
                        item_id.startswith("custom_")
                        or item_id.startswith("demand_")
                    ):
                        return False

                    return True

    return False


# =========================================
# CHECK WHETHER CUSTOMER ALREADY REVIEWED
# =========================================

def has_existing_review(
    product_id,
    order_id,
    mobile
):

    order_id = str(order_id).strip().upper()
    mobile = str(mobile).strip()

    reviews = load_reviews()

    for review in reviews:

        if (
            str(review.get("product_id", "")) ==
            str(product_id)
            and
            str(review.get("order_id", "")).strip().upper()
            == order_id
            and
            str(review.get("mobile", "")).strip()
            == mobile
        ):

            return True

    return False


# =========================================
# ORDER ID
# =========================================

def generate_order_id():

    orders = load_orders()

    existing_ids = {
        str(order.get("order_id", ""))
        for order in orders
    }

    while True:

        order_id = (
            "HB" +
            str(random.randint(100000, 999999))
        )

        if order_id not in existing_ids:
            return order_id


# =========================================
# CART COUNT
# =========================================

def get_cart_count():

    cart = session.get("cart", [])

    if not isinstance(cart, list):
        return 0

    cart_count = 0

    for item in cart:

        quantity = safe_integer(
            item.get("quantity", 0),
            0
        )

        if quantity > 0:
            cart_count += quantity

    return cart_count


# =========================================
# WISHLIST COUNT
# =========================================

def get_wishlist_count():

    wishlist = session.get("wishlist", [])

    if not isinstance(wishlist, list):
        return 0

    return len(wishlist)


# =========================================
# COUPON CALCULATION
# =========================================

def calculate_coupon_discount(product_total):

    coupon_code = session.get(
        "coupon_code",
        ""
    )

    if not coupon_code:
        return 0

    coupon_code = str(
        coupon_code
    ).upper()

    coupon = COUPONS.get(coupon_code)

    if coupon is None:
        return 0

    if coupon["type"] == "percent":

        discount = round(
            product_total *
            coupon["value"] /
            100
        )

    else:

        discount = coupon["value"]

    if discount < 0:
        discount = 0

    if discount > product_total:
        discount = product_total

    return discount


# =========================================
# HOME
# =========================================

@app.route("/")
def index():

    product_ratings = get_all_product_ratings()

    return render_template(
        "index.html",
        products=PRODUCTS,
        product_ratings=product_ratings,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


# =========================================
# PRODUCT DETAIL
# =========================================

@app.route("/product/<product_id>")
def product_detail(product_id):

    product = next(
        (
            p for p in PRODUCTS
            if p["id"] == product_id
        ),
        None
    )

    if product is None:
        return redirect("/")

    wishlist = session.get(
        "wishlist",
        []
    )

    if not isinstance(wishlist, list):
        wishlist = []

    reviews = get_product_reviews(product_id)

    average_rating, review_count = (
        get_product_rating(product_id)
    )

    return render_template(
        "product_detail.html",
        product=product,
        wishlist=wishlist,
        reviews=reviews,
        average_rating=average_rating,
        review_count=review_count,
        wishlist_count=get_wishlist_count(),
        cart_count=get_cart_count()
    )


# =========================================
# ADD REVIEW
# =========================================

@app.route(
    "/add_review/<product_id>",
    methods=["POST"]
)
def add_review(product_id):

    product = next(
        (
            p for p in PRODUCTS
            if p["id"] == product_id
        ),
        None
    )

    if product is None:
        return redirect("/")

    name = clean_text(
        request.form.get(
            "name",
            ""
        ),
        100
    )

    review_text = clean_text(
        request.form.get(
            "review",
            ""
        ),
        1000
    )

    rating = safe_integer(
        request.form.get(
            "rating",
            0
        ),
        0
    )

    order_id = clean_text(
        request.form.get(
            "order_id",
            ""
        ),
        50
    ).upper()

    mobile = clean_text(
        request.form.get(
            "mobile",
            ""
        ),
        10
    )

    if not name or len(name) < 2:
        return redirect("/product/" + product_id)

    if not review_text or len(review_text) < 3:
        return redirect("/product/" + product_id)

    if rating < 1 or rating > 5:
        return redirect("/product/" + product_id)

    if (
        not mobile.isdigit()
        or len(mobile) != 10
    ):
        return redirect("/product/" + product_id)

    if not order_id:
        return redirect("/product/" + product_id)

    verified_purchase = verify_product_purchase(
        product_id,
        order_id,
        mobile
    )

    if not verified_purchase:
        return redirect("/product/" + product_id)

    if has_existing_review(
        product_id,
        order_id,
        mobile
    ):
        return redirect("/product/" + product_id)

    reviews = load_reviews()

    review = {

        "id": (
            "review_" +
            str(random.randint(100000, 999999)) +
            "_" +
            str(random.randint(1000, 9999))
        ),

        "product_id": product_id,

        "product_name": product["name"],

        "name": name,

        "rating": rating,

        "review": review_text,

        "date": datetime.now().strftime(
            "%d-%m-%Y"
        ),

        "order_id": order_id,

        "mobile": mobile,

        "verified_purchase": True,

        "approved": False
    }

    reviews.append(review)

    save_reviews(reviews)

    add_notification(
        "new_review",
        "New Review Received ⭐",
        (
            name +
            " submitted a review for " +
            product["name"] +
            "."
        ),
        order_id
    )

    return redirect("/product/" + product_id)


# =========================================
# ADD NORMAL PRODUCT
# =========================================

@app.route(
    "/add_to_cart/<product_id>",
    methods=["GET"]
)
def add_to_cart(product_id):

    product = next(
        (
            p for p in PRODUCTS
            if p["id"] == product_id
        ),
        None
    )

    if product is None:
        return redirect("/")

    quantity = safe_integer(
        request.args.get(
            "quantity",
            1
        ),
        1
    )

    if quantity < 1:
        quantity = 1

    if quantity > 99:
        quantity = 99

    sizes = product.get(
        "sizes",
        {}
    )

    selected_size = clean_text(
        request.args.get(
            "size",
            ""
        ),
        30
    )

    if not sizes:

        selected_size = "One Size"

        selected_price = safe_integer(
            product.get(
                "price",
                0
            ),
            0
        )

    elif len(sizes) == 1:

        selected_size = next(
            iter(sizes)
        )

        selected_price = safe_integer(
            sizes[selected_size],
            0
        )

    else:

        if selected_size not in sizes:

            return redirect(
                "/product/" +
                product_id
            )

        selected_price = safe_integer(
            sizes[selected_size],
            0
        )

    color_required = (
        product_id != "lavender"
        and
        product_id != "sunflower"
    )

    selected_color = clean_text(
        request.args.get(
            "color",
            ""
        ),
        50
    )

    if color_required and not selected_color:

        return redirect(
            "/product/" +
            product_id
        )

    if not color_required:
        selected_color = ""

    size_key = (
        selected_size
        .lower()
        .replace(" ", "_")
    )

    color_key = ""

    if selected_color:

        color_key = (
            "__" +
            selected_color
            .lower()
            .replace(" ", "_")
        )

    cart_item_id = (
        product_id +
        "__" +
        size_key +
        color_key
    )

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(cart, list):
        cart = []

    found = False

    for item in cart:

        existing_cart_item_id = str(
            item.get(
                "cart_item_id",
                item.get(
                    "id",
                    ""
                )
            )
        )

        if (
            existing_cart_item_id ==
            cart_item_id
        ):

            old_quantity = safe_integer(
                item.get(
                    "quantity",
                    0
                ),
                0
            )

            item["quantity"] = min(
                old_quantity + quantity,
                99
            )

            found = True

            break

    if not found:

        item_name = product["name"]

        if len(sizes) > 1:

            item_name += (
                " - " +
                selected_size
            )

        if selected_color:

            item_name += (
                " - " +
                selected_color
            )

        cart.append({

            "id": cart_item_id,

            "product_id": product["id"],

            "cart_item_id": cart_item_id,

            "name": item_name,

            "price": selected_price,

            "image": product["image"],

            "quantity": quantity,

            "size": selected_size,

            "color": selected_color
        })

    session["cart"] = cart

    session.modified = True

    return redirect("/cart")


# =========================================
# WISHLIST
# =========================================

@app.route("/wishlist")
def wishlist():

    wishlist_ids = session.get(
        "wishlist",
        []
    )

    if not isinstance(wishlist_ids, list):
        wishlist_ids = []

    wishlist_products = []

    for product_id in wishlist_ids:

        product = next(
            (
                p for p in PRODUCTS
                if p["id"] == product_id
            ),
            None
        )

        if product is not None:
            wishlist_products.append(product)

    return render_template(
        "wishlist.html",
        wishlist_products=wishlist_products,
        wishlist_count=len(wishlist_products),
        cart_count=get_cart_count()
    )


@app.route(
    "/add_to_wishlist/<product_id>"
)
def add_to_wishlist(product_id):

    product = next(
        (
            p for p in PRODUCTS
            if p["id"] == product_id
        ),
        None
    )

    if product is None:
        return redirect("/")

    wishlist = session.get(
        "wishlist",
        []
    )

    if not isinstance(wishlist, list):
        wishlist = []

    if product_id not in wishlist:

        if len(wishlist) < 99:
            wishlist.append(product_id)

    session["wishlist"] = wishlist

    session.modified = True

    return redirect(
        request.referrer or "/"
    )


@app.route(
    "/remove_from_wishlist/<product_id>"
)
def remove_from_wishlist(product_id):

    wishlist = session.get(
        "wishlist",
        []
    )

    if not isinstance(wishlist, list):
        wishlist = []

    wishlist = [
        item
        for item in wishlist
        if str(item) != str(product_id)
    ]

    session["wishlist"] = wishlist

    session.modified = True

    return redirect(
        request.referrer or "/wishlist"
    )


@app.route(
    "/wishlist/add_to_cart/<product_id>"
)
def wishlist_add_to_cart(product_id):

    product = next(
        (
            p for p in PRODUCTS
            if p["id"] == product_id
        ),
        None
    )

    if product is None:
        return redirect("/wishlist")

    if (
        product_id != "lavender"
        and
        product_id != "sunflower"
    ):

        return redirect(
            "/product/" +
            product_id
        )

    sizes = product.get(
        "sizes",
        {}
    )

    if len(sizes) > 1:

        return redirect(
            "/product/" +
            product_id
        )

    selected_size = next(
        iter(sizes),
        "One Size"
    )

    selected_price = safe_integer(
        sizes.get(
            selected_size,
            product.get(
                "price",
                0
            )
        ),
        0
    )

    cart_item_id = (
        product_id +
        "__" +
        selected_size
        .lower()
        .replace(" ", "_")
    )

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(cart, list):
        cart = []

    found = False

    for item in cart:

        existing_cart_item_id = str(
            item.get(
                "cart_item_id",
                item.get(
                    "id",
                    ""
                )
            )
        )

        if (
            existing_cart_item_id ==
            cart_item_id
        ):

            old_quantity = safe_integer(
                item.get(
                    "quantity",
                    0
                ),
                0
            )

            item["quantity"] = min(
                old_quantity + 1,
                99
            )

            found = True

            break

    if not found:

        cart.append({

            "id": cart_item_id,

            "product_id": product["id"],

            "cart_item_id": cart_item_id,

            "name": (
                product["name"] +
                (
                    " - " +
                    selected_size
                    if len(sizes) > 1
                    else ""
                )
            ),

            "price": selected_price,

            "image": product["image"],

            "quantity": 1,

            "size": selected_size,

            "color": ""
        })

    session["cart"] = cart

    session.modified = True

    return redirect("/cart")


# =========================================
# CART
# =========================================

@app.route("/cart")
def cart():

    cart_items = session.get(
        "cart",
        []
    )

    if not isinstance(cart_items, list):

        cart_items = []

        session["cart"] = []

        session.modified = True

    total = 0

    for item in cart_items:

        price = safe_integer(
            item.get(
                "price",
                0
            ),
            0
        )

        quantity = safe_integer(
            item.get(
                "quantity",
                0
            ),
            0
        )

        if price < 0:
            price = 0

        if quantity < 0:
            quantity = 0

        total += (
            price *
            quantity
        )

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


@app.route("/increase/<item_id>")
def increase(item_id):

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(cart, list):
        cart = []

    for item in cart:

        if str(
            item.get("id")
        ) == str(item_id):

            quantity = safe_integer(
                item.get(
                    "quantity",
                    1
                ),
                1
            )

            if quantity < 99:

                item["quantity"] = (
                    quantity + 1
                )

            break

    session["cart"] = cart

    session.modified = True

    return redirect("/cart")


@app.route("/decrease/<item_id>")
def decrease(item_id):

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(cart, list):
        cart = []

    for item in cart:

        if str(
            item.get("id")
        ) == str(item_id):

            quantity = safe_integer(
                item.get(
                    "quantity",
                    1
                ),
                1
            )

            if quantity > 1:

                item["quantity"] = (
                    quantity - 1
                )

            else:

                cart.remove(item)

            break

    session["cart"] = cart

    session.modified = True

    return redirect("/cart")


@app.route("/remove/<item_id>")
def remove(item_id):

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(cart, list):
        cart = []

    cart = [
        item
        for item in cart
        if str(
            item.get("id")
        ) != str(item_id)
    ]

    session["cart"] = cart

    session.modified = True

    return redirect("/cart")


# =========================================
# CHECKOUT
# =========================================

@app.route("/checkout")
def checkout():

    cart_items = session.get(
        "cart",
        []
    )

    if not cart_items:
        return redirect("/cart")

    product_total = 0

    for item in cart_items:

        price = safe_integer(
            item.get(
                "price",
                0
            ),
            0
        )

        quantity = safe_integer(
            item.get(
                "quantity",
                0
            ),
            0
        )

        if price < 0:
            price = 0

        if quantity < 0:
            quantity = 0

        product_total += (
            price *
            quantity
        )

    coupon_code = session.get(
        "coupon_code",
        ""
    )

    discount = calculate_coupon_discount(
        product_total
    )

    coupon_error = session.pop(
        "coupon_error",
        None
    )

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        product_total=product_total,
        coupon_code=coupon_code,
        discount=discount,
        coupon_error=coupon_error,
        user=get_logged_in_user(),
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


# =========================================
# APPLY COUPON
# =========================================

@app.route(
    "/apply_coupon",
    methods=["POST"]
)
def apply_coupon():

    coupon_code = clean_text(
        request.form.get(
            "coupon_code",
            ""
        ),
        30
    ).upper()

    if not coupon_code:

        session["coupon_error"] = (
            "Please enter a coupon code."
        )

        session.pop(
            "coupon_code",
            None
        )

        return redirect("/checkout")

    if coupon_code not in COUPONS:

        session["coupon_error"] = (
            "Invalid coupon code. "
            "Please try another code."
        )

        session.pop(
            "coupon_code",
            None
        )

        return redirect("/checkout")

    session["coupon_code"] = coupon_code

    session.pop(
        "coupon_error",
        None
    )

    return redirect("/checkout")


@app.route(
    "/remove_coupon",
    methods=["POST"]
)
def remove_coupon():

    session.pop(
        "coupon_code",
        None
    )

    session.pop(
        "coupon_error",
        None
    )

    return redirect("/checkout")


# =========================================
# PLACE ORDER / CREATE RAZORPAY PAYMENT
# =========================================

@app.route(
    "/place_order",
    methods=["POST"]
)
def place_order():

    cart_items = session.get(
        "cart",
        []
    )

    if not isinstance(cart_items, list):
        cart_items = []

    if not cart_items:
        return redirect("/cart")

    name = clean_text(
        request.form.get("name", ""),
        100
    )

    email = clean_text(
        request.form.get("email", ""),
        150
    ).lower()

    mobile = clean_text(
        request.form.get("mobile", ""),
        10
    )

    address = clean_text(
        request.form.get("address", ""),
        500
    )

    city = clean_text(
        request.form.get("city", ""),
        100
    )

    state = clean_text(
        request.form.get("state", ""),
        100
    )

    pincode = clean_text(
        request.form.get("pincode", ""),
        6
    )

    if not name:
        return "Please enter your name."

    if len(name) < 2:
        return "Please enter a valid name."

    if not email:
        return "Please enter your email."

    if not is_valid_email(email):
        return "Please enter a valid email address."

    if not mobile.isdigit() or len(mobile) != 10:
        return "Invalid mobile number. Please enter exactly 10 digits."

    if not address:
        return "Please enter your address."

    if not city:
        return "Please enter your city."

    if not state:
        return "Please enter your state."

    if not pincode.isdigit() or len(pincode) != 6:
        return "Invalid pincode. Please enter exactly 6 digits."

    product_total = 0

    for item in cart_items:

        if not isinstance(item, dict):
            continue

        price = safe_integer(
            item.get("price", 0),
            0
        )

        quantity = safe_integer(
            item.get("quantity", 0),
            0
        )

        if price < 0:
            price = 0

        if quantity < 1:
            quantity = 1

        if quantity > 99:
            quantity = 99

        item["price"] = price
        item["quantity"] = quantity

        product_total += price * quantity

    if product_total <= 0:
        return "Your cart is empty or invalid. Please add a product again."

    coupon_code = str(
        session.get("coupon_code", "")
    ).upper()

    if coupon_code not in COUPONS:
        coupon_code = ""
        session.pop("coupon_code", None)

    discount = calculate_coupon_discount(product_total)

    delivery_charge = (
        0
        if city.lower() == "pali"
        else 99
    )

    final_total = (
        product_total
        - discount
        + delivery_charge
    )

    if final_total < 0:
        final_total = 0

    # Razorpay amount must be sent in paise.
    razorpay_amount = int(final_total * 100)

    if razorpay_amount <= 0:
        return "Invalid payment amount. Please try again."

    site_order_id = generate_order_id()

    try:

        razorpay_order = razorpay_client.order.create({
            "amount": razorpay_amount,
            "currency": "INR",
            "receipt": site_order_id,
            "notes": {
                "customer_name": name,
                "customer_mobile": mobile
            }
        })

    except Exception as error:

        print("Razorpay order creation error:", error)

        return "RAZORPAY ERROR: " + str(error)

    delivery_date_object = (
        datetime.now() + timedelta(days=10)
    )

    delivery_date = delivery_date_object.strftime(
        "%d-%m-%Y"
    )

    # Keep checkout data in the session until Razorpay payment is verified.
    # The actual order is NOT saved as a paid order until signature verification succeeds.
    session["pending_payment"] = {
        "site_order_id": site_order_id,
        "razorpay_order_id": razorpay_order.get("id", ""),
        "name": name,
        "email": email,
        "mobile": mobile,
        "address": address,
        "city": city,
        "state": state,
        "pincode": pincode,
        "items": cart_items,
        "product_total": product_total,
        "coupon_code": coupon_code,
        "discount": discount,
        "delivery_charge": delivery_charge,
        "final_total": final_total,
        "delivery_date": delivery_date
    }

    session.modified = True

    return render_template(
        "payment.html",
        razorpay_key_id=RAZORPAY_KEY_ID,
        razorpay_order_id=razorpay_order.get("id", ""),
        amount=razorpay_amount,
        amount_rupees=final_total,
        amount_paise=razorpay_amount,
        order_id=site_order_id,
        customer_name=name,
        customer_email=email,
        customer_mobile=mobile,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


# =========================================
# RAZORPAY PAYMENT SUCCESS / VERIFY PAYMENT
# =========================================

@app.route(
    "/payment_success",
    methods=["POST"]
)
def payment_success():

    pending_payment = session.get(
        "pending_payment"
    )

    if not isinstance(pending_payment, dict):
        return redirect("/checkout")

    razorpay_payment_id = clean_text(
        request.form.get(
            "razorpay_payment_id",
            ""
        ),
        100
    )

    razorpay_order_id = clean_text(
        request.form.get(
            "razorpay_order_id",
            ""
        ),
        100
    )

    razorpay_signature = clean_text(
        request.form.get(
            "razorpay_signature",
            ""
        ),
        200
    )

    expected_razorpay_order_id = str(
        pending_payment.get(
            "razorpay_order_id",
            ""
        )
    )

    if not razorpay_payment_id:
        return "Payment verification failed: payment ID is missing."

    if not razorpay_order_id:
        return "Payment verification failed: order ID is missing."

    if not razorpay_signature:
        return "Payment verification failed: signature is missing."

    if (
        razorpay_order_id !=
        expected_razorpay_order_id
    ):
        return "Payment verification failed: order mismatch."

    # Step 1: Verify the Checkout signature on the server.
    try:

        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

    except Exception as error:

        print("Razorpay payment verification error:", error)

        return (
            "Payment verification failed. "
            "Please do not place the order again immediately. "
            "Check the payment status first."
        )

    # Step 2: Fetch the payment from Razorpay instead of trusting only
    # the browser callback. This also lets us confirm the amount and order.
    try:

        payment = razorpay_client.payment.fetch(
            razorpay_payment_id
        )

    except Exception as error:

        print("Razorpay payment fetch error:", error)

        return (
            "Payment was received by Razorpay, but its status could not "
            "be verified right now. Please check the Razorpay payment "
            "status before placing the order again."
        )

    fetched_order_id = str(
        payment.get("order_id", "")
    )

    if fetched_order_id != razorpay_order_id:
        print(
            "Razorpay order mismatch:",
            fetched_order_id,
            razorpay_order_id
        )
        return "Payment verification failed: Razorpay order mismatch."

    expected_amount = int(
        safe_integer(
            pending_payment.get("final_total", 0),
            0
        ) * 100
    )

    fetched_amount = safe_integer(
        payment.get("amount", 0),
        0
    )

    if fetched_amount != expected_amount:
        print(
            "Razorpay amount mismatch:",
            fetched_amount,
            expected_amount
        )
        return "Payment verification failed: payment amount mismatch."

    payment_status = str(
        payment.get("status", "")
    ).lower()

    # If Razorpay has only authorised the payment, capture it before
    # marking the Handmade Blooms order as paid.
    if payment_status == "authorized":

        try:

            payment = razorpay_client.payment.capture(
                razorpay_payment_id,
                {
                    "amount": expected_amount,
                    "currency": "INR"
                }
            )

            payment_status = str(
                payment.get("status", "")
            ).lower()

        except Exception as error:

            print("Razorpay payment capture error:", error)

            return (
                "Payment is authorised but has not been captured yet. "
                "The order has NOT been marked as paid. Please check "
                "the Razorpay payment status before trying again."
            )

    # Never mark an order Paid unless Razorpay reports it as captured.
    if payment_status != "captured":

        print(
            "Razorpay payment is not captured. Status:",
            payment_status
        )

        return (
            "Payment verification is incomplete. Razorpay payment status: "
            + (payment_status or "unknown") +
            ". The order has NOT been marked as paid."
        )

    order_id = str(
        pending_payment.get(
            "site_order_id",
            ""
        )
    )

    if not order_id:
        return "Order could not be created because the order ID is missing."

    orders = load_orders()

    # Prevent duplicate order creation if the success callback is submitted twice.
    existing_order = next(
        (
            order for order in orders
            if str(
                order.get("order_id", "")
            ) == order_id
        ),
        None
    )

    if existing_order is not None:

        session["customer_mobile"] = str(
            existing_order.get("mobile", "")
        )

        session.pop(
            "pending_payment",
            None
        )

        session["cart"] = []
        session.pop("coupon_code", None)
        session.pop("coupon_error", None)
        session.modified = True

        return render_template(
            "confirmation.html",
            order=existing_order
        )

    order = {
        "order_id": order_id,
        "name": pending_payment.get("name", ""),
        "email": pending_payment.get("email", ""),
        "mobile": pending_payment.get("mobile", ""),
        "address": pending_payment.get("address", ""),
        "city": pending_payment.get("city", ""),
        "state": pending_payment.get("state", ""),
        "pincode": pending_payment.get("pincode", ""),
        "items": pending_payment.get("items", []),
        "product_total": pending_payment.get("product_total", 0),
        "coupon_code": pending_payment.get("coupon_code", ""),
        "discount": pending_payment.get("discount", 0),
        "delivery_charge": pending_payment.get("delivery_charge", 0),
        "final_total": pending_payment.get("final_total", 0),
        "total": pending_payment.get("final_total", 0),
        "status": "Pending",
        "delivery_date": pending_payment.get("delivery_date", ""),
        "delivery_time": "Delivery within 10 days",
        "order_date": datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        ),
        "payment_status": "Paid",
        "payment_method": "Razorpay",
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_signature": razorpay_signature
    }

    orders.append(order)

    if not save_orders(orders):
        return (
            "Payment was captured and verified, but the order could not be saved. "
            "Please contact Handmade Blooms with your payment ID: "
            + razorpay_payment_id
        )

    add_notification(
        "new_order",
        "New Paid Order Received 🛒",
        (
            "New paid order " +
            order_id +
            " placed by " +
            str(order.get("name", "")) +
            ". Total: ₹" +
            str(order.get("final_total", 0))
        ),
        order_id
    )

    session["customer_mobile"] = str(
        order.get("mobile", "")
    )

    session.pop(
        "pending_payment",
        None
    )

    session["cart"] = []

    session.pop(
        "coupon_code",
        None
    )

    session.pop(
        "coupon_error",
        None
    )

    session.modified = True

    return render_template(
        "confirmation.html",
        order=order
    )


# =========================================
# PAYMENT FAILED / CANCELLED
# =========================================

@app.route("/payment_failed")
def payment_failed():

    return render_template(
        "payment_failed.html",
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


# CUSTOM BOUQUET
# =========================================

@app.route("/custom_bouquet")
def custom_bouquet():

    return render_template(
        "custom_bouquet.html"
    )


@app.route("/add_custom_bouquet")
def add_custom_bouquet():

    size = clean_text(
        request.args.get(
            "size",
            "Small"
        ),
        20
    )

    if size == "Small":

        base_price = 250

    elif size == "Medium":

        base_price = 500

    elif size == "Large":

        base_price = 750

    else:

        size = "Small"

        base_price = 250

    extra_flowers = safe_integer(
        request.args.get(
            "extra_flowers",
            0
        ),
        0
    )

    if extra_flowers < 0:
        extra_flowers = 0

    if extra_flowers > 99:
        extra_flowers = 99

    message = clean_text(
        request.args.get(
            "message",
            ""
        ),
        2000
    )

    price = (
        base_price +
        extra_flowers * 50
    )

    custom_id = (
        "custom_" +
        str(
            random.randint(
                100000,
                999999
            )
        )
    )

    item = {

        "id": custom_id,

        "name": (
            "Custom " +
            size +
            " Bouquet"
        ),

        "price": price,

        "image": "",

        "quantity": 1,

        "message": message,

        "extra_flowers": extra_flowers
    }

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(
        cart,
        list
    ):

        cart = []

    cart.append(item)

    session["cart"] = cart

    session.modified = True

    return redirect("/cart")


# =========================================
# FLOWER AS PER DEMAND
# =========================================

@app.route("/flower_demand")
def flower_demand():

    return render_template(
        "flower_demand.html"
    )


@app.route("/add_flower_demand")
def add_flower_demand():

    flower_name = clean_text(
        request.args.get(
            "flower_name",
            ""
        ),
        200
    )

    demand_details = clean_text(
        request.args.get(
            "demand_details",
            ""
        ),
        3000
    )

    if not flower_name:

        flower_name = "Any Flower"

    if not demand_details:

        demand_details = (
            "Customer has not added "
            "extra details."
        )

    demand_id = (
        "demand_" +
        str(
            random.randint(
                100000,
                999999
            )
        )
    )

    message = (
        "FLOWER AS PER DEMAND | "
        "Flower: " +
        flower_name +
        " | Demand/Design: " +
        demand_details
    )

    item = {

        "id": demand_id,

        "name": "Flower As Per Demand",

        "price": 180,

        "image": "",

        "quantity": 1,

        "message": message,

        "flower_name": flower_name,

        "demand_details": demand_details
    }

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(
        cart,
        list
    ):

        cart = []

    cart.append(item)

    session["cart"] = cart

    session.modified = True

    return redirect("/cart")


# =========================================
# TRACK ORDER
# =========================================

@app.route(
    "/track_order",
    methods=["GET", "POST"]
)
def track_order():

    order = None

    error = None

    searched_mobile = ""

    if request.method == "POST":

        order_id = clean_text(
            request.form.get(
                "order_id",
                ""
            ),
            50
        ).upper()

        mobile = clean_text(
            request.form.get(
                "mobile",
                ""
            ),
            10
        )

        searched_mobile = mobile

        if (
            not mobile.isdigit()
            or len(mobile) != 10
        ):

            error = (
                "Please enter a valid "
                "10-digit mobile number."
            )

        elif not order_id:

            error = (
                "Please enter your Order ID."
            )

        else:

            orders = load_orders()

            for existing_order in orders:

                existing_order_id = str(
                    existing_order.get(
                        "order_id",
                        ""
                    )
                ).upper()

                existing_mobile = str(
                    existing_order.get(
                        "mobile",
                        ""
                    )
                )

                if (
                    existing_order_id == order_id
                    and
                    existing_mobile == mobile
                ):

                    order = existing_order

                    break

            if order is None:

                error = (
                    "Order not found. "
                    "Please check your Order ID "
                    "and mobile number."
                )

    return render_template(
        "order_tracking.html",
        order=order,
        error=error,
        searched_mobile=searched_mobile
    )


# =========================================
# MY ORDERS
# =========================================

@app.route(
    "/my_orders",
    methods=["GET", "POST"]
)
def my_orders():

    orders = []

    error = None

    mobile = ""

    if request.method == "GET":

        mobile = session.get(
            "customer_mobile",
            ""
        )

    if request.method == "POST":

        mobile = clean_text(
            request.form.get(
                "mobile",
                ""
            ),
            10
        )

    if mobile:

        if (
            not mobile.isdigit()
            or len(mobile) != 10
        ):

            error = (
                "Please enter a valid "
                "10-digit mobile number."
            )

        else:

            all_orders = load_orders()

            orders = [
                order
                for order in all_orders
                if str(
                    order.get(
                        "mobile",
                        ""
                    )
                ) == mobile
            ]

            orders.reverse()

            if not orders:

                error = (
                    "No orders found "
                    "for this mobile number."
                )

    return render_template(
        "my_orders.html",
        orders=orders,
        error=error,
        mobile=mobile
    )


# =========================================
# CANCEL ORDER
# =========================================

@app.route(
    "/cancel_order/<order_id>",
    methods=["POST"]
)
def cancel_order(order_id):

    mobile = clean_text(
        request.form.get(
            "mobile",
            ""
        ),
        10
    )

    if (
        not mobile.isdigit()
        or len(mobile) != 10
    ):

        return redirect(
            "/my_orders"
        )

    orders = load_orders()

    for order in orders:

        if (
            str(
                order.get(
                    "order_id",
                    ""
                )
            ) == str(order_id)

            and

            str(
                order.get(
                    "mobile",
                    ""
                )
            ) == mobile
        ):

            status = order.get(
                "status",
                "Pending"
            )

            items = order.get(
                "items",
                []
            )

            if not isinstance(
                items,
                list
            ):

                items = []

            has_custom = any(
                str(
                    item.get(
                        "id",
                        ""
                    )
                ).startswith(
                    "custom_"
                )
                for item in items
            )

            has_demand = any(
                str(
                    item.get(
                        "id",
                        ""
                    )
                ).startswith(
                    "demand_"
                )
                for item in items
            )

            if (
                has_custom
                or
                has_demand
            ):

                session[
                    "customer_mobile"
                ] = mobile

                return redirect(
                    "/my_orders"
                )

            if status not in [
                "Pending",
                "Processing"
            ]:

                session[
                    "customer_mobile"
                ] = mobile

                return redirect(
                    "/my_orders"
                )

            order["status"] = "Cancelled"

            save_orders(orders)

            add_notification(
                "cancelled_order",
                "Order Cancelled ❌",
                (
                    "Customer " +
                    order.get(
                        "name",
                        ""
                    ) +
                    " cancelled order " +
                    order_id +
                    "."
                ),
                order_id
            )

            session[
                "customer_mobile"
            ] = mobile

            return redirect(
                "/my_orders"
            )

    return redirect(
        "/my_orders"
    )


# =========================================
# CONTACT US
# =========================================

@app.route(
    "/contact",
    methods=["GET", "POST"]
)
def contact():


    error = None
    success = None

    user = get_logged_in_user()

    name = ""
    email = ""
    mobile = ""

    if user:

        name = str(
            user.get(
                "name",
                ""
            )
        )

        email = str(
            user.get(
                "email",
                ""
            )
        )

        mobile = str(
            user.get(
                "mobile",
                ""
            )
        )

    if request.method == "POST":

        name = clean_text(
            request.form.get(
                "name",
                ""
            ),
            100
        )

        email = clean_text(
            request.form.get(
                "email",
                ""
            ),
            150
        ).lower()

        mobile = clean_text(
            request.form.get(
                "mobile",
                ""
            ),
            10
        )

        message = clean_text(
            request.form.get(
                "message",
                ""
            ),
            2000
        )

        if not name or len(name) < 2:

            error = (
                "Please enter a valid name."
            )

        elif not is_valid_email(email):

            error = (
                "Please enter a valid email address."
            )

        elif (
            not mobile.isdigit()
            or len(mobile) != 10
        ):

            error = (
                "Please enter a valid "
                "10-digit mobile number."
            )

        elif not message or len(message) < 3:

            error = (
                "Please enter your message."
            )

        else:

            contacts = load_contacts()

            contact_id = (
                "contact_" +
                str(
                    random.randint(
                        100000,
                        999999
                    )
                ) +
                "_" +
                str(
                    random.randint(
                        1000,
                        9999
                    )
                )
            )

            contact_message = {

                "id": contact_id,

                "name": name,

                "email": email,

                "mobile": mobile,

                "message": message,

                "date": datetime.now().strftime(
                    "%d-%m-%Y %I:%M %p"
                ),

                "read": False
            }

            contacts.insert(
                0,
                contact_message
            )

            contacts = contacts[:200]

            if save_contacts(contacts):

                add_notification(
                    "contact_message",
                    "New Contact Message 📞",
                    (
                        name +
                        " sent a new contact message."
                    ),
                    ""
                )

                success = (
                    "Your message has been sent "
                    "successfully. 🌸"
                )

                name = ""
                email = ""
                mobile = ""

            else:

                error = (
                    "Message could not be sent. "
                    "Please try again."
                )

    return render_template(
        "contact.html",
        user=user,
        name=name,
        email=email,
        mobile=mobile,
        error=error,
        success=success,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )
# =========================================
# ABOUT US
# =========================================

@app.route("/about")
def about():

    return render_template(
        "about.html",
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )
@app.route("/faq")
def faq():

    return render_template(
        "faq.html",
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )

# =========================================
# CUSTOMER SIGNUP
# =========================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    error = None

    next_page = safe_next_url(
        request.args.get(
            "next",
            ""
        )
    )

    if request.method == "POST":

        name = clean_text(
            request.form.get(
                "name",
                ""
            ),
            100
        )

        email = clean_text(
            request.form.get(
                "email",
                ""
            ),
            150
        ).lower()

        mobile = clean_text(
            request.form.get(
                "mobile",
                ""
            ),
            10
        )

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        next_page = safe_next_url(
            request.form.get(
                "next",
                ""
            )
        )

        if not name or len(name) < 2:

            error = "Please enter a valid name."

        elif not is_valid_email(email):

            error = "Please enter a valid email address."

        elif (
            not mobile.isdigit()
            or len(mobile) != 10
        ):

            error = (
                "Please enter a valid "
                "10-digit mobile number."
            )

        elif len(password) < 6:

            error = (
                "Password must be at least "
                "6 characters."
            )

        elif password != confirm_password:

            error = "Passwords do not match."

        else:

            users = load_users()

            email_exists = any(
                str(
                    user.get(
                        "email",
                        ""
                    )
                ).lower() == email
                for user in users
            )

            if email_exists:

                error = (
                    "An account with this email "
                    "already exists."
                )

            else:

                mobile_exists = any(
                    str(
                        user.get(
                            "mobile",
                            ""
                        )
                    ) == mobile
                    for user in users
                )

                if mobile_exists:

                    error = (
                        "An account with this mobile "
                        "number already exists."
                    )

                else:

                    user_id = (
                        "user_" +
                        str(
                            random.randint(
                                100000,
                                999999
                            )
                        )
                    )

                    user = {

                        "id": user_id,

                        "name": name,

                        "email": email,

                        "mobile": mobile,

                        "password": (
                            generate_password_hash(
                                password
                            )
                        ),

                        "created_at": (
                            datetime.now().strftime(
                                "%d-%m-%Y %I:%M %p"
                            )
                        )
                    }

                    users.append(user)

                    if save_users(users):

                        session["customer_id"] = user_id

                        session["user"] = {
                            "id": user_id,
                            "name": name,
                            "email": email,
                            "mobile": mobile
                        }

                        session[
                            "customer_mobile"
                        ] = mobile

                        session.modified = True

                        if next_page:
                            return redirect(next_page)

                        return redirect("/account")

                    else:

                        error = (
                            "Account could not be created. "
                            "Please try again."
                        )

    return render_template(
        "signup.html",
        error=error,
        next=next_page
    )


# =========================================
# CUSTOMER LOGIN
# =========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    error = None

    next_page = safe_next_url(
        request.args.get(
            "next",
            ""
        )
    )

    if request.method == "POST":

        email = clean_text(
            request.form.get(
                "email",
                ""
            ),
            150
        ).lower()

        password = request.form.get(
            "password",
            ""
        )

        next_page = safe_next_url(
            request.form.get(
                "next",
                ""
            )
        )

        if not email:

            error = "Please enter your email."

        elif not password:

            error = "Please enter your password."

        else:

            users = load_users()

            found_user = None

            for user in users:

                if (
                    str(
                        user.get(
                            "email",
                            ""
                        )
                    ).lower() == email
                ):

                    found_user = user

                    break

            if found_user is None:

                error = (
                    "Invalid email or password."
                )

            else:

                stored_password = str(
                    found_user.get(
                        "password",
                        ""
                    )
                )

                password_valid = False

                try:

                    password_valid = (
                        check_password_hash(
                            stored_password,
                            password
                        )
                    )

                except ValueError:

                    password_valid = False

                if not password_valid:

                    error = (
                        "Invalid email or password."
                    )

                else:

                    user_id = str(
                        found_user.get(
                            "id",
                            ""
                        )
                    )

                    name = str(
                        found_user.get(
                            "name",
                            ""
                        )
                    )

                    mobile = str(
                        found_user.get(
                            "mobile",
                            ""
                        )
                    )

                    session["customer_id"] = user_id

                    session["user"] = {
                        "id": user_id,
                        "name": name,
                        "email": email,
                        "mobile": mobile
                    }

                    session[
                        "customer_mobile"
                    ] = mobile

                    session.modified = True

                    if next_page:
                        return redirect(next_page)

                    return redirect("/account")

    return render_template(
        "login.html",
        error=error,
        next=next_page
    )


# =========================================
# CUSTOMER ACCOUNT
# =========================================

@app.route("/account")
def account():

    user = session.get("user")

    if not session.get("customer_id"):

        return redirect(
            "/login?next=/account"
        )

    return render_template(
        "account.html",
        user=user,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


# =========================================
# CUSTOMER LOGOUT
# =========================================

@app.route("/logout")
def logout():

    session.pop(
        "customer_id",
        None
    )

    session.pop(
        "user",
        None
    )

    session.pop(
        "customer_mobile",
        None
    )

    return redirect("/")


# =========================================
# ADMIN LOGIN
# =========================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    error = None

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        if password == ADMIN_PASSWORD:

            session[
                "admin_logged_in"
            ] = True

            return redirect(
                "/admin/orders"
            )

        error = "Wrong password."

    return render_template(
        "admin_login.html",
        error=error
    )


# =========================================
# ADMIN LOGOUT
# =========================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        "/admin/login"
    )


# =========================================
# ADMIN ORDERS
# =========================================

@app.route(
    "/admin/orders",
    methods=["GET", "POST"]
)
def admin_orders():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            "/admin/login"
        )

    orders = load_orders()

    if request.method == "POST":

        order_id = clean_text(
            request.form.get(
                "order_id",
                ""
            ),
            50
        )

        status = clean_text(
            request.form.get(
                "status",
                ""
            ),
            30
        )

        delivery_date = clean_text(
            request.form.get(
                "delivery_date",
                ""
            ),
            20
        )

        valid_statuses = [
            "Pending",
            "Processing",
            "Shipped",
            "Delivered",
            "Cancelled"
        ]

        for order in orders:

            if (
                str(
                    order.get(
                        "order_id",
                        ""
                    )
                ) == order_id
            ):

                if status in valid_statuses:

                    order["status"] = status

                if delivery_date:

                    try:

                        date_object = (
                            datetime.strptime(
                                delivery_date,
                                "%Y-%m-%d"
                            )
                        )

                        minimum_date = (
                            datetime.now()
                            + timedelta(
                                days=10
                            )
                        )

                        if (
                            date_object.date()
                            >= minimum_date.date()
                        ):

                            order[
                                "delivery_date"
                            ] = (
                                date_object.strftime(
                                    "%d-%m-%Y"
                                )
                            )

                    except ValueError:

                        pass

                else:

                    order[
                        "delivery_date"
                    ] = ""

                break

        save_orders(orders)

        return redirect(
            "/admin/orders"
        )

    notifications = load_notifications()

    unread_notifications = [
        notification
        for notification in notifications
        if not notification.get(
            "read",
            False
        )
    ]

    unread_count = len(
        unread_notifications
    )

    reviews = load_reviews()

    reviews.reverse()

    pending_reviews = [
        review
        for review in reviews
        if not review.get(
            "approved",
            True
        )
    ]

    pending_review_count = len(
        pending_reviews
    )

    return render_template(
        "admin_orders.html",
        orders=orders[::-1],
        notifications=notifications,
        unread_count=unread_count,
        reviews=reviews,
        pending_review_count=pending_review_count
    )


# =========================================
# APPROVE REVIEW
# =========================================

@app.route(
    "/admin/reviews/approve/<review_id>",
    methods=["POST"]
)
def approve_review(review_id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            "/admin/login"
        )

    reviews = load_reviews()

    for review in reviews:

        if str(
            review.get(
                "id",
                ""
            )
        ) == str(review_id):

            review[
                "approved"
            ] = True

            break

    save_reviews(reviews)

    return redirect(
        "/admin/orders"
    )


# =========================================
# DELETE REVIEW
# =========================================

@app.route(
    "/admin/reviews/delete/<review_id>",
    methods=["POST"]
)
def delete_review(review_id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            "/admin/login"
        )

    reviews = load_reviews()

    reviews = [
        review
        for review in reviews
        if str(
            review.get(
                "id",
                ""
            )
        ) != str(review_id)
    ]

    save_reviews(reviews)

    return redirect(
        "/admin/orders"
    )


# =========================================
# MARK NOTIFICATIONS READ
# =========================================

@app.route(
    "/admin/notifications/read",
    methods=["POST"]
)
def mark_notifications_read():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            "/admin/login"
        )

    notifications = load_notifications()

    for notification in notifications:

        notification[
            "read"
        ] = True

    save_notifications(
        notifications
    )

    return redirect(
        "/admin/orders"
    )


# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )