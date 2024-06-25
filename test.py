import pytest
from app import app, db, Customer, Product, Order

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_add_customer(client):
    response = client.post('/add_customer', data={'name': 'Test Customer', 'code': 'TC001'})
    assert response.status_code == 302  # Redirect after successful post
    assert Customer.query.filter_by(name='Test Customer').first() is not None

def test_add_product(client):
    response = client.post('/add_product', data={'name': 'Test Product', 'price': 10.99})
    assert response.status_code == 302  # Redirect after successful post
    assert Product.query.filter_by(name='Test Product').first() is not None

def test_place_order(client):
    # Add a customer and a product
    client.post('/add_customer', data={'name': 'Test Customer', 'code': 'TC001'})
    client.post('/add_product', data={'name': 'Test Product', 'price': 10.99})
    
    customer = Customer.query.first()
    product = Product.query.first()
    
    response = client.post(f'/place_order/{customer.id}', data={'product_id': product.id, 'amount': 2})
    assert response.status_code == 302  # Redirect after successful post
    assert Order.query.filter_by(customer_id=customer.id).first() is not None

def test_sms_sending(client, monkeypatch):
    # Mock the SMS sending function
    def mock_send_sms(*args, **kwargs):
        return {"SMSMessageData": {"Message": "Sent to 1/1 Total Cost: USD 0.0"}}
    
    monkeypatch.setattr('africastalking.SMS.send', mock_send_sms)
    
    # Add a customer and a product
    client.post('/add_customer', data={'name': 'Test Customer', 'code': '+1234567890'})
    client.post('/add_product', data={'name': 'Test Product', 'price': 10.99})
    
    customer = Customer.query.first()
    product = Product.query.first()
    
    response = client.post(f'/place_order/{customer.id}', data={'product_id': product.id, 'amount': 2})
    assert response.status_code == 302  
   