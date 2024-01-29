from twilio.base.exceptions import TwilioRestException
from .twilio_requests import TwilioRequestResource


class UseLimitsResource:
    """Default usage limit triggers provided by twilio"""

    def __init__(self, account_sid, auth_token, base_url, app_url):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = base_url
        self.app_url = app_url
        self.client = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def create_sms_limit(self, friendly_name, frequency, trigger_value=10):
        """Create usage limit for the SMS
        @args
        - friendly name
        - frequency
        - trigger value
        """
        url = f"{self.base_url}/Accounts/{self.account_sid}/Triggers.json"
        data = {
            "TriggerValue": trigger_value,
            "TriggerBy": "price",
            "FriendlyName": friendly_name,
            "Recurring": frequency,
            "CallbackUrl": f"{self.app_url}/twilio_callbacks/circuit_breaker/{self.account_sid}",
            "UsageCategory": "sms",
        }
        try:
            response = await self.client.post(url=url, payload=data)
            return response
        except Exception as error:
            raise TwilioRestException(
                msg=error,  # type: ignore
                code=400,
                status=400,
                uri=url,
            ) from error

    async def create_usage_all_limit(
        self, friendly_name, frequency="daily", trigger_value=100
    ):
        """Create and set limits for call based on the price
        @args
        -frequency : time frequency range
        - friendly_name : trigger friendly name,
        - trigger value : value of trigger
        """
        trigger_value = 1
        url = f"{self.base_url}/Accounts/{self.account_sid}/Usage/Triggers.json"
        data = {
            "TriggerValue": trigger_value,
            "TriggerBy": "price",
            "FriendlyName": friendly_name,
            "Recurring": frequency,
            "CallbackUrl": f"{self.app_url}/twilio_callbacks/circuit_breaker/{self.account_sid}",
            "UsageCategory": "totalprice",
        }
        try:
            response = await self.client.post(url=url, payload=data)
            return response
        except Exception as error:
            raise TwilioRestException(
                msg=str(error),
                code=400,
                status=400,
                uri=url,
            ) from error
