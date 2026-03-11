## ⚠️ Note

This project is primarily built to **practice backend development skills**.  
The frontend may **not be fully optimized** for user experience or performance.

---

# 🛒 Django eCommerce Project

A feature-rich **Django-based eCommerce backend** focused on handling:

- Products  
- Product Variants  
- Variant Attributes & Values  
- Product & Variant Images  
- Optimized ORM Queries  
- Relational Data Management
- Custom User Model & Custom Authentication Backend So That The User Can Login Using Email Or Username
- Cart Session For Both Anonymous & Authenticated Users
- Generating Orders for Anonymous & Authenticated Users
- Stripe SandBox Api Integration

This project is designed to practice **real-world backend architecture**, database relationships, and performance optimization using Django ORM.

---

## 🚀 Project Overview

This eCommerce system allows:

- Creating products  
- Managing multiple variants per product (e.g., Size, Color)  
- Handling dynamic attributes and attribute values  
- Attaching images to both products and variants  
- Efficient querying using `select_related()` and `prefetch_related()`  
- Clean relational structure using `ForeignKey` and `ManyToMany` relationships
- Handle Cart Session Anonymous & Authenticated Users
- User Can Login Using Email Or Username
- Orders Can Be Generated For Both Anonymous & Authenticated Users

## 🔥 Key Features

- ✔ Dynamic product variants  
- ✔ Flexible attribute system  
- ✔ Optimized database queries  
- ✔ File cleanup using Django signals  
- ✔ Clean relational modeling  
- ✔ Scalable structure
- ✔ Stripe Api Integration To Accept Payments From Users

---

## ⚙️ Tech Stack

- Python
- Django
- SQLite (default)
- Django ORM
- Django Signals
- Stripe (for accepting payments from users)

---

## 🧠 Query Optimization

The project uses:

- `select_related()` for ForeignKey optimization
- `prefetch_related()` for ManyToMany relationships
- Bulk operations where possible
- Controlled object creation to reduce unnecessary queries

---

## 📂 URL Endpoints

Below is the list of available routes and what they do:

| URL | Method | Description |
|-----|--------|------------|
| `/products/` | GET | Display all products with pagination |
| `/products/create-product/` | GET/POST | Create proudct with dynamic variants, each variant can have dynamic attribute and values (e.g Color: Black, Size: Full Size) and images. |
| `products/update-product/<productId:int>` | GET/POST | Update product, variants, attributes and images. |
| `products/product-view/<productId:int>` | GET | Display product, it's variants, attributes and images. The regular user will see this kind of content of product. |
| `products/delete-product/<productId:int>` | POST | Delete product, it's variants, attrbiutes and all images linked to that product. |
| '/register/' | GET/POST | Register users |
| '/login/' | GET/POST | Login user |
| '/logout/' | GET | Logout user|
| '/cart/' | GET | Display all products added to cart |
| '/add-to-cart/' | POST | Add the product to cart, both anonymouse & authenticated users can add products to cart, anonymouse user uses django session to store cart info |
| '/delete-from-cart/' | POST | Delete product from your cart |
| '/check-out/' | POST | Checkout page to accept payment using stripe, you must use stripe api in order for this url to work. Check "Stripe Api Integration" section for how to use stripe api in this project |
| '/tracking/' | GET | Track your order by entering order id which was given when the order was generated |

---

## 💲 Stripe Api Integration

In Order To Accept Payments In Stripe SandBox, You Must Create .env File In Project Folder And Define Variables "stripe_publick_key" And "stripe_screte_key". These Both Keys Can Acquired By Creating An Account On Stripe Website For Free. You Can Search "stripe testing cards" To Get SandBox Working Cards Or Use The Below One For Successful Paymeny

| Brand | Number | CVC | Date |
|----|--------------|---|---|
| 'Visa' | 4242 4242 4242 4242 | Any 3 Digits | Any Future Date |
