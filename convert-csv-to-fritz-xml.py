import click
import csv
import numpy
import sys

from typing import List, Dict, Any, Tuple, Union, Callable, NewType

PhonebookName = NewType("PhonebookName", str)


class Contact:
    def __init__(self):
        self.realName = ""
        self.home_number = ""
        self.mobile_number = ""

    # def __str__(self):
    #     return self.__repr__()

    def __repr__(self):
        return str("Contact: " + self.realName)


class Template:

    @staticmethod
    def base() -> str:
        # We have to start with the XML declaration on the first line, or we would get invalid XML.
        return """<?xml version="1.0" encoding="utf-8"?>
<phonebooks>
    <phonebook owner="1" name="{phonebook-name}">
        {contacts-will-be-placed-here}
    </phonebook>
</phonebooks>
"""

    @staticmethod
    def contact() -> str:
        return """
        <contact>
            <category>0</category>
            <person>
                <realName>{real-name}</realName>
            </person>
            <telephony nid="3">
                <number type="home" vanity="" prio="1" id="0">{home-number}</number>
                <number type="mobile" vanity="" prio="0" id="1">{mobile-number}</number>
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

    # print(csv_dict_reader.fieldnames)
    # print(list(map(lambda name: name.lower(), csv_dict_reader.fieldnames)))

    diff_list = numpy.setdiff1d(expected_column_headers, csv_dict_reader.fieldnames)
    return len(diff_list) == 0, diff_list


def contacts_from_csv(data_reader: csv.DictReader):
    res = list()
    for row in data_reader:
        c = Contact()
        c.realName = row["realName"]
        c.home_number = row["home-number"]
        c.mobile_number = row["mobile-number"]
        res.append(c)

    return res


def build_phonebook(
    phonebook_name: PhonebookName, phonebook_template: str, contacts_block: str
) -> str:
    return phonebook_template.replace("{phonebook-name}", phonebook_name).replace(
        "{contacts-will-be-placed-here}", contacts_block
    )


def replace_placeholder_in_contact_xml_template(
    xml_template: str, contacts: List[Contact]
) -> List[str]:
    res = list()
    for c in contacts:
        res.append(
            xml_template.replace("{real-name}", c.realName)
            .replace("{home-number}", c.home_number)
            .replace("{mobile-number}", c.mobile_number)
        )

    return res


@click.command()
@click.option(
    "-phonebook_name",
    type=click.STRING,
    help="The name for the resulting Fritz phonebook. This will be displayed also in your handheld device.",
    required=True,
)
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
def make_all(input_file: str, output_file: str, phonebook_name: str):
    expected_column_headers: List[str] = ["realName", "home-number", "mobile-number"] # TODO: Change to one source of truth. Don't deal with these strings all the time.
    all_contacts: List[Contact] = []
    res_phonebook_name = PhonebookName(phonebook_name)

    with open(input_file, mode='r', newline="") as csvfile:
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

        all_contacts = contacts_from_csv(data_reader)
        # All contacts have been read. File can be closed.

    # print("Found {count} contacts".format(count=len(all_contacts)))
    # print(all_contacts)
    xml_contacts = replace_placeholder_in_contact_xml_template(
        Template.contact(), all_contacts
    )
    # print(xml_contacts)

    phonebook_xml = build_phonebook(res_phonebook_name, Template.base(), "".join(xml_contacts)) # TODO: Add to arguments.
    # print(phonebook_xml)

    with open(output_file, mode='w', newline="") as xml_file:
        xml_file.write(phonebook_xml)
    

if __name__ == "__main__":
    make_all()  # pylint: disable=no-value-for-parameter

