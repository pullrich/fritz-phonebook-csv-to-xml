import click
import csv
import numpy
import sys

from typing import List, Dict, Any, Tuple, Union, Callable, NewType

PhonebookName = NewType("PhonebookName", str)


class Template:
    def base(self) -> str:
        # We have to start with the XML declaration on the first line, or we would get invalid XML.
        return """<?xml version="1.0" encoding="utf-8"?>
<phonebooks>
    <phonebook owner="1" name="{phonebook-name}">
        {contacts-will-be-placed-here}
    </phonebook>
</phonebooks>
"""

    def contact(self) -> str:
        return """
        <contact>
            <category>0</category>
            <person>
                <realName>{real-name}</realName>
            </person>
            <telephony nid="3">
                <number type="home" vanity="" prio="1" id="0">{home-phone-number}</number>
                <number type="mobile" vanity="" prio="0" id="1">{mobile-phone-number}</number>
                <number type="work" vanity="" prio="" id="2"></number>
            </telephony>
            <services />
            <setup />
            <uniqueid></uniqueid>
        </contact>
        """


def all_expected_columns_present_in_csv(
    csv_dict_reader, expected_column_headers
) -> Tuple[bool, List[str]]:
    """Returns True and an empty list if all expected colum headers are present.
    Returns False and a list of string if there are column headers missing. The list contains the missing column names.
    """

    diff_list = numpy.setdiff1d(expected_column_headers, csv_dict_reader.fieldnames)
    return len(diff_list) == 0, diff_list


def build_phonebook(
    phonebook_name: PhonebookName, phonebook_template: str, contacts_block: str
) -> str:
    return phonebook_template.replace("{phonebook-name}", phonebook_name).replace(
        "{contacts-will-be-placed-here}", contacts_block
    )


@click.command()
@click.option(
    "-input_file",
    type=click.Path(exists=True, readable=True, resolve_path=True),
    help="CSV input file",
    required=False,
)
@click.option(
    "-output_file",
    type=click.Path(exists=False, resolve_path=True),
    help="Fritz phone book output file",
    required=False,
)
def make_all(input_file: str, output_file: str):
    expected_column_headers: List[str] = ["realName", "home-number", "mobile-number"]

    with open(input_file, newline="") as csvfile:
        data_reader = csv.DictReader(
            csvfile, delimiter=",", quotechar='"'
        )  # TODO: Make these configurable.

        success, missing_columns = all_expected_columns_present_in_csv(
            data_reader, expected_column_headers
        )
        if success:
            print("Good! All expected columns are present.")
        else:
            sys.exit(
                "Fail! Missing columns: {0} - stopping execution".format(
                    missing_columns
                )
            )

        # all_contacts = contacts_from_csv(data_reader)
        # print("Found {count} contacts".format(count=len(all_contacts)))

    pass


if __name__ == "__main__":
    make_all()  # pylint: disable=no-value-for-parameter

