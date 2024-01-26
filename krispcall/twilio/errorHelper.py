CALL_FAILED_ERROR_MESSAGE = {
    21215: "Geographic Permission not enabled. Please contact support.",
    21214: "Invalid Number.",
    20005: "Account not active.",
    32205: "Geographic Permission not enabled.",
    10001: "Account is not active.",
    21203: "International calling not enabled.",
    21210: "Phone number not verified.",
    21217: "Phone number does not appear to be valid.",
}


def handle_call_failed(error_code: int):
    return CALL_FAILED_ERROR_MESSAGE.get(error_code)
