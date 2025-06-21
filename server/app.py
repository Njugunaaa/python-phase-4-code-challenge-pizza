#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

#returns alll the restaurants using the get request
class Restaurants(Resource):
     def get(self):
        restaurants = Restaurant.query.all()
        result = [{
            "id": r.id,
            "name": r.name,
            "address": r.address
        } for r in restaurants]
        return result, 200
api.add_resource(Restaurants, "/restaurants")



#returns alll the restaurants hby using input of id  using the get request and delete request
class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)

        if restaurant is None:
            return {"error": "Restaurant not found"}, 404

        data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": []
        }

        for order in restaurant.restaurant_pizzas:
            pizza = order.pizza
            data["restaurant_pizzas"].append({
                "id": order.id,
                "price": order.price,
                "pizza_id": order.pizza_id,
                "restaurant_id": order.restaurant_id,
                "pizza": {
                    "id": pizza.id,
                    "name": pizza.name,
                    "ingredients": pizza.ingredients
                }
            })

        return data, 200

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204
api.add_resource(RestaurantByID, "/restaurants/<int:id>")


#returns all the pizzas using the get request
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200


api.add_resource(Pizzas, "/pizzas")

class AddRestaurantPizza(Resource):
    def post(self):
        data = request.get_json()

        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if not price or not pizza_id or not restaurant_id:
            return {"errors": ["validation errors"]}, 400

        if price < 1 or price > 30:
            return {"errors": ["validation errors"]}, 400

        new_rp = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(new_rp)
        db.session.commit()

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        response = {
            "id": new_rp.id,
            "price": price,
            "pizza_id": pizza_id,
            "restaurant_id": restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }

        return make_response(response, 201)

api.add_resource(AddRestaurantPizza, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
