from db import db

class TagsItem(db.Model):
    __tablename__ = "tags_items"

    id = db.Column(db.Integer, primary_key = True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)

    