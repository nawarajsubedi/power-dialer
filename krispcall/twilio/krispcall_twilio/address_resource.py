from .type import NumberAddress
from .twilio_requests import TwilioRequestResource
from .endpoints import convert_dict_to_pascal_case


class AddressResource:
    # task
    def __init__(self, account_sid, auth_token, base_url) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.base_url = base_url
        self.client = TwilioRequestResource(
            account_sid=account_sid, auth_token=auth_token
        )

    async def create_address(self, address: NumberAddress):
        payload = address.dict(exclude_none=True)
        payload = convert_dict_to_pascal_case(payload)
        url = f"{self.base_url}/Accounts/{self.account_sid}/Addresses.json"

        return await self.client.post(url=url, payload=payload)

    async def all_addresses(self, limit):
        url = (
            f"{self.base_url}/Accounts/{self.account_sid}/"
            f"Addresses.json?PageSize={limit}"
        )
        return await self.client.get(url=url)

    async def get_address_from_country(self, iso_country: str):
        url = (
            f"{self.base_url}/Accounts/{self.account_sid}/"
            f"Addresses.json?IsoCountry={iso_country}"
        )
        return await self.client.get(url=url)

    async def update_address(self):
        raise NotImplementedError

    async def delete_address(self):
        raise NotImplementedError
