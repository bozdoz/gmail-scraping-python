from __future__ import print_function

import os
import re

from datetime import datetime

from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

YEAR = int(os.getenv("YEAR", 2022))
NAMES = os.getenv("NAMES", "")

# your oauth credentials file
CREDENTIALS = "credentials.json"
# generated google token file
TOKEN = "token.json"

# global google apis service
service = None


def get_service():
    """Call the Gmail API"""
    global service

    creds = get_creds()

    service = build("gmail", "v1", credentials=creds)


def get_creds():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN, "w") as token:
            token.write(creds.to_json())

    return creds


def get_query(q: list[str]):
    if q is None:
        q = []

    default = ["in:ETransfers", "-mint", "-communications"]

    q = default + q

    return " ".join(q)


def get_emails(q: list[str]):
    """gets thread snippets"""
    query = get_query(q)
    results = service.users().threads().list(userId="me", q=query).execute()
    threads = results.get("threads", [])

    return [a["snippet"].lower() for a in threads]


def format_date_mdy(d: datetime):
    """M/D/Y - used for spreadsheet"""
    return d.strftime("%m/%d/%Y")


def format_date(d: datetime):
    """Y/M/D - used for gmail querystring"""
    return d.strftime("%Y/%m/%d")


def get_emails_for_month(m: int):
    # TODO: we should just get all transactions for a month
    # otherwise, we get wrong year data
    before = datetime(YEAR, m, 15)
    prev_year = YEAR - 1 if m == 1 else YEAR
    prev_month = 12 if m == 1 else m - 1
    after = datetime(prev_year, prev_month, 15)

    return get_emails(
        [
            "after:{0}".format(format_date(after)),
            "before:{0}".format(format_date(before)),
        ]
    )


def get_data_for_month(m: int):
    date = format_date_mdy(datetime(YEAR, m, 1))
    emails = get_emails_for_month(m)
    output = []

    names = NAMES.split(", ")

    for name in names:
        name_parts = name.lower().split(" ")
        snippets = [
            email for email in emails if all([name in email for name in name_parts])
        ]

        for snippet in snippets:
            money = re.findall(r"(\$\d+)\.", snippet)

            if len(money) > 0:
                output.append([name, date, money[0]])
            else:
                print("couldn't find money: {0}".format(snippet))

    return "\n".join([",".join(a) for a in output]) + "\n"


def get_data_for_year():
    out = ""

    for x in range(1, 13):
        out += get_data_for_month(x)

    return out


def main():
    get_service()

    output = get_data_for_year()

    print(output)


if __name__ == "__main__":
    main()
