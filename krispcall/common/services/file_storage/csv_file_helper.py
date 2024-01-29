import io
import re
import typing
import pandas as pd
from starlette.datastructures import UploadFile

from krispcall.common.error_handler.exceptions import CSVProcessingError, ColumnNotFound
# from krispcall.common.exceptions import (
#     InvalidPhoneNumber,
#     ColumnNotFound,
#     CSVProcessingError,
#     PermissionDenied,
# )

def clean_phone_number(text):
    ph_no = re.sub(r"\D", "", str(text))
    if ph_no:
        return f"+{ph_no}"
    return ""


async def process_contacts_csv(
    csv_file: UploadFile,
    contact_number_column: str = "phone number",
    contact_name_column: str = "full name",
    usecols: typing.List[str] = None,
    dtype: typing.Dict = None,
) -> typing.List[dict]:
    """
    Process a CSV file containing contact information.

    Parameters:
        - csv_file (UploadFile): CSV file to be processed.
        - contact_name_column (str): The CSV file header's label for the contact name column.
        - contact_number_column (str): The CSV file header's label for the contact number column.
        - usecols (list, optional): List of columns to be used. If None, all columns will be considered.
        - dtype (dict, optional): Dictionary specifying data types for columns.

    Returns:
        List[dict]: A list of dictionaries representing processed contacts.
    """
    contact_name_column = contact_name_column.title()  # contact name
    contact_number_column = contact_number_column.title()  # contact number

    # process csv file and get back data frame
    try:
        df = await csv_file_to_df(
            csv_file=csv_file,
            columns_to_clean=[contact_number_column],
            usecols=usecols,
            dtype=dtype,
        )
    # Incase of invalid csv, use cols error, catch and raise '400' in resolver
    except ValueError:
        raise CSVProcessingError()

    # clean phone number
    df[contact_number_column] = df[contact_number_column].apply(
        lambda num: clean_phone_number(num)
    )

    # remove duplicates from the contact number column and only keep last occurence
    df_clean = df.drop_duplicates(subset=contact_number_column, keep="last")

    # Sort contacts based on contact name in ascending order
    if contact_name_column in df.columns:
        df_clean = df_clean.sort_values(by=contact_name_column, ascending=True)

    # convert dataframe into python dictionary
    all_contacts = df_clean.to_dict("records")

    # saving contact history logs
    valid_contacts = [
        contact
        for contact in all_contacts
        if not len(contact.get(contact_number_column, "")) > 15
        and not len(contact.get(contact_name_column, "")) > 63
    ]

    return valid_contacts

# csv files helpers
async def csv_file_to_df(
    csv_file: UploadFile,
    usecols: typing.List[str] = None,
    dtype: typing.Dict = None,
    clean_csv: bool = True,
    columns_to_clean: typing.List[str] = None,
) -> pd.DataFrame:
    """
    Convert a CSV file to a pandas DataFrame.

    Parameters:
        - csv_file (UploadFile): CSV file to be converted.
        - usecols (list, optional): List of columns to be used. If None, all columns will be considered.
        - dtype (dict, optional): Dictionary specifying data types for columns.
        - clean_csv (bool, optional): Drop rows with Nan values if True.
        - columns_to_clean (list, optional): List of columns to be cleaned. Not required if clean_csv is false.

    Returns:
        pd.DataFrame: Converted DataFrame.
    """
    file_str = await csv_file.read()
    file_stream = io.StringIO(str(file_str, "utf-8"))

    df = pd.read_csv(
        file_stream,
        encoding="utf-8",
        usecols=usecols,
        na_values=[".", "??", "no value"],
        dtype=dtype,
    )

    # change first letter of each word in csv columns to upper case
    df.columns = [column.title() for column in df.columns]

    # drop rows with Nan values in given columns
    if clean_csv:
        if columns_to_clean:
            columns_to_clean = [column.title() for column in columns_to_clean]
            # check if columns_to_clean is in csv file
            for column in columns_to_clean:
                if column not in df.columns:
                    error_message = (
                        f"{column} column missing from the csv file!"
                    )
                    raise ColumnNotFound(error_message)

        df = df.dropna(subset=columns_to_clean)

    df = df.reset_index(drop=True)
    df = df.fillna("")

    return df