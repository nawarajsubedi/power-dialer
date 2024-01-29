from typing import List, Optional, Union
from .type import NumberAvailabilityParams
from urllib.parse import urlencode

BASE_URL = "https://api.twilio.com/2010-04-01"


def snake_case_to_pascal_case(snake_case: str) -> str:
    return snake_case.replace("_", " ").title().replace(" ", "")


def convert_dict_to_pascal_case(obj: dict) -> dict:
    pascal_keys = [snake_case_to_pascal_case(k) for k in obj.keys()]
    return dict(zip(pascal_keys, list(obj.values())))


def build_available_number_params(params: NumberAvailabilityParams) -> str:
    values = params.dict(exclude_none=True)
    query = convert_dict_to_pascal_case(values)
    return urlencode(query)


def build_available_country_path(sid: str, country: Optional[str]) -> str:
    if country is not None:
        return (
            f"{BASE_URL}/Accounts/{sid}/AvailablePhoneNumbers/{country}.json"
        )
    else:
        return f"{BASE_URL}/Accounts/{sid}/AvailablePhoneNumbers.json"


def build_available_number_path(
    sid: str,
    country_iso: str,
    params: NumberAvailabilityParams,
    type: Union[str, List[str]],
):
    if isinstance(type, str):
        query = build_available_number_params(params)
        return (
            f"{BASE_URL}/Accounts/{sid}/"
            f"AvailablePhoneNumbers/{country_iso}/{type}.json?{query}"
        )
    elif isinstance(type, list):
        page_size = params.page_size
        shared_size = int(page_size / len(type))
        paths = []
        for i, t in enumerate(type):
            if i < len(type) - 1:
                params.page_size = shared_size
                query = build_available_number_params(params)
                paths.append(
                    (
                        f"{BASE_URL}/Accounts/{sid}/AvailablePhoneNumbers/"
                        f"{country_iso}/{t}.json?{query}"
                    )
                )
            else:
                params.page_size = page_size - shared_size * (len(type) - 1)
                query = build_available_number_params(params)
                paths.append(
                    (
                        f"{BASE_URL}/Accounts/{sid}/AvailablePhoneNumbers/"
                        f"{country_iso}/{t}.json?{query}"
                    )
                )
        return paths
