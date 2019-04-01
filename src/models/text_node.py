from neomodel import StructuredNode, StringProperty, JSONProperty, \
                     Relationship, IntegerProperty

from models.text_relation import TextRelation


class TextNode(StructuredNode):
    order_id = IntegerProperty(required=True, unique_index=True)
    text = StringProperty(required=True)
    short = StringProperty(required=True)
    alg_results = JSONProperty()
    link = Relationship('TextNode', 'ALG', model=TextRelation)
