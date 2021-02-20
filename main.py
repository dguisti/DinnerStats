from __future__ import print_function
import datetime
import pickle
import os.path
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    #print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='rtfpqnsch2c0t3rl591dhf5pl8@group.calendar.google.com', singleEvents=True,
                                          orderBy='startTime').execute()  # timeMin=now
    events = events_result.get('items', [])

    meals = {}

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        rawText = event['summary']
        items = [y.strip().lower().title()
                 for y in re.split(',| and', rawText) if y != ""]
        for meal in items:
            if meal in meals:
                meals[meal]["lastDate"] = start
                meals[meal]["count"] += 1
                meals[meal]["pastDates"].append(start)
            else:
                meals[meal] = {"lastDate:": start,
                               "count": 1, "pastDates": []}

    for meal in meals:
        print(f"{meal}: {meals[meal]['count']}")


if __name__ == '__main__':
    main()
