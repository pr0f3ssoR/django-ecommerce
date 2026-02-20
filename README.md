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

## 🔥 Key Features

- ✔ Dynamic product variants  
- ✔ Flexible attribute system  
- ✔ Optimized database queries  
- ✔ File cleanup using Django signals  
- ✔ Clean relational modeling  
- ✔ Scalable structure  

---

## ⚙️ Tech Stack

- Python
- Django
- SQLite (default)
- Django ORM
- Django Signals

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

---

## 🔥 Upcoming Features

-  Authentication
-  Adding items to cart 
-  Generating Orders  
-  Adding reviews and comments to products
-  Customer Support: Chat live with agent (django channels)
    
