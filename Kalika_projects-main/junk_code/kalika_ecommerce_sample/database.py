# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    # Create a configured "Session" class


    ### insert product data in ecommerce.db in table name products
    # products = [
    #     {id: 1, name: "Handgloves", price: 19.99, description: "Description for Product 1"},
    #     {id: 2, name: "Stretchfilm", price: 29.99, description: "Description for Product 2"},
    #     {id: 3, name: "Tarpaulin", price: 39.99, description: "Description for Product 3"},
    # ];


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    total_amount = Column(Float)
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    order = relationship("Order", back_populates="items")

class Database:
    def __init__(self):
        engine = create_engine('sqlite:///ecommerce.db')
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)
        products = [
            {"id": 1, "name": "Handgloves", "price": 19.99, "description": "Description for Product 1"},
            {"id": 2, "name": "Stretchfilm", "price": 29.99, "description": "Description for Product 2"},
            {"id": 3, "name": "Tarpaulin", "price": 39.99, "description": "Description for Product 3"},
        ]

        # Insert products into the database
        for product_data in products:
            product = Product(
                id=product_data["id"],
                name=product_data["name"],
                price=product_data["price"],
                description=product_data["description"]
            )
            self.session.add(product)

        # Commit the transaction
        self.session.commit()


    def get_products(self):
        session = self.Session()
        products = session.query(Product).all()
        session.close()
        return products

    def get_product(self, product_id):
        session = self.Session()
        product = session.query(Product).filter_by(id=product_id).first()
        session.close()
        return product

    def create_order(self, cart_items):
        session = self.Session()
        order = Order(total_amount=sum(item['price'] * item['quantity'] for item in cart_items))
        for item in cart_items:
            order_item = OrderItem(product_id=item['product_id'], quantity=item['quantity'])
            order.items.append(order_item)
        session.add(order)
        session.commit()
        order_id = order.id
        session.close()
        return order_id
