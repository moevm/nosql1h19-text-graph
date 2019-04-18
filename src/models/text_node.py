from neomodel import StructuredNode, StringProperty, JSONProperty, \
                     Relationship, IntegerProperty

from models.text_relation import TextRelation


class TextNode(StructuredNode):
    order_id = IntegerProperty(required=True, unique_index=True)
    text = StringProperty(required=True)
    alg_results = JSONProperty()
    link = Relationship('TextNode', 'ALG', model=TextRelation)

    def short(self):
        res = ''.join([word + ' ' for word in self.text.split(' ')[:5]])
        return res

    def preview(self):
        return f"{self.order_id}: {self.short()}..."

    def words_num(self):
        return len(self.text.split())

    def character_num(self):
        return len(self.text)

    def sentences_num(self):
        return len([s for s in self.text.split('.') if len(s) > 2])
