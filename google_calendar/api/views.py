from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.views import View
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# Create your views here.

def home(request):
    return HttpResponse("hello")

class GoogleCalendarInitView(View):
    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRET_FILE,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri='http://127.0.0.1:8000/rest/v1/calendar/redirect/'
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        # Save the state in the session for later verification
        request.session['calendar_auth_state'] = state

        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        state = request.session.pop('calendar_auth_state', None)

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRET_FILE,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri='http://127.0.0.1:8000/rest/v1/calendar/redirect/'
        )
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
            state=state
        )

        credentials = flow.credentials

        # Use the credentials to make API requests
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        # Process the events and return the response
        # ...

        return HttpResponse("Events: {}".format(events))
