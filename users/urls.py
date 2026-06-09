from django.urls import path
from .views import (
    ActivateUserEmail,
    CompletePasswordReset,
    VerifyOTP,
    DeleteUserWithEmail,
    ForgotPasswordRequest,
    GetUserReferalCode,
    MarkUserAsPaymentCompleted,
    GetUserWithID,
    GetUsersStats,
    GetUsersView,
    LoginUserView,
    UpdateProfileImage,
    UpdateUser,
    UpdateUserBasicInformation,
    UpdateUserPassword,
    UpdateUserView,
    UserMe,
    LogoutUser,
    UserMeAuth,
    GetUserTokenWithEmail,
    RegisterUserView,
    EditUserWithProfileImageView,
    GetPostAdministrators,
    EditUserView,
    ToggleUserActiveState,
    UsersStatsView,
    UpdateAdminPassword,
    AddUserDeviceToken,
    ValidateEmail,
    UserEmailListView,
    ContactUsView,
    AccountQuestionsSerializerView,
    ContinueForgotOTPPassword
)


urlpatterns = [
    ###ADMIN
    path(
        "",
        GetUsersView.as_view(),
    ),
    path("update_user_as_paid/", MarkUserAsPaymentCompleted.as_view()),
    path("get_users_emails/", UserEmailListView.as_view()),
    path("users_stats/", GetUsersStats.as_view()),
    path(
        "get_users/",
        GetPostAdministrators.as_view(),
    ),
    path(
        "update_user_token/",
        AddUserDeviceToken.as_view(),
    ),
    path(
        "get_users_stats/",
        UsersStatsView.as_view(),
    ),
    path("toggle_user_active_state/<int:id>/", ToggleUserActiveState.as_view()),
    path(
        "edit_user_with_profile_image/",
        EditUserWithProfileImageView.as_view(),
    ),
    path("update_admin_password/", UpdateAdminPassword.as_view()),
    path(
        "edit_user/",
        EditUserView.as_view(),
    ),
    path(
        "validate_email/",
        ValidateEmail.as_view(),
    ),
    ##USER
    path("login/", LoginUserView.as_view()),
    path("register/", RegisterUserView.as_view()),
    path("logout/", LogoutUser.as_view(), name="logout"),
    path("me/", UserMeAuth.as_view(), name="user_me_auth"),
    path(
        "get_user_referal_code/",
        GetUserReferalCode.as_view(),
        name="get_user_referal_code",
    ),
    path(
        "continue_forgot_password/",
        ContinueForgotOTPPassword.as_view(),
        name="continue_forgot_password",
    ),
    path("forgot_password/", ForgotPasswordRequest.as_view(), name="forgot_password"),
    path(
        "verify_otp/",
        VerifyOTP.as_view(),
        name="verify_otp",
    ),
    path(
        "complete_password_reset/",
        CompletePasswordReset.as_view(),
        name="complete_password_reset",
    ),
    path(
        "delete_user_with_email/<email>/",
        DeleteUserWithEmail.as_view(),
        name="delete_user",
    ),
    path(
        "activate_account/<token>/<uidb64>/",
        ActivateUserEmail.as_view(),
        name="activateUserAccount",
    ),
    path(
        "update_user_basic_informations/",
        UpdateUserBasicInformation.as_view(),
        name="update_user_basic_informations",
    ),
    path(
        "update_profile_image/",
        UpdateProfileImage.as_view(),
        name="update_profile_image",
    ),
    path(
        "update_user_password/",
        UpdateUserPassword.as_view(),
        name="update_user_password",
    ),
    path(
        "update_user/",
        UpdateUser.as_view(),
    ),
    path("contact_us/", ContactUsView.as_view()),
    path("get_user/<id>/", GetUserWithID.as_view(), name="get_user"),
    path("me/<int:id>/", UserMe.as_view(), name="user_me"),
    path("get_user_token_with_email/<email>/", GetUserTokenWithEmail.as_view()),
    path("update/", UpdateUserView.as_view()),
    path(
        "update_account_set_question_and_answers/",
        AccountQuestionsSerializerView.as_view(),
    ),
]
