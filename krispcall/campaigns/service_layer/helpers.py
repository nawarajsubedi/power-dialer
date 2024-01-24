""" Helpers for the campaign component"""

from typing import Dict, List, Union


def build_callable(contact_data: List[Dict]):
    """Takes in the list of Dict
    and return list of callable object
    type : List[Dict]
    # [{"Contact Name": "test", "Phone Number": "1234567890"}]
    {
        "numbers" : ["+919999999999", "+919999999999"],
        "reattempt_list" : {}, // empty list for now
    }
    """
    return {
        "numbers": [data.get("Phone Number") for data in contact_data],
        "reattempt_list": {},
    }


def build_callable_list(contact_data: Union[List[Dict], None]):
    """Takes in the list of Dict or Nonetype
    and return list of callable object or empty dict
    type : Union[List[Dict], None]
    # [{"Contact Name": "test", "Phone Number": "1234567890"}]
    {
        "numbers" : ["+919999999999", "+919999999999"],
        "reattempt_list" : {}, // empty list for now
    }
    """
    if contact_data is None:
        return {}
    return build_callable(contact_data)
