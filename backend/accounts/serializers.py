from rest_framework import serializers
from .models import User, Tenant


class RegisterSerializer(serializers.ModelSerializer):

    tenant_name = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password",
            "tenant_name"
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def create(self, validated_data):

        tenant_name = validated_data.pop(
            "tenant_name"
        )

        tenant, _ = Tenant.objects.get_or_create(
            name=tenant_name
        )

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            tenant=tenant
        )

        return user