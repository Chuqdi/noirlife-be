from users.models import   ReferalCode, User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from utils.randomString import GenerateRandomString


def checkUserRefCodeExist():
    code = GenerateRandomString.randomAlhanumeric(6)
    if User.objects.filter(ref_code=code).exists():
        checkUserCodeExist()
    return code


def checkUserCodeExist():
    code = GenerateRandomString.randomAlhanumeric(6)
    if ReferalCode.objects.filter(code=code).exists():
        checkUserCodeExist()
    return code

        
class UserEmailSerializer(serializers.Serializer):
    user__full_name = serializers.CharField() 
    user__email = serializers.EmailField()

        
        
class ReferalCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferalCode
        fields=[
            "code"
        ]

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length =8)
    
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "full_name",
            "is_new",
            "is_active",
            "referalCode",
            "refered_by_code",
            "is_superuser",
            "profile_image",
            "date_joined",
            "phone_number",
            "ref_code",
            "is_book_session_payment_completed"
        ]
        




    # def validate(self, attrs):
    #     if User.objects.filter(email=attrs.get("email")).exists():
    #         raise ValidationError("User email already taken")

        # return super().validate(attrs)
    
    def create(self, validated_data):
        password = validated_data.get("password")
        user = super().create(validated_data)
        user.set_password(password)
        ref_code = checkUserRefCodeExist()
        referalCode =checkUserCodeExist()
        ReferalCode.objects.create(user=user, code = referalCode)
        user.referalCode = referalCode
        user.ref_code = ref_code
        Token.objects.create(user=user)
        user.save()
        
        return user
 
