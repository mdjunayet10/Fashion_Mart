from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import MySQLdb
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'fashion_user'),
    'passwd': os.getenv('MYSQL_PASSWORD', 'fashion_pass_2024'),
    'db': os.getenv('MYSQL_DB', 'fashion_mart'),
    'charset': 'utf8mb4'
}

def get_db():
    """Get database connection"""
    return MySQLdb.connect(**DB_CONFIG)

# =====================================================
# HOME ROUTES
# =====================================================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration"""
    if request.method == 'POST':
        data = request.form
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                INSERT INTO Customer (Username, Password, Name, Email, Number, Road, Area, City, District)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['username'], data['password'], data['name'], data['email'],
                data.get('number', ''), data.get('road', ''), data.get('area', ''),
                data.get('city', ''), data.get('district', '')
            ))
            
            db.commit()
            cursor.close()
            db.close()
            
            return redirect(url_for('login'))
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login"""
    if request.method == 'POST':
        data = request.form
        try:
            db = get_db()
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute("""
                SELECT * FROM Customer WHERE Username = %s AND Password = %s
            """, (data['username'], data['password']))
            
            user = cursor.fetchone()
            cursor.close()
            db.close()
            
            if user:
                session['customer_id'] = user['CustomerID']
                session['username'] = user['Username']
                session['name'] = user['Name']
                return redirect(url_for('products'))
            else:
                return render_template('login.html', error='Invalid credentials')
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))

# =====================================================
# PRODUCT ROUTES
# =====================================================

@app.route('/products')
def products():
    """Display all products"""
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Build query based on filters
        query = "SELECT * FROM Product WHERE 1=1"
        params = []
        
        if category:
            query += " AND Category = %s"
            params.append(category)
        
        if search:
            query += " AND ProductName LIKE %s"
            params.append(f'%{search}%')
        
        query += " ORDER BY ProductName"
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Get all categories for filter
        cursor.execute("SELECT DISTINCT Category FROM Product ORDER BY Category")
        categories = [row['Category'] for row in cursor.fetchall()]
        
        cursor.close()
        db.close()
        
        return render_template('products.html', 
                             products=products, 
                             categories=categories,
                             selected_category=category,
                             search_term=search)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Display product details"""
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get product details
        cursor.execute("SELECT * FROM Product WHERE ProductID = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            db.close()
            return "Product not found", 404
        
        # Get product reviews
        cursor.execute("""
            SELECT r.*, c.Name as CustomerName, c.Username
            FROM Review r
            JOIN Customer c ON r.CustomerID = c.CustomerID
            WHERE r.ProductID = %s
            ORDER BY r.ReviewDate DESC
        """, (product_id,))
        reviews = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return render_template('product_detail.html', product=product, reviews=reviews)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products')
def api_products():
    """API endpoint for products"""
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT * FROM Product ORDER BY ProductName")
        products = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        # Convert Decimal to float for JSON serialization
        for product in products:
            product['Price'] = float(product['Price'])
            product['Rating'] = float(product['Rating'])
        
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# ORDER ROUTES
# =====================================================

@app.route('/cart')
def cart():
    """Display shopping cart"""
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('cart.html')

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to cart (stored in session)"""
    if 'customer_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get product details
        cursor.execute("SELECT * FROM Product WHERE ProductID = %s", (product_id,))
        product = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if product['Quantity'] < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Initialize cart in session if not exists
        if 'cart' not in session:
            session['cart'] = {}
        
        # Add or update cart item
        cart = session['cart']
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            cart[product_id_str]['quantity'] += quantity
        else:
            cart[product_id_str] = {
                'product_id': product_id,
                'name': product['ProductName'],
                'price': float(product['Price']),
                'quantity': quantity,
                'image': product['ImageURL']
            }
        
        session['cart'] = cart
        session.modified = True
        
        return jsonify({'success': True, 'cart_count': len(cart)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart/get')
def get_cart():
    """Get cart items"""
    if 'customer_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    cart = session.get('cart', {})
    return jsonify(cart)

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    if 'customer_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    data = request.json
    product_id = str(data.get('product_id'))
    quantity = data.get('quantity', 1)
    
    cart = session.get('cart', {})
    
    if product_id in cart:
        if quantity <= 0:
            del cart[product_id]
        else:
            cart[product_id]['quantity'] = quantity
        
        session['cart'] = cart
        session.modified = True
        
        return jsonify({'success': True})
    
    return jsonify({'error': 'Item not in cart'}), 404

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    if 'customer_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    data = request.json
    product_id = str(data.get('product_id'))
    
    cart = session.get('cart', {})
    
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        session.modified = True
        return jsonify({'success': True})
    
    return jsonify({'error': 'Item not in cart'}), 404

@app.route('/checkout')
def checkout():
    """Checkout page"""
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('products'))
    
    # Get customer details
    db = get_db()
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Customer WHERE CustomerID = %s", (session['customer_id'],))
    current_user = cursor.fetchone()
    cursor.close()
    db.close()
    
    return render_template('checkout.html', current_user=current_user)

@app.route('/api/order/create', methods=['POST'])
def create_order():
    """Create a new order"""
    if 'customer_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    cart = session.get('cart', {})
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400
    
    try:
        # Get payment method from request
        data = request.get_json() or {}
        payment_method = data.get('payment_method', 'Cash on Delivery')
        
        db = get_db()
        cursor = db.cursor()
        
        # Get customer address
        cursor.execute("""
            SELECT Road, Area, City, District, Number 
            FROM Customer 
            WHERE CustomerID = %s
        """, (session['customer_id'],))
        customer = cursor.fetchone()
        delivery_address = f"{customer[0]}, {customer[1]}, {customer[2]}, {customer[3]}. Phone: {customer[4]}"
        
        # Calculate total amount
        cart_items = list(cart.values())
        subtotal = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
        delivery_charge = 100.00
        total_amount = subtotal + delivery_charge
        
        # Create order with payment method and delivery address
        cursor.execute("""
            INSERT INTO `Order` (CustomerID, TotalAmount, OrderStatus, PaymentMethod, PaymentStatus, DeliveryAddress)
            VALUES (%s, %s, 'Pending', %s, 'Pending', %s)
        """, (session['customer_id'], total_amount, payment_method, delivery_address))
        
        order_id = cursor.lastrowid
        
        # Create order items
        for item in cart_items:
            cursor.execute("""
                INSERT INTO OrderItem (OrderID, ProductID, Quantity, Price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['product_id'], item['quantity'], item['price']))
            
            # Update product quantity
            cursor.execute("""
                UPDATE Product 
                SET Quantity = Quantity - %s, Demand = Demand + %s
                WHERE ProductID = %s
            """, (item['quantity'], item['quantity'], item['product_id']))
        
        # Create delivery record
        cursor.execute("""
            INSERT INTO Delivery (OrderID, DeliveryStatus)
            VALUES (%s, 'Pending')
        """, (order_id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        # Clear cart
        session['cart'] = {}
        session.modified = True
        
        return jsonify({
            'success': True, 
            'order_id': order_id,
            'total_amount': float(total_amount)
        })
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/orders')
def my_orders():
    """Display customer orders"""
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get customer orders
        cursor.execute("""
            SELECT o.*, d.DeliveryStatus, d.DeliveryDate
            FROM `Order` o
            LEFT JOIN Delivery d ON o.OrderID = d.OrderID
            WHERE o.CustomerID = %s
            ORDER BY o.OrderDate DESC
        """, (session['customer_id'],))
        
        orders = list(cursor.fetchall())
        
        # Get order items for each order
        for order in orders:
            cursor.execute("""
                SELECT oi.*, p.ProductName, p.ImageURL
                FROM OrderItem oi
                JOIN Product p ON oi.ProductID = p.ProductID
                WHERE oi.OrderID = %s
            """, (order['OrderID'],))
            order['order_items'] = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return render_template('orders.html', orders=orders)
    except Exception as e:
        print(f"Error in my_orders: {e}")
        import traceback
        traceback.print_exc()
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

@app.route('/order/confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Display order confirmation receipt"""
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get order details
        cursor.execute("""
            SELECT o.*, d.DeliveryStatus, d.DeliveryDate
            FROM `Order` o
            LEFT JOIN Delivery d ON o.OrderID = d.OrderID
            WHERE o.OrderID = %s AND o.CustomerID = %s
        """, (order_id, session['customer_id']))
        
        order = cursor.fetchone()
        
        if not order:
            return redirect(url_for('my_orders'))
        
        # Get order items
        cursor.execute("""
            SELECT oi.*, p.ProductName, p.ImageURL
            FROM OrderItem oi
            JOIN Product p ON oi.ProductID = p.ProductID
            WHERE oi.OrderID = %s
        """, (order_id,))
        
        order['order_items'] = list(cursor.fetchall())
        
        # Get customer details
        cursor.execute("""
            SELECT * FROM Customer WHERE CustomerID = %s
        """, (session['customer_id'],))
        
        customer = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return render_template('order_confirmation.html', order=order, customer=customer)
    except Exception as e:
        print(f"Error in order_confirmation: {e}")
        return redirect(url_for('my_orders'))

@app.route('/order/<int:order_id>')
def order_detail(order_id):
    """Display order details"""
    if 'customer_id' not in session:
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get order details
        cursor.execute("""
            SELECT o.*, d.DeliveryStatus, d.DeliveryDate, c.Name, c.Email, c.Number,
                   c.Road, c.Area, c.City, c.District
            FROM `Order` o
            LEFT JOIN Delivery d ON o.OrderID = d.OrderID
            JOIN Customer c ON o.CustomerID = c.CustomerID
            WHERE o.OrderID = %s AND o.CustomerID = %s
        """, (order_id, session['customer_id']))
        
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            db.close()
            return "Order not found", 404
        
        # Get order items
        cursor.execute("""
            SELECT oi.*, p.ProductName, p.ImageURL, p.Category
            FROM OrderItem oi
            JOIN Product p ON oi.ProductID = p.ProductID
            WHERE oi.OrderID = %s
        """, (order_id,))
        
        order['order_items'] = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return render_template('order_detail.html', order=order)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# REVIEW AND RATING ROUTES
# =====================================================

@app.route('/api/review/add', methods=['POST'])
def add_review():
    """Add a new review for a product"""
    try:
        if 'customer_id' not in session:
            return jsonify({'error': 'Please login to submit a review'}), 401
        
        data = request.get_json()
        product_id = data.get('product_id')
        rating = data.get('rating')
        comment = data.get('comment', '').strip()
        
        # Validate input
        if not product_id or not rating:
            return jsonify({'error': 'Product ID and rating are required'}), 400
        
        if not (1 <= int(rating) <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        customer_id = session['customer_id']
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if product exists
        cursor.execute("SELECT ProductID FROM Product WHERE ProductID = %s", (product_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if customer already reviewed this product
        cursor.execute("""
            SELECT ReviewID FROM Review 
            WHERE CustomerID = %s AND ProductID = %s
        """, (customer_id, product_id))
        
        if cursor.fetchone():
            return jsonify({'error': 'You have already reviewed this product'}), 400
        
        # Insert review
        cursor.execute("""
            INSERT INTO Review (CustomerID, ProductID, Rating, Comment, ReviewDate)
            VALUES (%s, %s, %s, %s, NOW())
        """, (customer_id, product_id, rating, comment))
        
        db.commit()
        review_id = cursor.lastrowid
        
        # Get the review with customer name
        cursor.execute("""
            SELECT r.ReviewID, r.Rating, r.Comment, r.ReviewDate,
                   c.FirstName, c.LastName
            FROM Review r
            JOIN Customer c ON r.CustomerID = c.CustomerID
            WHERE r.ReviewID = %s
        """, (review_id,))
        
        review = cursor.fetchone()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Review submitted successfully',
            'review': {
                'review_id': review[0],
                'rating': review[1],
                'comment': review[2],
                'review_date': review[3].strftime('%Y-%m-%d %H:%M:%S'),
                'customer_name': f"{review[4]} {review[5]}"
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviews/<int:product_id>', methods=['GET'])
def get_reviews(product_id):
    """Get all reviews for a product"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get all reviews for the product
        cursor.execute("""
            SELECT r.ReviewID, r.Rating, r.Comment, r.ReviewDate,
                   c.FirstName, c.LastName, c.CustomerID
            FROM Review r
            JOIN Customer c ON r.CustomerID = c.CustomerID
            WHERE r.ProductID = %s
            ORDER BY r.ReviewDate DESC
        """, (product_id,))
        
        reviews_data = cursor.fetchall()
        
        # Get average rating and count
        cursor.execute("""
            SELECT AVG(Rating) as avg_rating, COUNT(*) as review_count
            FROM Review
            WHERE ProductID = %s
        """, (product_id,))
        
        stats = cursor.fetchone()
        avg_rating = float(stats[0]) if stats[0] else 0
        review_count = stats[1]
        
        cursor.close()
        db.close()
        
        reviews = []
        for review in reviews_data:
            reviews.append({
                'review_id': review[0],
                'rating': review[1],
                'comment': review[2],
                'review_date': review[3].strftime('%B %d, %Y at %I:%M %p'),
                'customer_name': f"{review[4]} {review[5]}",
                'customer_id': review[6],
                'is_mine': 'customer_id' in session and session['customer_id'] == review[6]
            })
        
        return jsonify({
            'success': True,
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1),
            'review_count': review_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# DELIVERY MAN ROUTES
# =====================================================

@app.route('/delivery/login', methods=['GET', 'POST'])
def delivery_login():
    """Delivery man login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('delivery_login.html')
        
        try:
            db = get_db()
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute("""
                SELECT * FROM DeliveryMan 
                WHERE Username = %s AND Password = %s AND Status = 'Active'
            """, (username, password))
            
            delivery_man = cursor.fetchone()
            cursor.close()
            db.close()
            
            if delivery_man:
                session['delivery_man_id'] = delivery_man['DeliveryManID']
                session['delivery_man_name'] = delivery_man['Name']
                session['user_type'] = 'delivery'
                session.modified = True
                
                flash('Login successful!', 'success')
                return redirect(url_for('delivery_dashboard'))
            else:
                flash('Invalid credentials or inactive account', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('delivery_login.html')

@app.route('/delivery/logout')
def delivery_logout():
    """Delivery man logout"""
    session.pop('delivery_man_id', None)
    session.pop('delivery_man_name', None)
    session.pop('user_type', None)
    session.modified = True
    flash('Logged out successfully', 'success')
    return redirect(url_for('delivery_login'))

@app.route('/delivery/dashboard')
def delivery_dashboard():
    """Delivery man dashboard showing assigned orders"""
    if 'delivery_man_id' not in session:
        return redirect(url_for('delivery_login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get assigned orders
        cursor.execute("""
            SELECT o.*, c.Name, c.Number, c.Road, c.Area, c.City, c.District
            FROM `Order` o
            JOIN Customer c ON o.CustomerID = c.CustomerID
            WHERE o.DeliveryManID = %s
            ORDER BY o.OrderDate DESC
        """, (session['delivery_man_id'],))
        
        orders = list(cursor.fetchall())
        
        # Get order items for each order
        for order in orders:
            cursor.execute("""
                SELECT oi.*, p.ProductName, p.ImageURL
                FROM OrderItem oi
                JOIN Product p ON oi.ProductID = p.ProductID
                WHERE oi.OrderID = %s
            """, (order['OrderID'],))
            order['order_items'] = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return render_template('delivery_dashboard.html', orders=orders)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('delivery_login'))

@app.route('/delivery/api/update-payment-status', methods=['POST'])
def update_payment_status():
    """Update payment status when delivery man receives cash"""
    if 'delivery_man_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    payment_status = data.get('payment_status')
    
    if not order_id or not payment_status:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verify order is assigned to this delivery man
        cursor.execute("""
            SELECT DeliveryManID, OrderStatus FROM `Order` WHERE OrderID = %s
        """, (order_id,))
        
        result = cursor.fetchone()
        if not result or result[0] != session['delivery_man_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        current_order_status = result[1]
        
        # Update payment status
        cursor.execute("""
            UPDATE `Order` 
            SET PaymentStatus = %s
            WHERE OrderID = %s
        """, (payment_status, order_id))
        
        # If order is delivered AND payment is now paid/received, mark as Complete
        if current_order_status == 'Delivered' and payment_status == 'Paid':
            cursor.execute("""
                UPDATE `Order` 
                SET OrderStatus = 'Complete'
                WHERE OrderID = %s
            """, (order_id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'message': 'Payment status updated'})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delivery/api/update-order-status', methods=['POST'])
@app.route('/delivery/api/update-order-status', methods=['POST'])
def update_order_status():
    """Update order delivery status"""
    if 'delivery_man_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    order_status = data.get('order_status')
    
    if not order_id or not order_status:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verify order is assigned to this delivery man and get payment info
        cursor.execute("""
            SELECT DeliveryManID, PaymentStatus, PaymentMethod 
            FROM `Order` 
            WHERE OrderID = %s
        """, (order_id,))
        
        result = cursor.fetchone()
        if not result or result[0] != session['delivery_man_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        payment_status = result[1]
        payment_method = result[2]
        
        # Update order status
        cursor.execute("""
            UPDATE `Order` 
            SET OrderStatus = %s
            WHERE OrderID = %s
        """, (order_status, order_id))
        
        # If marked as Delivered
        if order_status == 'Delivered':
            # For Online Payment or Bank Transfer, auto-mark payment as Paid and order as Complete
            if payment_method in ['Online Payment', 'Bank Transfer']:
                cursor.execute("""
                    UPDATE `Order` 
                    SET PaymentStatus = 'Paid', OrderStatus = 'Complete'
                    WHERE OrderID = %s
                """, (order_id,))
            # For Cash on Delivery with already paid status, mark as Complete
            elif payment_status == 'Paid':
                cursor.execute("""
                    UPDATE `Order` 
                    SET OrderStatus = 'Complete'
                    WHERE OrderID = %s
                """, (order_id,))
        
        # Also update delivery table
        cursor.execute("""
            UPDATE Delivery 
            SET DeliveryStatus = %s,
                DeliveryDate = CASE WHEN %s IN ('Delivered', 'Complete') THEN CURDATE() ELSE DeliveryDate END
            WHERE OrderID = %s
        """, (order_status, order_status, order_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'message': 'Order status updated'})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

# =====================================================
# ADMIN ROUTES
# =====================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('admin_login.html')
        
        try:
            db = get_db()
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            
            cursor.execute("""
                SELECT * FROM Admin 
                WHERE Username = %s AND Password = %s
            """, (username, password))
            
            admin = cursor.fetchone()
            cursor.close()
            db.close()
            
            if admin:
                session['admin_id'] = admin['AdminID']
                session['admin_name'] = admin['Name']
                session['admin_role'] = admin['Role']
                session['user_type'] = 'admin'
                session.modified = True
                
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid credentials', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_role', None)
    session.pop('user_type', None)
    session.modified = True
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Main admin dashboard"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) as total FROM Customer")
        total_customers = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM Product")
        total_products = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM `Order`")
        total_orders = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM DeliveryMan WHERE Status = 'Active'")
        total_delivery = cursor.fetchone()['total']
        
        cursor.execute("SELECT SUM(TotalAmount) as revenue FROM `Order` WHERE OrderStatus = 'Complete'")
        total_revenue = cursor.fetchone()['revenue'] or 0
        
        # Get recent orders
        cursor.execute("""
            SELECT o.*, c.Name as CustomerName 
            FROM `Order` o
            JOIN Customer c ON o.CustomerID = c.CustomerID
            ORDER BY o.OrderDate DESC
            LIMIT 5
        """)
        recent_orders = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        stats = {
            'customers': total_customers,
            'products': total_products,
            'orders': total_orders,
            'delivery_men': total_delivery,
            'revenue': float(total_revenue)
        }
        
        return render_template('admin_dashboard.html', stats=stats, recent_orders=recent_orders)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/orders')
def admin_orders():
    """Admin page to view and assign orders"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get all orders with customer and delivery man info
        cursor.execute("""
            SELECT o.*, c.Name as CustomerName, c.Number, d.Name as DeliveryManName
            FROM `Order` o
            JOIN Customer c ON o.CustomerID = c.CustomerID
            LEFT JOIN DeliveryMan d ON o.DeliveryManID = d.DeliveryManID
            ORDER BY o.OrderDate DESC
        """)
        
        orders = list(cursor.fetchall())
        
        # Get all active delivery men
        cursor.execute("""
            SELECT DeliveryManID, Name, Phone, VehicleType 
            FROM DeliveryMan 
            WHERE Status = 'Active'
            ORDER BY Name
        """)
        
        delivery_men = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return render_template('admin_orders.html', orders=orders, delivery_men=delivery_men)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/admin/customers')
def admin_customers():
    """Admin page to manage customers"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("""
            SELECT c.*, 
                   COUNT(DISTINCT o.OrderID) as TotalOrders,
                   COALESCE(SUM(CASE WHEN o.OrderStatus = 'Complete' THEN o.TotalAmount ELSE 0 END), 0) as TotalSpent
            FROM Customer c
            LEFT JOIN `Order` o ON c.CustomerID = o.CustomerID
            GROUP BY c.CustomerID
            ORDER BY c.CreatedAt DESC
        """)
        
        customers = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return render_template('admin_customers.html', customers=customers)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/admin/products')
def admin_products():
    """Admin page to manage products"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("SELECT * FROM Product ORDER BY ProductName")
        products = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return render_template('admin_products.html', products=products)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/admin/delivery')
def admin_delivery():
    """Admin page to manage delivery personnel"""
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("""
            SELECT d.*, 
                   COUNT(DISTINCT o.OrderID) as AssignedOrders,
                   SUM(CASE WHEN o.OrderStatus = 'Complete' THEN 1 ELSE 0 END) as CompletedDeliveries
            FROM DeliveryMan d
            LEFT JOIN `Order` o ON d.DeliveryManID = o.DeliveryManID
            GROUP BY d.DeliveryManID
            ORDER BY d.Name
        """)
        
        delivery_men = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return render_template('admin_delivery.html', delivery_men=delivery_men)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/admin/api/add-product', methods=['POST'])
def add_product():
    """Add new product"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO Product (ProductName, Category, Price, Quantity, Description, ImageURL, Embroidery)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('name'),
            data.get('category'),
            data.get('price'),
            data.get('stock'),
            data.get('description'),
            data.get('image_url'),
            data.get('embroidery_type', 'None')
        ))
        
        db.commit()
        product_id = cursor.lastrowid
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'product_id': product_id})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/update-product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    """Update product"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            UPDATE Product 
            SET ProductName = %s, Category = %s, Price = %s, 
                Quantity = %s, Description = %s, ImageURL = %s, Embroidery = %s
            WHERE ProductID = %s
        """, (
            data.get('name'),
            data.get('category'),
            data.get('price'),
            data.get('stock'),
            data.get('description'),
            data.get('image_url'),
            data.get('embroidery_type'),
            product_id
        ))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/delete-product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM Product WHERE ProductID = %s", (product_id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/add-delivery-person', methods=['POST'])
def add_delivery_person():
    """Add new delivery person"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'username', 'password', 'email', 'phone', 'vehicle_type']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT DeliveryManID FROM DeliveryMan WHERE Username = %s", (data['username'],))
        if cursor.fetchone():
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check if email already exists
        cursor.execute("SELECT DeliveryManID FROM DeliveryMan WHERE Email = %s", (data['email'],))
        if cursor.fetchone():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Insert new delivery person
        cursor.execute("""
            INSERT INTO DeliveryMan (Username, Password, Name, Email, Phone, Address, VehicleType, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
        """, (
            data['username'],
            data['password'],
            data['name'],
            data['email'],
            data['phone'],
            data.get('address', ''),
            data['vehicle_type']
        ))
        
        db.commit()
        delivery_man_id = cursor.lastrowid
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'delivery_man_id': delivery_man_id})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/assign-delivery', methods=['POST'])
def assign_delivery():
    """Assign order to delivery man"""
    data = request.get_json()
    order_id = data.get('order_id')
    delivery_man_id = data.get('delivery_man_id')
    
    if not order_id or not delivery_man_id:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Update order with delivery man assignment
        cursor.execute("""
            UPDATE `Order` 
            SET DeliveryManID = %s
            WHERE OrderID = %s
        """, (delivery_man_id, order_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'message': 'Order assigned successfully'})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/customer/<int:customer_id>')
def get_customer_details(customer_id):
    """Get customer details"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute("""
            SELECT c.*, 
                   COUNT(DISTINCT o.OrderID) as TotalOrders,
                   COALESCE(SUM(CASE WHEN o.OrderStatus = 'Complete' THEN o.TotalAmount ELSE 0 END), 0) as TotalSpent
            FROM Customer c
            LEFT JOIN `Order` o ON c.CustomerID = o.CustomerID
            WHERE c.CustomerID = %s
            GROUP BY c.CustomerID
        """, (customer_id,))
        
        customer = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if customer:
            return jsonify(customer)
        else:
            return jsonify({'error': 'Customer not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/delivery-orders/<int:delivery_man_id>')
def get_delivery_orders(delivery_man_id):
    """Get orders assigned to a delivery man"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        db = get_db()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        
        # Get delivery man name
        cursor.execute("SELECT Name FROM DeliveryMan WHERE DeliveryManID = %s", (delivery_man_id,))
        delivery_man = cursor.fetchone()
        
        if not delivery_man:
            return jsonify({'error': 'Delivery man not found'}), 404
        
        # Get orders
        cursor.execute("""
            SELECT o.OrderID, o.TotalAmount, o.OrderStatus, o.PaymentStatus, 
                   o.OrderDate, c.Name as CustomerName
            FROM `Order` o
            JOIN Customer c ON o.CustomerID = c.CustomerID
            WHERE o.DeliveryManID = %s
            ORDER BY o.OrderDate DESC
        """, (delivery_man_id,))
        
        orders = list(cursor.fetchall())
        
        cursor.close()
        db.close()
        
        return jsonify({
            'delivery_man_name': delivery_man['Name'],
            'orders': orders
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
