from __future__ import print_function

import base64
import os
import re

from datetime import datetime, timedelta

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
    out: list[dict[str, str]] = []

    results = service.users().threads().list(userId="me", q=query).execute() # type: ignore

    # https://developers.google.com/resources/api-libraries/documentation/gmail/v1/python/latest/gmail_v1.users.messages.html
    for thread in results.get("threads", []):
        message = service.users().threads().get(userId="me", id=thread["id"]).execute()["messages"][0]

        date = message["internalDate"]
        date = datetime.fromtimestamp(int(date) / 1000)

        # wow
        body = message["payload"]["parts"][0]

        while 'parts' in body:
            body = body['parts'][0]

        body = body['body']['data']

        out.append(dict(
            body=base64url_decode(body).lower(),
            date=date,
        ))

    return out

def base64url_decode(data: str) -> str:
    """Decode a base64url encoded string."""
    # Pad the string with '=' characters to make its length a multiple of 4
    padding = "=" * ((4 - len(data) % 4) % 4)
    data += padding

    # Decode the base64url encoded string
    return base64.urlsafe_b64decode(data).decode("utf-8")


def format_date_mdy(d: datetime):
    """M/D/Y - used for spreadsheet"""
    return d.strftime("%m/%d/%Y")


def format_date(d: datetime):
    """Y/M/D - used for gmail querystring"""
    return d.strftime("%Y/%m/%d")


def get_last_day(m: datetime):
    """returns the last day of the month"""
    if m.month == 12:
        return datetime(m.year + 1, 1, 1) - timedelta(days=1)
    else:
        return datetime(m.year, m.month + 1, 1) - timedelta(days=1)

def get_emails_for_month(m: int):
    after = datetime(YEAR, m, 1)
    before = get_last_day(after)

    return get_emails(
        [
            "after:{0}".format(format_date(after)),
            "before:{0}".format(format_date(before + timedelta(days=1))),
        ]
    )


def get_data_for_month(m: int):
    emails = get_emails_for_month(m)
    output = []

    names = NAMES.split(", ")

    for name in names:
        name_parts = name.lower().split(" ")
        snippets = [
            email for email in emails if all([name in email['body'] for name in name_parts])
        ]

        for snippet in snippets:
            money = re.findall(r"(\$[\d,]+)\.", snippet['body'])

            if len(money) > 0:
                money = money[0].replace(",", "")
                output.append([name, format_date_mdy(snippet['date']), money])
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
