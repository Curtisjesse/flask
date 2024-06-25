import os
import datetime
from flask import Flask, request, render_template, redirect, url_for, flash
from africastalking.Service import AfricasTalkingException
from flask_sqlalchemy import SQLAlchemy
import africastalking
from dotenv import load_dotenv
import traceback
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Africa's Talking
at_username = os.getenv('AT_USERNAME')
at_api_key = os.getenv('AT_API_KEY')

if not at_username or not at_api_key:
    raise ValueError("Africa's Talking credentials are missing. Check your .env file.")

africastalking.initialize(at_username, at_api_key)
sms = africastalking.SMS

# Log the initialization
app.logger.info(f"Initialized Africa's Talking with username: {at_username}")

# Define models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Customer {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Order {self.item}>'

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    customers = Customer.query.all()
    products = Product.query.all()
    return render_template('index.html', customers=customers, products=products)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        new_customer = Customer(name=name, code=code)
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_customer.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/place_order/<int:customer_id>', methods=['GET', 'POST'])
def place_order(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    products = Product.query.all()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['amount'])
        product = Product.query.get_or_404(product_id)
        total_price = product.price * quantity

        new_order = Order(item=product.name, price=product.price, quantity=quantity, customer_id=customer_id)
        db.session.add(new_order)
        db.session.commit()

        # Prepare the SMS message
        message = f"Hello {customer.name}, your order has been placed successfully.\n"
        message += f"Item: {product.name}\n"
        message += f"Quantity: {quantity}\n"
        message += f"Total Price: Ksh{total_price:.2f}\n"
        message += "Thank you for your order!"

        try:
            # Send the SMS
            response = sms.send(message, [customer.code])
            app.logger.info(f"SMS sent successfully: {response}")
            flash('Order placed successfully and confirmation SMS sent.', 'success')
        except AfricasTalkingException as e:
            app.logger.error(f"Africa's Talking error: {str(e)}")
            flash(f'Order placed successfully, but SMS sending failed: {str(e)}', 'warning')
        except Exception as e:
            app.logger.error(f"Unexpected error while sending SMS: {str(e)}")
            app.logger.error(traceback.format_exc())
            flash('Order placed successfully, but we encountered an unexpected error while sending the SMS.', 'warning')

        return redirect(url_for('index'))

    return render_template('place_order.html', customer=customer, products=products)

@app.route('/test_sms')
def test_sms():
    try:
        response = sms.send("Test message", [""]) #a valid phone number to receive the sms
        app.logger.info(f"SMS test successful. Response: {response}")
        return f"SMS test successful. Response: {response}"
    except AfricasTalkingException as e:
        app.logger.error(f"Africa's Talking error during SMS test: {str(e)}")
        return f"SMS test failed (Africa's Talking error): {str(e)}", 500
    except Exception as e:
        app.logger.error(f"Unexpected error during SMS test: {str(e)}")
        app.logger.error(traceback.format_exc())
        return f"SMS test failed (unexpected error): {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)