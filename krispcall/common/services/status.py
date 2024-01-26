"""
error key for each error response from krispcall
"""
HTTP_200_OK = (200, "Ok")
HTTP_403_FORBIDDEN = (403, "forbidden")
HTTP_401_UNAUTHORIZED = (401, "unauthorized")
HTTP_500_INTERNAL_SERVER_ERROR = (500, "internal_server_error", "Internal Server Error")
HTTP_400_INVALID = (400, "validataion_error")
HTTP_403_TOKEN_EXPIRED = (403, "token_expired")
HTTP_401_TOKEN_EXPIRED = (401, "token_expired")
HTTP_404_DOES_NOT_EXISTS = (404, "does_not_exists")
HTTP_429_TOGGLE_RECHARGE_LIMIT_EXCEED = (
    429,
    "toggle_recharge_time_limit_exceed",
)


# user
HTTP_409_ALREADY_EXISTS = (409, "already_exists")
HTTP_409_USER_EXISTS = (409, "user_exists")
HTTP_409_ORGANIZATION_EXISTS = (409, "organization_exists")
HTTP_400_INVALID_INPUT = (400, "invalid_input")
HTTP_400_INVALID_EMAIL = (400, "invalid_email")
HTTP_400_INVALID_OLD_PASSWORD = (400, "invalid_old_password")
HTTP_401_INVALID_LOGIN_PASSWORD = (401, "invalid_login_password")
HTTP_401_INVALID_PASSWORD = (401, "invalid_password")

# foundation
HTTP_409_WORKSPACE_EXISTS = (409, "workspace_exists")
HTTP_400_INVALID_WORKSPACE = (400, "invalid_workspace")
HTTP_400_INVALID_LINK = (400, "invalid_link")
HTTP_400_LINK_EXPIRED = (400, "link_expired")
HTTP_400_INVALID_CODE = (400, "invalid_code")
HTTP_409_MEMBER_EXISTS = (409, "member_exists")
HTTP_400_ROLE_MISSING = (400, "role_missing")

# channel
HTTP_409_EMAIL_EXISTS = (409, "email_exists")
HTTP_409_INVITE_EMAIL_EXISTS = (409, "email_exists")
HTTP_409_PHONE_NUMBER_EXISTS = (409, "phone_number_exists")
HTTP_429_LIMIT_EXCEED = (429, "limit_exceed")
HTTP_409_CHECKOUT_NUMBER_DOESNOT_EXISTS = (
    409,
    "checkout number doesn't exists",
)
HTTP_409_CHECKOUT_NUMBER_EXISTS = (
    409,
    "number not available",
)
HTTP_403_INVALID_TWILIO_CREDENTIALS = (
    401,
    "invalid twilio exception",
)
HTTP_401_NOT_AUTHORIZED = (
    403,
    "not authorized",
)
HTTP_409_CHECKOUT_NAME_EXISTS = (409, "Name exists")

# client
HTTP_409_TAG_NAME_EXISTS = (409, "tag_name_exists")

# organization
HTTP_409_TITLE_EXISTS = (409, "title_exists")

HTTP_404_PAYMENT_METHOD_NOT_AVAILABLE = (
    404,
    "payment_method_not_available",
)
HTTP_501_NOT_IMPLEMENTED = (501, "not_implemented")

# integration
HTTP_409_GOOGLE_ACCOUNT_EXISTS = (409, "google_account_already_exists")

HTTP_403_UNDER_REVIEW = (403, "under_review")

# HubSpot
HTTP_409_HUBSPOT_INTEGRATION_EXISTS = (
    409,
    "hubspot_integration_already_exists",
)

HTTP_401_HUBSPOT_INTERGRATION_FAILED = (
    401,
    "Couldn't create token, integration failed!!!!",
)

HTTP_401_HUBSPOT_CONTACT_UPDATE_FAILED = (
    401,
    "Couldn't update hubspot contact, contact update failed!!!!",
)

HTTP_404_CONTACT_OBJECT_NOT_FOUND = (
    404,
    "Contact with given properties not exists in hubspot!!!",
)

HTTP_401_FAILED_ENGAGEMENTS = (
    401,
    "Failed on create crm engagements",
)

# PipeDrive
HTTP_401_PIPEDRIVE_CONTACT_UPDATE_FAILED = (
    401,
    "Couldn't update pipedrive contact, contact update failed!!!!",
)
HTTP_401_REMOVE_CONTACT_FAILED = (
    401,
    "Failed on deleting contact.",
)

HTTP_401_DYNAMICS_INTERGRATION_FAILED = (
    401,
    "Couldn't create token, integration failed!!!!",
)

HTTP_401_CRISPCALL_INTERGRATION_FAILED = (
    401,
    "Couldn't create token, integration failed!!!!",
)
