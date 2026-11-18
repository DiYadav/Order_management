from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer

        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
        ]

        read_only_fields = ["id"]
