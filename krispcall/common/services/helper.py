from functools import reduce

def change_camel_case_to_snake(camel_case: str):
    return reduce(
        lambda x, y: x + ("_" if y.isupper() else "") + y, camel_case
    ).lower()

def convert_dict_to_snake_case(dictionary: dict):
    return {
        change_camel_case_to_snake(key): value
        for key, value in dictionary.items()
    }

