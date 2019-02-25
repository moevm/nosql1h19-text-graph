from neomodel import StringProperty, StructuredNode


class HelloNode(StructuredNode):
    hello_text = StringProperty(required=True)

