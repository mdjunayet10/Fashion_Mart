# 🛍️ Fashion Mart 

A full-stack web application for managing a modern fashion retail store, built with Flask (Python) and MySQL.

## 📋 Overview

Fashion Mart Management System is a comprehensive digital platform that automates core retail operations including:
- **Product Management** - Browse, search, and filter fashion products
- **Order Processing** - Complete shopping cart and checkout functionality
- **Customer Management** - Registration, authentication, and profile management
- **Inventory Tracking** - Real-time stock management
- **Review System** - Customer reviews and product ratings

## ✨ Implemented Features

### 1. Product View Feature ✅
- **Product Catalog**: Browse all available products with images, prices, and details
- **Search & Filter**: Search by product name and filter by category
- **Product Details**: View detailed product information including:
  - Product name, category, and description
  - Price and stock availability
  - Customer ratings and reviews
  - Embroidery type and special features
- **Product Cards**: Responsive grid layout with hover effects
- **Stock Management**: Real-time stock availability display

### 2. Order Management Feature ✅
- **Shopping Cart**: 
  - Add/remove products
  - Update quantities
  - Real-time cart total calculation with delivery charge
  - Session-based cart storage
- **Checkout Process**:
  - Order summary with item breakdown
  - Fixed ৳100 delivery charge
  - Multiple payment methods (Cash on Delivery, Online Payment, Bank Transfer)
  - Order confirmation with payment status
  - Automatic inventory updates
- **Order History**:
  - View all past orders
  - Track order and delivery status
  - Payment status tracking (for COD orders)
  - Detailed order information
- **Order Tracking**:
  - Order status monitoring
  - Delivery status updates
  - Payment status for Cash on Delivery
  - Order details with item breakdown

### 3. Payment Status Tracking ✅
- **Cash on Delivery Orders**:
  - Payment status: Pending → Paid
  - Delivery man confirms cash receipt
  - Two-step completion process (delivery + payment)
- **Online Payment/Bank Transfer**:
  - Auto-completion on delivery
  - Single-step completion
  - Payment status auto-marked as "Paid"

### 4. Delivery Management ✅
- **Delivery Dashboard**:
  - View assigned orders
  - Mark orders as delivered
  - Confirm cash received (COD only)
  - Real-time status updates
- **Smart Status Management**:
  - Button state changes (Mark as Delivered → ✓ Done)
  - Conditional payment confirmation
  - Auto-complete for pre-paid orders

### 5. Delivery Charge System ✅
- **Fixed Delivery Charge**: ৳100.00 on all orders
- **Transparent Pricing**: Shows subtotal, delivery charge, and total
- **Cart Display**: Delivery charge visible in cart summary
- **Checkout Breakdown**: Itemized pricing at checkout
- **Order Confirmation**: Complete price breakdown on confirmation page

## 🛠️ Technologies Used

- **Backend**: Python 3.x, Flask 3.0
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Additional Libraries**: Flask-MySQLdb, Flask-CORS, python-dotenv

## 📁 Project Structure

```
Fashion mart/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── database/
│   ├── schema.sql             # Database schema and sample data
│   └── db_config.py           # Database configuration
├── static/
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   └── js/
│       └── main.js            # JavaScript utilities
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Homepage
    ├── login.html             # Login page
    ├── register.html          # Registration page
    ├── products.html          # Product catalog
    ├── product_detail.html    # Product details
    ├── cart.html              # Shopping cart
    ├── checkout.html          # Checkout page
    ├── orders.html            # Order history
    └── order_detail.html      # Order details
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

### Step 1: Clone or Navigate to Project
```bash
cd "/home/tahmid/Documents/Fashion mart"
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` file with your MySQL credentials:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=fashion_mart
MYSQL_PORT=3306

SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### Step 5: Setup Database

#### Option A: Using MySQL Command Line
```bash
mysql -u root -p < database/schema.sql
```

#### Option B: Using MySQL Workbench or phpMyAdmin
1. Open MySQL Workbench/phpMyAdmin
2. Import the `database/schema.sql` file
3. Execute all queries

#### Option C: Using Python Script
Update the password in `database/db_config.py` and run:
```bash
python database/db_config.py
```

### Step 6: Update Database Credentials in app.py
Edit `app.py` and update the `DB_CONFIG` dictionary with your MySQL password:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'your_mysql_password',  # Update this
    'db': 'fashion_mart',
    'charset': 'utf8mb4'
}
```

### Step 7: Run the Application
```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## 📊 Database Schema

### Core Tables

**Customer**
- CustomerID (PK), Username, Password, Name, Email, Number
- RewardPoint, Road, Area, City, District

**Product**
- ProductID (PK), ProductName, Category, Price, Quantity
- Demand, Rating, Embroidery, Description, ImageURL

**Order**
- OrderID (PK), OrderDate, TotalAmount, OrderStatus
- PaymentMethod, PaymentStatus, DeliveryAddress
- CustomerID (FK → Customer)

**OrderItem**
- OrderID (FK → Order), ProductID (FK → Product)
- Quantity, Price

**Delivery**
- DeliveryID (PK), DeliveryDate, DeliveryStatus
- OrderID (FK → Order)

**DeliveryMan**
- DeliveryManID (PK), Name, Username, Password
- Number, Area, Rating

**Admin**
- AdminID (PK), Name, Username, Password
- Email, Number

**Review**
- ReviewID (PK), CustomerID (FK), ProductID (FK)
- Rating, ReviewDate, Comment

**Payment** (Structure ready for future implementation)
- PaymentID (PK), PaymentMethod, Amount, PaymentDate
- PaymentStatus, DealerID (FK), OrderID (FK)

**Dealer** (Structure ready for future implementation)
- DealerID (PK), DealerName, Contact, Email

**Ranking** (Structure ready for future implementation)
- CustomerID (FK), ProductID (FK), Quantity

## 🎯 Usage Guide

### For Customers

1. **Registration**
   - Click "Register" in navigation
   - Fill in username, password, name, email
   - Optionally add address details
   - Submit to create account

2. **Login**
   - Click "Login" in navigation
   - Enter username and password
   - Access personalized features

3. **Browse Products**
   - Visit "Products" page
   - Use search bar to find specific items
   - Filter by category using dropdown
   - Click on product cards for details

4. **Add to Cart**
   - Click "Add to Cart" on product cards
   - Or select quantity on product detail page
   - View cart icon for item count

5. **Place Order**
   - Go to Shopping Cart
   - Review items and quantities
   - Proceed to Checkout
   - Confirm order placement

6. **Track Orders**
   - Visit "My Orders" page
   - View order history and payment status
   - Click order for detailed tracking

### For Delivery Personnel

1. **Login**
   - Visit `/delivery/login`
   - Use delivery man credentials

2. **Manage Deliveries**
   - View assigned orders
   - Mark orders as delivered
   - Confirm cash received (for COD orders)

### For Administrators

1. **Login**
   - Visit `/admin/login`
   - Use admin credentials

2. **View Dashboard**
   - Monitor orders and customers
   - View sales statistics
   - Manage system operations

### Default Test Accounts

**Sample Customers** (Password: `password123` for all):
- Username: `john_doe` - John Doe
- Username: `jane_smith` - Jane Smith
- Username: `guest_user` - Guest User

**Admin Account**:
- Username: `admin`
- Password: `admin123`

**Delivery Man Account**:
- Username: `deliveryman1`
- Password: `pass123`

## 🔜 Future Enhancements (Not Yet Implemented)

The following features are planned for future development:

1. **Advanced Payment Features**
   - Payment gateway integration (bKash, Nagad, Cards)
   - Digital payment receipts
   - Payment history tracking

2. **Enhanced Admin Dashboard**
   - Product management (add, edit, delete with UI)
   - Advanced analytics and reports
   - Customer management tools
   - Inventory alerts and notifications

3. **Advanced Features**
   - Product review submission (currently view-only)
   - Reward points redemption system
   - Email/SMS notifications
   - Product recommendations based on purchase history
   - Advanced search with multiple filters
   - Wishlist functionality
   - Order cancellation and returns

4. **Security Enhancements**
   - Password hashing (bcrypt/scrypt)
   - CSRF protection
   - Enhanced input validation
   - Rate limiting for API endpoints
   - Two-factor authentication

5. **UI/UX Improvements**
   - Image upload for products
   - Product image gallery
   - Enhanced mobile responsiveness
   - Dark mode
   - Real-time notifications
   - Progressive Web App (PWA) support

## 🐛 Troubleshooting

### Database Connection Error
- Verify MySQL server is running
- Check credentials in `.env` or `app.py`
- Ensure `fashion_mart` database exists

### Import Errors
- Activate virtual environment
- Run `pip install -r requirements.txt`
- Check Python version (3.8+)

### Port Already in Use
- Change port in `app.py`: `app.run(port=5001)`
- Or kill process using port 5000

### MySQLdb Import Error
- Install MySQL development headers:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
  
  # macOS
  brew install mysql
  
  # Then reinstall
  pip install mysqlclient
  ```

## 📝 API Endpoints

### Products
- `GET /products` - View all products with filters
- `GET /product/<id>` - View product details
- `GET /api/products` - JSON API for products

### Cart
- `POST /api/cart/add` - Add item to cart
- `GET /api/cart/get` - Get cart contents
- `POST /api/cart/update` - Update cart item quantity
- `POST /api/cart/remove` - Remove item from cart

### Orders
- `POST /api/order/create` - Create new order
- `GET /orders` - View customer orders
- `GET /order/<id>` - View order details
- `GET /order/confirmation/<id>` - Order confirmation page

### Delivery
- `POST /api/delivery/update-status/<id>` - Update delivery status
- `POST /api/delivery/confirm-payment/<id>` - Confirm cash received
- `GET /delivery/dashboard` - Delivery man dashboard

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/orders` - Manage all orders

### Authentication
- `POST /register` - Customer registration
- `POST /login` - Customer login
- `POST /delivery/login` - Delivery man login
- `POST /admin/login` - Admin login
- `GET /logout` - Logout

## 👨‍💻 Development

### Running in Development Mode
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

### Database Reset
To reset database with fresh sample data:
```bash
mysql -u root -p < database/schema.sql
```

## 📄 License

This project is developed for educational purposes.

## 🤝 Contributing

This is a learning project. Future features will be implemented based on requirements.

## 📧 Support

For issues or questions, please refer to the troubleshooting section above.

---

**Built with ❤️ for Fashion Mart**

*Last Updated: November 10, 2025*

## 📚 Additional Documentation

For detailed technical documentation, see:
- `CODE_TRIGGER_MAP.md` - Complete button-to-code mapping guide
- `FACULTY_CODE_FLOW_GUIDE.md` - Code execution flow explanations
- `PAYMENT_STATUS_FEATURE.md` - Payment tracking workflow
- `PAYMENT_STATUS_FIX.md` - Online payment auto-update details
