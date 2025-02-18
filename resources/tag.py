from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db   
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint("tags", __name__, description="Operations on tags")

@blp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):

        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="A tag with that name already exists in this store")

        tag = TagModel(**tag_data, store_id=store_id)
        
        try:
            db.session.add(tag)
            db.session.commit()
        
        except SQLAlchemyError:
            abort(500, message="An error has ocurred while inserting the tag")
        
        return tag

# This route is used to link and unlink tags to items
@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(200, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag in item.tags:
            return {"message": "Tag already linked to item", "tag": tag, "item": item}

        item.tags.append(tag)
        db.session.commit()
        return {"message": "Tag linked to item", "tag": tag, "item": item}

    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag not in item.tags:
            return {"message": "Tag not linked to item", "tag": tag, "item": item}

        item.tags.remove(tag)
        db.session.commit()
        return {"message": "Tag unlinked from item", "tag": tag, "item": item}

    
@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def put(self, tag_data, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        tag.name = tag_data["name"]
        db.session.commit()
        return tag

    