from pathlib import Path
import shutil
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(".")
OUT = ROOT / "docs"

if OUT.exists():
    shutil.rmtree(OUT)

OUT.mkdir(parents=True, exist_ok=True)
(OUT / ".nojekyll").write_text("", encoding="utf-8")

if Path("static").exists():
    shutil.copytree("static", OUT / "static")

def url_for(endpoint, **values):
    if endpoint == "static":
        return "static/" + values.get("filename", "")

    routes = {
        "index": "index.html",
        "products": "products.html",
        "product_detail": "product_detail.html",
        "login": "login.html",
        "register": "register.html",
        "logout": "index.html",
        "cart": "cart.html",
        "checkout": "checkout.html",
        "my_orders": "orders.html",
        "order_detail": "orders.html",
        "delivery_login": "login.html",
        "admin_login": "login.html",
    }

    if endpoint.startswith("api_") or endpoint in {
        "add_to_cart",
        "get_cart",
        "update_cart",
        "remove_from_cart",
        "create_order",
    }:
        return "#"

    return routes.get(endpoint, "#")

def get_flashed_messages(with_categories=False):
    return []

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

env.globals["url_for"] = url_for
env.globals["session"] = {}
env.globals["get_flashed_messages"] = get_flashed_messages

sample_products = [
    {
        "ProductID": 1,
        "ProductName": "Elegant Embroidered Saree",
        "Category": "Saree",
        "Price": 2450.00,
        "Quantity": 12,
        "Demand": 25,
        "Rating": 4.8,
        "Embroidery": "Hand Embroidery",
        "Description": "Premium saree with elegant embroidery and soft comfortable fabric.",
        "ImageURL": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=900&q=80",
    },
    {
        "ProductID": 2,
        "ProductName": "Classic Men's Panjabi",
        "Category": "Men's Wear",
        "Price": 1850.00,
        "Quantity": 18,
        "Demand": 20,
        "Rating": 4.6,
        "Embroidery": "Simple Work",
        "Description": "Classic festive panjabi with a clean modern cut.",
        "ImageURL": "https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&w=900&q=80",
    },
    {
        "ProductID": 3,
        "ProductName": "Women's Fashion Kurti",
        "Category": "Women's Wear",
        "Price": 1250.00,
        "Quantity": 22,
        "Demand": 30,
        "Rating": 4.7,
        "Embroidery": "Printed Design",
        "Description": "Stylish kurti for daily wear and casual outings.",
        "ImageURL": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=80",
    },
]

pages = {
    "index.html": ("index.html", {}),
    "products.html": (
        "products.html",
        {
            "products": sample_products,
            "categories": ["Saree", "Men's Wear", "Women's Wear"],
            "selected_category": "",
            "search_term": "",
        },
    ),
    "product_detail.html": (
        "product_detail.html",
        {
            "product": sample_products[0],
            "reviews": [],
        },
    ),
    "login.html": ("login.html", {"error": None}),
    "register.html": ("register.html", {}),
}

def fix_static_html(html):
    html = html.replace('href="/static/', 'href="static/')
    html = html.replace("href='/static/", "href='static/")
    html = html.replace('src="/static/', 'src="static/')
    html = html.replace("src='/static/", "src='static/")
    html = html.replace('action="/', 'action="#')
    html = re.sub(r'href="/([^"]*)"', r'href="\1.html"', html)
    html = html.replace('href=".html"', 'href="index.html"')
    html = html.replace('href="products.html.html"', 'href="products.html"')
    html = html.replace('href="login.html.html"', 'href="login.html"')
    html = html.replace('href="register.html.html"', 'href="register.html"')
    html = html.replace('href="cart.html.html"', 'href="cart.html"')
    html = html.replace('href="checkout.html.html"', 'href="checkout.html"')
    html = html.replace('href="orders.html.html"', 'href="orders.html"')
    html = html.replace("fetch('/api/", "fetch('#")
    html = html.replace('fetch("/api/', 'fetch("#')
    return html

for output_name, (template_name, context) in pages.items():
    template = env.get_template(template_name)
    html = template.render(**context)
    html = fix_static_html(html)
    (OUT / output_name).write_text(html, encoding="utf-8")

# Also copy the same homepage to root, in case GitHub Pages is set to root.
shutil.copyfile(OUT / "index.html", ROOT / "index.html")

print("Exported actual Fashion Mart frontend to docs/")
