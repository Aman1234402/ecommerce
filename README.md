# Ecommerce

A Django e-commerce project featuring a product catalog, interactive product pages, email-verified accounts, and a persistent shopping cart.

## Features

- Browse a product catalog with live search, category filters, and price/name sorting.
- Save products as favorites in the browser and filter the catalog to favorites.
- View product galleries with thumbnails, next/previous navigation, and an enlarged image viewer.
- Choose product sizes and see the adjusted price update on the product page.
- Create an account, verify an email address, and sign in.
- Add products and selected variants to a persistent cart; update quantities, remove items, and see the subtotal.
- Manage products, product images, categories, and variants using Django Admin.

## Requirements

- Python 3.13 or newer
- pip

This project uses Django 6.1.2. The local `env` virtual environment is not required if you create a new one.

## Setup

Open a terminal in the project directory and run:

```powershell
py -3.13 -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "Django==6.1.2" "Pillow==12.3.0"
```

If the virtual environment is already present, activate it and continue with the migrations:

```powershell
.\env\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Email configuration

Registration sends an account-verification email. Configure these environment variables before registering:

```text
EMAIL_HOST_USER=your-sender@example.com
EMAIL_HOST_PASSWORD=your-email-app-password
```

The project reads values from the process environment or a local `.env` file in the project root. Never commit real email credentials. Without email settings, the site displays an email-configuration error when someone submits registration.

## Admin and sample catalog

Create an administrator account with:

```powershell
python manage.py createsuperuser
```

Sign in at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) to add or update categories, products, product images, and size or color variants. Product images can be added inline while editing a product.

The SQLite database and product records are local to this project. When setting up a clean checkout, migrate the database and add catalog data through Admin if a populated database is not included.

## Run tests

```powershell
python manage.py test
```

## Main project areas

| Path | Responsibility |
| --- | --- |
| `accounts/` | User accounts, email activation, and cart |
| `products/` | Products, categories, variants, and product details |
| `home/` | Product catalog, search, and category filtering |
| `templates/` | Django HTML templates |
| `public/static/` | Stylesheets, JavaScript, and static/media assets |
| `ecomm/settings.py` | Django project settings |
