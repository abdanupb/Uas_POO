from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = "adanpedia-secret-key"

BASE_URL = "https://dummyjson.com/products"
CATEGORY_URL = "https://dummyjson.com/products/categories"


def get_cart_count():
    return len(session.get("cart", []))


@app.route("/")
def index():
    query = request.args.get("q")
    category = request.args.get("category")

    categories = requests.get(CATEGORY_URL).json()

    if category:
        products = requests.get(f"{BASE_URL}/category/{category}").json()["products"]
    elif query:
        products = requests.get(f"{BASE_URL}/search?q={query}").json()["products"]
    else:
        products = requests.get(BASE_URL).json()["products"]

    return render_template(
        "index.html",
        products=products,
        categories=categories,
        selected_category=category,
        cart_count=len(session.get("cart", []))
    )





@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    cart = session.get("cart", [])
    cart.append(product_id)
    session["cart"] = cart
    return redirect(request.referrer or url_for("index"))


@app.route("/product/<int:product_id>")
def detail(product_id):
    product = requests.get(f"{BASE_URL}/{product_id}").json()
    cart = session.get("cart", [])
    return render_template(
    "detail.html",
    product=product,
    cart_count=get_cart_count()
)



@app.route("/checkout/<int:product_id>")
def checkout(product_id):
    product = requests.get(f"{BASE_URL}/{product_id}").json()
    cart = session.get("cart", [])
    return render_template("checkout.html", product=product, cart_count=len(cart))


@app.route("/payment/<int:product_id>", methods=["POST"])
def payment(product_id):
    product = requests.get(f"{BASE_URL}/{product_id}").json()
    cart = session.get("cart", [])
    return render_template("payment.html", product=product, cart_count=len(cart))


@app.route("/success", methods=["POST"])
def success():
    session.pop("cart", None)
    return render_template("success.html", cart_count=0)


@app.route("/cart")
def cart():
    cart_ids = session.get("cart", [])
    products = []
    total = 0

    for pid in cart_ids:
        product = requests.get(f"{BASE_URL}/{pid}").json()
        products.append(product)
        total += product["price"]

    return render_template(
        "cart.html",
        products=products,
        total=total,
        cart_count=len(cart_ids)
    )

@app.route("/remove-from-cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", [])
    if product_id in cart:
        cart.remove(product_id)
    session["cart"] = cart
    return redirect(url_for("cart"))




if __name__ == "__main__":
    app.run(debug=True)
