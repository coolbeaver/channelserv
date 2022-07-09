
import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials

from config import *


class Sheets:
    creds = None

    def __init__(self):

        creds_json = os.path.dirname(__file__) + "/cre.json"
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes=[
            'https://www.googleapis.com/auth/spreadsheets'])

    @staticmethod
    def read_sheets(creds):
        try:
            service = build('sheets', 'v4', credentials=creds)

            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = list(map(tuple, result.get('values', ())))
            return values

        except HttpError as err:
            print(err)


