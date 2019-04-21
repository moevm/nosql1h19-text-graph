from neomodel import StructuredNode, StringProperty, JSONProperty, \
                     Relationship, IntegerProperty
import numpy as np
import re

from models.text_relation import TextRelation


class TextNode(StructuredNode):
    order_id = IntegerProperty(required=True, unique_index=True)
    text = StringProperty(required=True)
    alg_results = JSONProperty()
    link = Relationship('TextNode', 'ALG', model=TextRelation)

    def short(self):
        res = ''.join([word.strip() + ' '
                       for word in re.split(r'[\n ]', self.text, 5)[:5]])
        return res

    def describe(self):
        return f"""
            <h1>Фрагмент: {self.order_id} </h1>
            <table border="1" width=100%>
                <caption>
                    Информация о вершине
                </caption>
                <tr>
                    <th>Количество символов</th>
                    <td>{self.character_num()}</td>
                </tr>
                <tr>
                    <th>Количество слов</th>
                    <td>{self.words_num()}</td>
                </tr>
                <tr>
                    <th>Количество предложений</th>
                    <td>{self.sentences_num()}</td>
                </tr>
                <tr>
                    <th>Количество связей</th>
                    <td>{len(self.link)}</td>
                </tr>
            </table>
        """

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
