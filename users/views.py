import threading
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
import json
from email_validator import validate_email
from users.models import DeviceToken, ReferalCode, User, UserEmailActivationCode
from users.serializers import (
    ReferalCodeSerializer,
    SignUpSerializer,
)
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import permissions
from django.contrib.auth import logout
from utils.ResponseGenerator import ResponseGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from utils.helpers import generateUserOTP, validateOTPCode
from utils.TokenGenerator import generateToken
from datetime import date, datetime
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from datetime import timedelta
from utils.tasks import send_email
from django.utils import timezone


def schedule_onboarding_emails(user_email, signup_time=None):
    if signup_time is None:
        signup_time = timezone.now()

    schedules = [
        ("second", timedelta(hours=24)),
        ("third", timedelta(hours=72)),
        ("fourth", timedelta(days=7)),
    ]

    for email_type, delay in schedules:
        scheduled_time = signup_time + delay

        # Create a ClockedSchedule for the specific time
        clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=scheduled_time)

        # Create or update the periodic task
        PeriodicTask.objects.update_or_create(
            name=f"onboarding_{email_type}_",  # Removed user_email for uniqueness
            defaults={
                "clocked": clocked,  # Required schedule type
                "task": "utils.tasks.send_onboarding_email",
                "args": json.dumps([user_email, email_type]),
                "one_off": True,
                "enabled": True,
            },
        )


class MarkUserAsPaymentCompleted(APIView):
    def post(self, request):
        user = request.user
        user.is_book_session_payment_completed = True
        user.save()
        return ResponseGenerator.response(
            data=SignUpSerializer(user).data,
            message="User payment updated",
            status=status.HTTP_200_OK,
        )


class ContactUsView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        first_name = request.data.get("first_name")
        email = request.data.get("email")
        message = request.data.get("message")
        last_name = request.data.get("last_name")
        # ContactUsEmail.objects.create(first_name=first_name,last_name=last_name,email=email, message=message)

        return ResponseGenerator.response(
            data={"status": True},
            status=status.HTTP_201_CREATED,
            message="Contact Us email sent successfully",
        )


class UserEmailListView(APIView):
    def get(self, request):
        emails = User.objects.values_list("email", flat=True)
        emails_list = list(emails)

        return ResponseGenerator.response(
            data=emails_list, message="Users emails", status=status.HTTP_200_OK
        )




class SaveUserSafeWordView(APIView):
    def post(self, request):
        safe_word = request.data.get("safeWord")
        if not safe_word:
            return ResponseGenerator.response(
                data={},
                message="Safe word not found",
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user.safe_word = safe_word
        user.save()
        
        return ResponseGenerator.response(
            data=SignUpSerializer(user).data,
            status=status.HTTP_200_OK,
            message="User safeword updated"
        )

class GetUsersStats(APIView):
    def get(self, request):
        total_users = User.objects.all()
        starter_users = total_users.filter(planName__icontains="Starter").count()
        growth_users = total_users.filter(planName__icontains="Growth").count()
        scale__plan_users = total_users.filter(planName__icontains="Scale Plan").count()
        scale__plus_users = total_users.filter(planName__icontains="Scale Plus").count()

        return ResponseGenerator.response(
            data={
                "total_users": total_users.count(),
                "starter_users": starter_users,
                "growth_users": growth_users,
                "scale__plan_users": scale__plan_users,
                "scale__plus_users": scale__plus_users,
            },
            status=status.HTTP_200_OK,
            message="Calls retrieved",
        )


class GetUsersView(APIView):
    def get(self, request):
        queryLimit = settings.QUERY_LIMIT
        page = request.GET.get("page", 1)
        planName = request.GET.get("planName", "")
        user_status = request.GET.get("status", "")
        startingDate = request.GET.get("startingDate", "")
        endingDate = request.GET.get("endingDate", "")
        searchText = request.GET.get("searchText", "")
        requestPage = queryLimit * int(page)
        startingPage = (int(page) - 1) * queryLimit

        total = User.objects.all()
        users = total
        if planName:
            users = users.filter(Q(planName__icontains=planName))
        if searchText:
            users = users.filter(
                Q(email__icontains=searchText) | Q(full_name__icontains=searchText)
            )

        if user_status == "Inactive":
            users = users.filter(is_active=False)

        if user_status == "Active":
            users = users.filter(is_active=True)

        if startingDate:
            try:
                start_date = datetime.strptime(startingDate, "%Y-%m-%d").date()
                users = users.filter(date_joined__gte=start_date)
            except ValueError:
                pass

        if endingDate:
            try:
                end_date = datetime.strptime(endingDate, "%Y-%m-%d").date()
                users = users.filter(date_joined__lte=end_date)
            except ValueError:
                pass

        total = users
        users = users[int(startingPage) : requestPage]

        return ResponseGenerator.response(
            data={
                "data": SignUpSerializer(users, many=True).data,
                "total": total.count(),
            },
            status=status.HTTP_200_OK,
            message="users",
        )


class AddUserDeviceToken(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        user = request.user

        tokenInstance, created = DeviceToken.objects.get_or_create(user=user)
        tokenInstance.token = token
        tokenInstance.save()

        return ResponseGenerator.response(
            status=status.HTTP_201_CREATED,
            data={},
            message="Device token added successfully",
        )


class ValidateEmail(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.GET.get("email", "")
        return ResponseGenerator.response(
            data=User.objects.filter(email=email).exists(),
            message="Valid email",
            status=status.HTTP_200_OK,
        )


class UpdateAdminPassword(APIView):
    def put(self, request):
        try:
            user = request.user
            new_password = request.data.get("new_password")
            old_password = request.data.get("old_password")

            if not user.check_password(old_password):
                return ResponseGenerator.response(
                    data={},
                    message="Old password is incorrect",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not user.check_password(new_password):
                return ResponseGenerator.response(
                    data={},
                    message="New password is same as current password",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.password = make_password(new_password)
            user.save()

            serializer = SignUpSerializer(user)

            return ResponseGenerator.response(
                data=serializer.data,
                message="User password successfully",
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return ResponseGenerator.response(
                data={}, message="User not found", status=status.HTTP_404_NOT_FOUND
            )


class EditUserWithProfileImageView(APIView):
    def put(self, request):
        try:
            user = request.user
            user.full_name = request.data.get("full_name")
            user.email = request.data.get("email")
            profile_image = request.FILES.get("profile_image")
            if profile_image:
                user.profile_image = profile_image
            user.save()

            serializer = SignUpSerializer(user)

            return ResponseGenerator.response(
                data=serializer.data,
                message="User updated successfully",
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return ResponseGenerator.response(
                data={}, message="User not found", status=status.HTTP_404_NOT_FOUND
            )


class UsersStatsView(APIView):
    def get(self, request, *args, **kwargs):
        today = date.today()
        users = User.objects.all()
        total_users = users.filter(is_superuser=False)
        active_users = total_users.filter(is_active=True)
        suspended_users = total_users.filter(is_active=False)
        joined_today = total_users.filter(date_joined__date=today)

        return ResponseGenerator.response(
            data={
                "total_users": total_users.count(),
                "active_users": active_users.count(),
                "suspended_users": suspended_users.count(),
                "joined_today": joined_today.count(),
            },
            message="Stats for users",
            status=status.HTTP_200_OK,
        )


class EditUserView(APIView):
    def post(self, request):
        try:
            user = request.user

            serializer = SignUpSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ResponseGenerator.response(
                    data=serializer.data,
                    message="User updated successfully",
                    status=status.HTTP_200_OK,
                )
        except User.DoesNotExist:
            return ResponseGenerator.response(
                data={}, message="User not found", status=status.HTTP_404_NOT_FOUND
            )


class ToggleUserActiveState(APIView):
    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
            if user.is_active:
                user.is_active = False
            else:
                user.is_active = True
            user.save()
            return ResponseGenerator.response(
                data={},
                message="User status toggled successfully",
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return ResponseGenerator.response(
                data={}, message="User not found", status=status.HTTP_404_NOT_FOUND
            )


class GetPostAdministrators(APIView):
    def get(self, request):
        queryLimit = settings.QUERY_LIMIT
        page = request.GET.get("page", 1)
        requestPage = queryLimit * int(page)
        startingPage = (int(page) - 1) * queryLimit
        searchQuery = request.GET.get("searchQuery", "")
        user = User.objects.filter(
            Q(email__icontains=searchQuery)
            | Q(full_name__icontains=searchQuery)
            | Q(phone_number__icontains=searchQuery)
        ).filter(is_superuser=False)[int(startingPage) : requestPage]
        allUser = User.objects.filter(is_superuser=False)
        serializer = SignUpSerializer(user, many=True)
        return ResponseGenerator.response(
            data={"data": serializer.data, "total_count": allUser.count()},
            message="Users retrieved successfully",
            status=status.HTTP_200_OK,
        )


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = SignUpSerializer(data=request.data)
        email = request.data.get("email").lower()
        if User.objects.filter(email=email).exists():
            return ResponseGenerator.response(
                data={},
                message="User with this email already exists",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if s.is_valid():
            s.save()

            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            generateUserOTP(user)

            responseData = {
                "data": {**s.data, "email": email},
                "token": user.auth_token.key,
            }

            return ResponseGenerator.response(
                data=responseData,
                message="User  registered successfully",
                status=status.HTTP_201_CREATED,
            )
        return ResponseGenerator.response(
            message=s.errors, status=status.HTTP_400_BAD_REQUEST, data={}
        )


class ActivateUserEmail(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token, uidb64):
        try:
            uuid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uuid)
        except Exception as e:
            user = None

        if user and generateToken.check_token(user, token):
            user.is_active = True
            user.save()

            return render(
                request,
                "notification.html",
                {
                    "message": "User account activated successfully, please return to the login to continue process.",
                    "user": user,
                },
            )

        return render(
            request,
            "notification.html",
            {"message": "Sorry, there was an error activating your account"},
        )


class LoginUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = User.objects.filter(email__iexact=request.data.get("email"))
        isAdmin = request.data.get("isAdmin", False)

        if not user.exists():
            return ResponseGenerator.response(
                message="Email not found",
                data={},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.exists() and not user[0].is_active:
            return ResponseGenerator.response(
                message="Sorry User account is not activated",
                data={},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = user[0]
        checking_password = check_password(request.data.get("password"), user.password)

        if isAdmin and user and not user.is_superuser:
            return ResponseGenerator.response(
                message="Sorry User is not admin",
                data={},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if checking_password:

            return ResponseGenerator.response(
                data={
                    "data": SignUpSerializer(user).data,
                    "token": user.auth_token.key,
                },
                message="User logged in successfully",
                status=status.HTTP_200_OK,
            )
        return ResponseGenerator.response(
            data={},
            message="User Credentials are not correct",
            status=status.HTTP_404_NOT_FOUND,
        )


class UserMe(APIView):
    def get(self, request, id):
        user = User.objects.filter(id=id)

        if user.exists():
            return Response(
                data={"message": "User with this ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            data={
                "data": SignUpSerializer(instance=user[0]),
                "message": "User retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )


class DeleteUserWithEmail(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, email):
        try:
            user = User.objects.get(email=email)
            user.delete()
            return ResponseGenerator.response(
                data={},
                message="User deleted",
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist as e:
            return ResponseGenerator.response(
                data={},
                message="Error deleting user",
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserMeAuth(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        return ResponseGenerator.response(
            data=SignUpSerializer(user).data,
            message="User authenticated",
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        id = request.user.id
        user = User.objects.get(id=id).delete()

        return Response(
            data={
                "messgae": "User Deleted Successfully",
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutUser(APIView):

    def post(self, request):
        logout(request=request)
        return Response(data={"message": "User Logged Out Successfully"})


class GetUserReferalCode(APIView):

    def get(self, request):
        r = ReferalCode.objects.get(user=request.user)
        return Response(data=ReferalCodeSerializer(r).data, status=status.HTTP_200_OK)


class ForgotPasswordRequest(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        user = User.objects.filter(email__iexact=email)

        if not user.exists():
            return ResponseGenerator.response(
                data={},
                message="Sorry, User with this email does not exist",
                status=status.HTTP_400_BAD_REQUEST,
            )

        c = generateUserOTP(user[0].email)
        emailMessage = f"We received a request to reset the password for your account associated with this email address. If you didn't request a password reset, please ignore this email. To reset your password, please use the code below \n\n {c} "
        # message = render_to_string(
        #     "emails/message.html",
        #     {"message": emailMessage, "name": f"{user[0].full_name}"},
        # )
        # t = threading.Thread(
        #     target=send_email, args=("Your Password reset", message, [email])
        # )
        # t.start()

        return ResponseGenerator.response(
            message=f"Forgot Password code sent to email.",
            data=SignUpSerializer(user[0]).data,
            status=status.HTTP_200_OK,
        )


class ContinueForgotOTPPassword(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get("code")
        validatingOTP = validateOTPCode(code)
        if not validatingOTP.get("type"):
            return ResponseGenerator.response(
                data={},
                message=validatingOTP.get("message"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = validatingOTP.get("code").user

        return ResponseGenerator.response(
            data=SignUpSerializer(user).data,
            message="User authenticated successfully",
            status=status.HTTP_200_OK,
        )


class VerifyOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get("code")
        validatingOTP = validateOTPCode(code)
        if not validatingOTP.get("type"):
            return Response(
                data={
                    "error": validatingOTP.get("message"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = validatingOTP.get("code").user

        return ResponseGenerator.response(
            data=SignUpSerializer(user).data,
            message="User password updated successfully",
            status=status.HTTP_200_OK,
        )


class CompletePasswordReset(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        password = request.data.get("password")
        email = request.data.get("email")
        print(email)

        if not password:
            return ResponseGenerator.response(
                message="Please enter your password",
                data={},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_model().objects.get(email__iexact=email)

        user.set_password(password)
        user.save()

        return ResponseGenerator.response(
            data=SignUpSerializer(user).data,
            message="User password updated",
            status=status.HTTP_202_ACCEPTED,
        )


class GetUserWithID(APIView):
    def get(self, request, id):
        print("Here")
        try:
            user = User.objects.get(id=id)
            return ResponseGenerator.response(
                data=SignUpSerializer(user).data,
                message="User retrieved successfully",
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                data={"message": "User with this ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateUserPassword(APIView):
    def post(self, request):
        old_password = request.data.get("old_password")
        password = request.data.get("password")

        if not password:
            return Response(
                data={"message": "Please enter your password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_model().objects.get(id=request.user.id)

        if not user.check_password(old_password):
            return ResponseGenerator.response(
                data={},
                status=status.HTTP_400_BAD_REQUEST,
                message="Your old password is incorrect",
            )
        if user.check_password(password):
            return ResponseGenerator.response(
                data={},
                message="Error updating user password",
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return ResponseGenerator.response(
            data=SignUpSerializer(user).data,
            message="User password updated",
            status=status.HTTP_202_ACCEPTED,
        )


class UpdateUserBasicInformation(APIView):
    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        phone_number = request.data.get("phone_number")
        business_category = request.data.get("business_category")

        if not first_name:
            return Response(
                data={"message": "Please enter your first name"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not last_name:
            return Response(
                data={"message": "Please enter your last name"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not email:
            return Response(
                data={"message": "Please enter your email"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not phone_number:
            return Response(
                data={"message": "Please enter your phone number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.get(id=request.user.id)
        user.email = email
        user.phone_number = phone_number
        user.first_name = first_name
        user.last_name = last_name
        if business_category:
            user.business_category = business_category

        user.save()

        return Response(
            data={
                "message": "User profile updated",
                "user": SignUpSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DeleteAccount(APIView):
    def delete(self, request):
        user = request.user
        user = User.objects.get(email=user.email)
        user.delete()

        return Response(
            data={"message": "User account deleted successfully"},
            status=status.HTTP_202_ACCEPTED,
        )


class UpdateProfileImage(APIView):
    def patch(self, request):
        image = request.FILES.get("profile_image")
        user = request.user
        user.profile_image = image
        user.save()

        return Response(
            data={
                "message": "Profile image updated successfully",
                "user": SignUpSerializer(user).data,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class UpdateCVDocument(APIView):
    def patch(self, request):
        cv = request.FILES.get("cv")
        cover_letter = request.FILES.get("cover_letter")
        user = request.user

        if cv:
            user.cv = cv
        if cover_letter:
            user.cover_letter = cover_letter

        user.save()

        return Response(
            data={
                "message": "Profile image updated successfully",
                "user": SignUpSerializer(user).data,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class GetUserTokenWithEmail(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, email, *args, **kwargs):
        try:
            user = User.objects.get(email=email)
            return Response(
                data={
                    "token": user.auth_token.key,
                    "message": "User token found",
                }
            )
        except:
            return Response(
                data={"message": "User with this email does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateUser(APIView):
    def sendEmailNow(self, user: User, title: str, template: str, data: object):
        data_obj = {
            **data,
            "name": user.full_name.strip(),
        }
        message = render_to_string(template, data_obj)
        t = threading.Thread(
            target=send_email,
            args=(
                title,
                message,
                [user.email],
            ),
        )
        t.start()

    def post(self, request):
        user = request.user
        data = request.data
        signup_stage = data.get("signup_stage", "")
        send_payment_email = data.get("send_payment_email")

        if signup_stage == "ANSWERED":
            self.sendEmailNow(
                user=user,
                title="Spot secured",
                template="emails/secure_spot.html",
                data={},
            )
        if send_payment_email == "YES":
            amount = data.get("amount", "")
            planName = data.get("planName", "")
            invoice = Invoice.objects.create(
                user=user, amount=amount, planName=planName
            )
            self.sendEmailNow(
                user=user,
                title="Payment Invoice",
                template="emails/receipt.html",
                data={"inv": invoice, "ref_code": user.ref_code},
            )

        serializer = SignUpSerializer(instance=user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data, message="User updated", status=status.HTTP_200_OK
            )


class UpdateUserView(APIView):

    def patch(self, request):
        user = request.user

        serializer = SignUpSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseGenerator.response(
                data=serializer.data,
                message="User updated",
                status=status.HTTP_202_ACCEPTED,
            )

        return ResponseGenerator.response(
            data={}, message="user was not updated", status=status.HTTP_400_BAD_REQUEST
        )


class AccountQuestionsSerializerView(APIView):
    def get(self, request):
        user = request.user
        account_question = AccountQuestions.objects.get_or_create(user=user)
        account_question, created = account_question
        return ResponseGenerator.response(
            data=AccountQuestionsSerializer(account_question).data,
            message="Created",
            status=status.HTTP_201_CREATED,
        )

    def post(self, request):
        user = request.user
        data = request.data

        AccountQuestions.objects.update_or_create(
            user=user, defaults={"questions_answers": data}
        )

        return ResponseGenerator.response(
            data=True, message="Created", status=status.HTTP_200_OK
        )
