from neomodel import StructuredRel, FloatProperty, JSONProperty, StringProperty


class TextRelation(StructuredRel):
    algorithm_name = StringProperty(required=True)
    intersection = FloatProperty(required=True)
    data = JSONProperty()
