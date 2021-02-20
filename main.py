from __future__ import print_function
import datetime
import pickle
import os.path
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from string import capwords

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/spreadsheets']


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
    now = datetime.datetime.utcnow()
    nowstring = now.isoformat() + 'Z'  # 'Z' indicates UTC time
    #print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='rtfpqnsch2c0t3rl591dhf5pl8@group.calendar.google.com', singleEvents=True,
                                          orderBy='startTime', timeMax=nowstring).execute()  # timeMin=now
    events = events_result.get('items', [])

    meals = {}

    FREQUENCY_FACTOR = 1
    DELTA_FACTOR = 1
    TOTAL_FACTOR = 1
    T_FACTOR = 0.05

    for event in events:
        start = event['start'].get(
            'dateTime', event['start'].get('date'))[:10].split("-")
        start = [start[1], start[2], start[0]]
        start = "/".join([str(int(y)) for y in start])
        rawText = event['summary']
        items = [capwords(y.strip().lower())
                 for y in re.split(',| and', rawText) if y != ""]
        for meal in items:
            if meal in meals:
                meals[meal]["lastDate"] = start
                meals[meal]["count"] += 1
                meals[meal]["pastDates"].append(start)

                deltas = []
                for i in range(len(meals[meal]["pastDates"]) - 1):
                    initial = datetime.datetime.strptime(
                        meals[meal]["pastDates"][i], "%m/%d/%Y")
                    final = datetime.datetime.strptime(
                        meals[meal]["pastDates"][i + 1], "%m/%d/%Y")
                    delta = final - initial
                    deltas.append(delta.days)

                initial = datetime.datetime.strptime(
                    meals[meal]["pastDates"][-1], "%m/%d/%Y")
                final = datetime.datetime.strptime(
                    start, "%m/%d/%Y")
                delta = final - initial
                deltas.append(delta.days)

                deltaLast = now - datetime.datetime.strptime(start, "%m/%d/%Y")
                lastDays = deltaLast.days

                meals[meal]["score"] = round(sum(deltas)/len(deltas)*FREQUENCY_FACTOR +
                                             deltas[-1]*DELTA_FACTOR + meals[meal]["count"] *
                                             TOTAL_FACTOR + lastDays*T_FACTOR)

            else:
                deltaLast = now - datetime.datetime.strptime(start, "%m/%d/%Y")
                lastDays = deltaLast.days
                meals[meal] = {"lastDate": start,
                               "count": 1, "pastDates": [start], "score": round(lastDays*T_FACTOR)}

    meals = dict(
        sorted(meals.items(), key=lambda x: x[1]['score'], reverse=True))

    for meal in meals:
        print(f"{meal}: {meals[meal]['count']}")

    print("-------------------------------------------")

    SHEET_ID = '1UmLCwJMjzRG-7x2iAGDLn48KLy_TPSzJuvu7TQ2OJBg'
    SHEET_REFERENCE = 'Recipes!A2:E'

    sa = build('sheets', 'v4', credentials=creds)

    ac = sa.spreadsheets()

    values = [[recipe, meta['count'], meta['lastDate'], meta['score']]
              for recipe, meta in meals.items()]

    body = {
        'values': values
    }

    result = ac.values().update(spreadsheetId=SHEET_ID, range=SHEET_REFERENCE,
                                body=body, valueInputOption="USER_ENTERED").execute()

    print('{0} cells updated.'.format(result.get('updatedCells')))


if __name__ == '__main__':
    main()
