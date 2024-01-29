"""
"""


class RequestValidator:
    def validate_sms(self, body, message_to, message_from):
        # if not body or body == "":
        #     raise ValueError("Body cannot be empty")
        if len(body) >= 1600:
            raise ValueError(
                "Sms body should be less than or equal to 1600 characters"
            )

        if not message_to or message_to == "":
            raise ValueError("Message receiver cannot be empty")

        if not message_from or message_from == "":
            raise ValueError("Message sender cannot be empty")

    def validate_bulksms(self, body, message_to):
        if not body or body == "":
            raise ValueError("Body cannot be empty")
        if len(body) >= 1600:
            raise ValueError(
                "Sms body should be less than or equal to 1600 characters"
            )

        if not message_to or message_to == "":
            raise ValueError("Message receiver cannot be empty")

    def validate_create_sub_account(self, name):
        if not name or name == "":
            raise ValueError("Please enter a name for creating a subaccount")

    def validate_delete_sub_account(self, subaccount_sid):
        if not subaccount_sid or subaccount_sid == "":
            raise ValueError("Subaccount sid is required")

    def validate_move_numbers_to_sub_account(
        self, subaccount_sid, phonenumber_sid
    ):
        if not subaccount_sid or subaccount_sid == "":
            raise ValueError("Subaccount sid is required")

        if not phonenumber_sid or phonenumber_sid == "":
            raise ValueError("Phone number sid is required")

    def validate_get_sub_account_details(self, subaccount_sid):
        if not subaccount_sid or subaccount_sid == "":
            raise ValueError(
                "Subaccount sid is required for fetching its details"
            )

    def validate_suspend_subaccount(self, subaccount_sid):
        if not subaccount_sid or subaccount_sid == "":
            raise ValueError("Subaccount sid is required")

    def validate_re_activate_subaccount(self, subaccount_sid):
        if not subaccount_sid or subaccount_sid == "":
            raise ValueError("Subaccount sid is required")
