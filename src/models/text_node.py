from neomodel import StructuredNode, StringProperty, JSONProperty, \
                     Relationship, IntegerProperty
import numpy as np

from models.text_relation import TextRelation


class TextNode(StructuredNode):
    order_id = IntegerProperty(required=True, unique_index=True)
    text = StringProperty(required=True)
    alg_results = JSONProperty()
    link = Relationship('TextNode', 'ALG', model=TextRelation)

    def short(self):
        res = ''.join([word + ' ' for word in self.text.split(' ')[:5]])
        return res

    def preview(self, frag_num=0):
        leading = 3
        if frag_num > 0:
            leading = int(np.floor(np.log10(frag_num))) + 1
        return f"{str(self.order_id).zfill(leading)}: {self.short()}..."

    def words_num(self):
        return len(self.text.split())

    def character_num(self):
        return len(self.text)

    def sentences_num(self):
        return len([s for s in self.text.split('.') if len(s) > 2])
