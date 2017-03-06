from rest_framework import serializers
import base64

class BytesField(serializers.Field):

    def to_representation(self, obj):
        stringRep = base64.b64encode(obj)
        return stringRep

    def to_internal_value(self, data):
        return base64.b64decode(data)
