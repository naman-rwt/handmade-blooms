from flask import Flask, render_template, request, redirect, session
import json
import os
import random
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = "handmade_blooms_secret_key"

ORDERS_FILE = "orders.json"
NOTIFICATIONS_FILE = "notifications.json"
REVIEWS_FILE = "reviews.json"
USERS_FILE = "users.json"

ADMIN_PASSWORD = "HBadmin123"


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
        "id": "sunflower",
        "name": "Sunflower",
        "price": 150,
        "image": "sunflower.png",
        "description": "Bright and cheerful handmade sunflower, crafted with care."
    },
    {
        "id": "lily",
        "name": "Lily",
        "price": 150,
        "image": "lily.png",
        "description": "Elegant handmade lily, perfect for gifting and special moments."
    },
    {
        "id": "mix_brown_lily",
        "name": "Mix Brown Lily",
        "price": 160,
        "image": "mix_brown_lily.png",
        "description": "A beautiful handmade mix brown lily with a warm, elegant look."
    },
    {
        "id": "rose",
        "name": "Rose",
        "price": 140,
        "image": "rose.png",
        "description": "Beautiful handmade rose, crafted with love for your special moments."
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


# =========================================
# USER / CUSTOMER ACCOUNT FUNCTIONS
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


def generate_customer_id():

    users = load_users()

    existing_ids = {
        str(user.get("customer_id", ""))
        for user in users
    }

    while True:

        customer_id = (
            "HBUSER" +
            str(random.randint(100000, 999999))
        )

        if customer_id not in existing_ids:
            return customer_id


def get_logged_in_user():

    customer_id = session.get(
        "customer_id",
        ""
    )

    if not customer_id:
        return None

    users = load_users()

    for user in users:

        if str(
            user.get("customer_id", "")
        ) == str(customer_id):

            return user

    return None


def is_customer_logged_in():

    return get_logged_in_user() is not None


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
                    item.get("id", "")
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
# CUSTOMER ACCOUNT - SIGN UP
# =========================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if is_customer_logged_in():
        return redirect("/account")

    error = None

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

            email_exists = False
            mobile_exists = False

            for user in users:

                if str(
                    user.get("email", "")
                ).lower() == email:

                    email_exists = True

                if str(
                    user.get("mobile", "")
                ) == mobile:

                    mobile_exists = True

            if email_exists:

                error = (
                    "An account with this "
                    "email already exists."
                )

            elif mobile_exists:

                error = (
                    "An account with this "
                    "mobile number already exists."
                )

            else:

                customer_id = generate_customer_id()

                new_user = {

                    "customer_id": customer_id,

                    "name": name,

                    "email": email,

                    "mobile": mobile,

                    "password": generate_password_hash(
                        password
                    ),

                    "created_at": datetime.now().strftime(
                        "%d-%m-%Y %I:%M %p"
                    )
                }

                users.append(new_user)

                if save_users(users):

                    session["customer_id"] = customer_id
                    session["customer_mobile"] = mobile

                    session.modified = True

                    return redirect("/account")

                error = (
                    "Account could not be created. "
                    "Please try again."
                )

    return render_template(
        "signup.html",
        error=error,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


# =========================================
# CUSTOMER ACCOUNT - LOGIN
# =========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if is_customer_logged_in():
        return redirect("/account")

    error = None

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

        if not is_valid_email(email):

            error = (
                "Please enter a valid "
                "email address."
            )

        elif not password:

            error = "Please enter your password."

        else:

            users = load_users()

            found_user = None

            for user in users:

                if str(
                    user.get("email", "")
                ).lower() == email:

                    found_user = user
                    break

            if found_user is None:

                error = (
                    "No account found "
                    "with this email."
                )

            else:

                stored_password = str(
                    found_user.get(
                        "password",
                        ""
                    )
                )

                if check_password_hash(
                    stored_password,
                    password
                ):

                    session["customer_id"] = (
                        found_user.get(
                            "customer_id",
                            ""
                        )
                    )

                    session["customer_mobile"] = (
                        found_user.get(
                            "mobile",
                            ""
                        )
                    )

                    session.modified = True

                    return redirect("/account")

                error = "Incorrect password."

    return render_template(
        "login.html",
        error=error,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


# =========================================
# CUSTOMER ACCOUNT - LOGOUT
# =========================================

@app.route("/logout")
def logout():

    session.pop(
        "customer_id",
        None
    )

    session.pop(
        "customer_mobile",
        None
    )

    return redirect("/")


# =========================================
# CUSTOMER ACCOUNT PAGE
# =========================================

@app.route("/account")
def account():

    user = get_logged_in_user()

    if user is None:
        return redirect("/login")

    customer_id = user.get(
        "customer_id",
        ""
    )

    all_orders = load_orders()

    customer_orders = []

    for order in all_orders:

        if str(
            order.get(
                "customer_id",
                ""
            )
        ) == str(customer_id):

            customer_orders.append(order)

        elif (
            not order.get("customer_id")
            and
            str(
                order.get(
                    "mobile",
                    ""
                )
            ) == str(
                user.get(
                    "mobile",
                    ""
                )
            )
        ):

            customer_orders.append(order)

    customer_orders.reverse()

    return render_template(
        "account.html",
        user=user,
        orders=customer_orders,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


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
        request.form.get("name", ""),
        100
    )

    review_text = clean_text(
        request.form.get("review", ""),
        1000
    )

    rating = safe_integer(
        request.form.get("rating", 0),
        0
    )

    order_id = clean_text(
        request.form.get("order_id", ""),
        50
    ).upper()

    mobile = clean_text(
        request.form.get("mobile", ""),
        10
    )

    if not name or len(name) < 2:

        return redirect(
            "/product/" +
            product_id
        )

    if not review_text or len(review_text) < 3:

        return redirect(
            "/product/" +
            product_id
        )

    if rating < 1 or rating > 5:

        return redirect(
            "/product/" +
            product_id
        )

    if (
        not mobile.isdigit()
        or len(mobile) != 10
    ):

        return redirect(
            "/product/" +
            product_id
        )

    if not order_id:

        return redirect(
            "/product/" +
            product_id
        )

    verified_purchase = verify_product_purchase(
        product_id,
        order_id,
        mobile
    )

    if not verified_purchase:

        return redirect(
            "/product/" +
            product_id
        )

    if has_existing_review(
        product_id,
        order_id,
        mobile
    ):

        return redirect(
            "/product/" +
            product_id
        )

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

    return redirect(
        "/product/" +
        product_id
    )


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
        request.args.get("quantity", 1),
        1
    )

    if quantity < 1:
        quantity = 1

    if quantity > 99:
        quantity = 99

    cart = session.get("cart", [])

    if not isinstance(cart, list):
        cart = []

    found = False

    for item in cart:

        if item.get("id") == product_id:

            old_quantity = safe_integer(
                item.get("quantity", 0),
                0
            )

            item["quantity"] = min(
                old_quantity + quantity,
                99
            )

            found = True
            break

    if not found:

        cart.append(
            {
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "image": product["image"],
                "quantity": quantity
            }
        )

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

    cart = session.get(
        "cart",
        []
    )

    if not isinstance(cart, list):
        cart = []

    found = False

    for item in cart:

        if item.get("id") == product_id:

            old_quantity = safe_integer(
                item.get("quantity", 0),
                0
            )

            item["quantity"] = min(
                old_quantity + 1,
                99
            )

            found = True
            break

    if not found:

        cart.append(
            {
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "image": product["image"],
                "quantity": 1
            }
        )

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
            item.get("price", 0),
            0
        )

        quantity = safe_integer(
            item.get("quantity", 0),
            0
        )

        if price < 0:
            price = 0

        if quantity < 0:
            quantity = 0

        total += price * quantity

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cart_count=get_cart_count(),
        wishlist_count=get_wishlist_count()
    )


@app.route("/increase/<item_id>")
def increase(item_id):

    cart = session.get("cart", [])

    if not isinstance(cart, list):
        cart = []

    for item in cart:

        if str(item.get("id")) == str(item_id):

            quantity = safe_integer(
                item.get("quantity", 1),
                1
            )

            if quantity < 99:
                item["quantity"] = quantity + 1

            break

    session["cart"] = cart
    session.modified = True

    return redirect("/cart")


@app.route("/decrease/<item_id>")
def decrease(item_id):

    cart = session.get("cart", [])

    if not isinstance(cart, list):
        cart = []

    for item in cart:

        if str(item.get("id")) == str(item_id):

            quantity = safe_integer(
                item.get("quantity", 1),
                1
            )

            if quantity > 1:
                item["quantity"] = quantity - 1

            else:
                cart.remove(item)

            break

    session["cart"] = cart
    session.modified = True

    return redirect("/cart")


@app.route("/remove/<item_id>")
def remove(item_id):

    cart = session.get("cart", [])

    if not isinstance(cart, list):
        cart = []

    cart = [
        item
        for item in cart
        if str(item.get("id")) != str(item_id)
    ]

    session["cart"] = cart
    session.modified = True

    return redirect("/cart")


# =========================================
# CHECKOUT
# =========================================

@app.route("/checkout")
def checkout():

    cart_items = session.get("cart", [])

    if not cart_items:
        return redirect("/cart")

    product_total = 0

    for item in cart_items:

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

        if quantity < 0:
            quantity = 0

        product_total += price * quantity

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

    user = get_logged_in_user()

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        product_total=product_total,
        coupon_code=coupon_code,
        discount=discount,
        coupon_error=coupon_error,
        user=user,
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
# PLACE ORDER
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
    )

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

    if (
        not mobile.isdigit()
        or len(mobile) != 10
    ):
        return (
            "Invalid mobile number. "
            "Please enter exactly 10 digits."
        )

    if not address:
        return "Please enter your address."

    if not city:
        return "Please enter your city."

    if not state:
        return "Please enter your state."

    if (
        not pincode.isdigit()
        or len(pincode) != 6
    ):
        return (
            "Invalid pincode. "
            "Please enter exactly 6 digits."
        )

    product_total = 0

    for item in cart_items:

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

        return (
            "Your cart is empty or invalid. "
            "Please add a product again."
        )

    coupon_code = session.get(
        "coupon_code",
        ""
    )

    discount = calculate_coupon_discount(
        product_total
    )

    if coupon_code and coupon_code not in COUPONS:

        coupon_code = ""
        discount = 0

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

    delivery_date_object = (
        datetime.now()
        + timedelta(days=10)
    )

    delivery_date = (
        delivery_date_object.strftime(
            "%d-%m-%Y"
        )
    )

    order_id = generate_order_id()

    logged_in_user = get_logged_in_user()

    customer_id = ""

    if logged_in_user:

        customer_id = logged_in_user.get(
            "customer_id",
            ""
        )

    order = {

        "order_id": order_id,

        "customer_id": customer_id,

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

        "total": final_total,

        "status": "Pending",

        "delivery_date": delivery_date,

        "delivery_time": "Delivery within 10 days",

        "order_date": datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )
    }

    orders = load_orders()

    orders.append(order)

    save_orders(orders)

    add_notification(
        "new_order",
        "New Order Received 🛒",
        (
            "New order " +
            order_id +
            " placed by " +
            name +
            ". Total: ₹" +
            str(final_total)
        ),
        order_id
    )

    session["customer_mobile"] = mobile

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
        str(random.randint(100000, 999999))
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

    if not isinstance(cart, list):
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
        str(random.randint(100000, 999999))
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

    if not isinstance(cart, list):
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
                    and existing_mobile == mobile
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

    logged_in_user = get_logged_in_user()

    if logged_in_user:

        customer_id = logged_in_user.get(
            "customer_id",
            ""
        )

        all_orders = load_orders()

        orders = [
            order
            for order in all_orders
            if str(
                order.get(
                    "customer_id",
                    ""
                )
            ) == str(customer_id)
            or (
                not order.get("customer_id")
                and
                str(
                    order.get(
                        "mobile",
                        ""
                    )
                ) == str(
                    logged_in_user.get(
                        "mobile",
                        ""
                    )
                )
            )
        ]

        orders.reverse()

    elif request.method == "POST":

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

    else:

        mobile = session.get(
            "customer_mobile",
            ""
        )

        if mobile:

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
        return redirect("/my_orders")

    orders = load_orders()

    logged_in_user = get_logged_in_user()

    customer_id = ""

    if logged_in_user:

        customer_id = logged_in_user.get(
            "customer_id",
            ""
        )

    for order in orders:

        same_order = (
            str(
                order.get(
                    "order_id",
                    ""
                )
            ) == str(order_id)
        )

        same_mobile = (
            str(
                order.get(
                    "mobile",
                    ""
                )
            ) == mobile
        )

        same_customer = (
            customer_id
            and
            str(
                order.get(
                    "customer_id",
                    ""
                )
            ) == str(customer_id)
        )

        if (
            same_order
            and
            same_mobile
            and
            (
                same_customer
                or not order.get("customer_id")
            )
        ):

            status = order.get(
                "status",
                "Pending"
            )

            items = order.get(
                "items",
                []
            )

            if not isinstance(items, list):
                items = []

            has_custom = any(
                str(
                    item.get(
                        "id",
                        ""
                    )
                ).startswith("custom_")
                for item in items
            )

            has_demand = any(
                str(
                    item.get(
                        "id",
                        ""
                    )
                ).startswith("demand_")
                for item in items
            )

            if has_custom or has_demand:

                session["customer_mobile"] = mobile

                return redirect("/my_orders")

            if status not in [
                "Pending",
                "Processing"
            ]:

                session["customer_mobile"] = mobile

                return redirect("/my_orders")

            order["status"] = "Cancelled"

            save_orders(orders)

            add_notification(
                "cancelled_order",
                "Order Cancelled ❌",
                (
                    "Customer " +
                    order.get("name", "") +
                    " cancelled order " +
                    order_id +
                    "."
                ),
                order_id
            )

            session["customer_mobile"] = mobile

            return redirect("/my_orders")

    return redirect("/my_orders")


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

            session["admin_logged_in"] = True

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

                        date_object = datetime.strptime(
                            delivery_date,
                            "%Y-%m-%d"
                        )

                        minimum_date = (
                            datetime.now()
                            + timedelta(days=10)
                        )

                        if (
                            date_object.date()
                            >= minimum_date.date()
                        ):

                            order["delivery_date"] = (
                                date_object.strftime(
                                    "%d-%m-%Y"
                                )
                            )

                    except ValueError:
                        pass

                else:

                    order["delivery_date"] = ""

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
        if not review.get("approved", True)
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
            review.get("id", "")
        ) == str(review_id):

            review["approved"] = True
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
            review.get("id", "")
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
        notification["read"] = True

    save_notifications(notifications)

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