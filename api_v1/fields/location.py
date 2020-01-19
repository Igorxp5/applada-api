from rest_framework import serializers

class LocationField(serializers.Field):

    def to_representation(self, obj):
        ret = {
            "latitude": obj.latitude,
            "longitude": obj.longitude
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            "location": {
                "latitude": data["latitude"],
                "longitude": data["longitude"]
            }
            
        }
        return ret
