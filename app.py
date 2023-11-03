from flask import Flask, request
from db import shops, products
import uuid

app = Flask(__name__)

# DB for now


@app.route("/shop")
def get_shops():
    return shops

@app.route("/shop", methods=['POST'])
def create_shop():
    shop_data = request.json
    shop_id = uuid.uuid4().hex
    print(shop_id)
    shop = {**shop_data, "id": shop_id}
    print(shop)
    shops[shop_id]= shop
    return shop, 201

# <shop_name> - Path parameter
@app.route("/product", methods=['POST'])
def create_product(shop_name):
    new_product = request.json
    if new_product['shop_id'] not in shops:
        return {'message': 'Shop not found'}, 404
    product_id = uuid.uuid4().hex 
    product = {**new_product, "id": product_id}
    products[product_id] = product

    return product


@app.route("/shops/<shop_id>")
def get_shop_by_name(shop_id):
    try:
        return shops[shop_id]
    except KeyError:
        return {'message': 'Shop not found'}, 404
@app.route("/product/<shop_id>")
def get_shop_by_id(shop_id):
    try:
        return shops[shop_id]
    except KeyError:
        return {'message': 'Shop not found'}, 404
    
@app.route("/product")
def get_products():
        return {'products': list(products.values())}
 
    

app.run()