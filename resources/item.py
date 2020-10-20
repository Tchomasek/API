from flask_restful import Resource, reqparse
from flask_jwt_extended import (
                                jwt_required,
                                get_jwt_claims,
                                jwt_optional,
                                get_jwt_identity,
                                fresh_jwt_required
                                )
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=str,
        required=True,
        help="This field cannot be blank."
    )

    parser.add_argument(
        'store_id',
        type=str,
        required=True,
        help="Every item needs a store id"
    )

    @jwt_required
    def get(self,name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item Not Found'},404

    @fresh_jwt_required
    def post(self,name):
        if ItemModel.find_by_name(name):
            return {'message': f"an item with {name} already exists."}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name,**data)
        try:
            item.save_to_db()
        except:
            return {'message':"An error occured inserting the item."}, 500 #Internal Server Error

        return item.json(),201

    @jwt_required
    def delete(self,name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message':'admin privilege required'}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message':'Item Deleted'}
        return {'message':'No such item in the database.'}

    def put(self,name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name,**data)
        else:
            item.price = data['price']
        item.save_to_db()

        return item.json()

class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {'items': [item['name'] for item in items],
                'message': 'more data available if you log in.'
        }, 200














#d
