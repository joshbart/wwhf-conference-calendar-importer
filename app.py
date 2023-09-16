from datetime import datetime, timezone, timedelta
from re import search
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

def timezone_converter(input_timezone: str):
    normalized_timezone = input_timezone.strip()
    if normalized_timezone == "MDT":
        return timezone(-timedelta(hours=6))

def calculate_datetime(human_readable_time: str, machine_readable_date: datetime, machine_readable_timezone: timezone):
    try:
        time = datetime.strptime(human_readable_time, "%I:%M %p").time()
    except ValueError:
        stripped_time = search(r"\d{1,2}:\d{2} [ap]m", human_readable_time).group(0)
        time = datetime.strptime(stripped_time, "%I:%M %p").time()
    return datetime.combine(machine_readable_date, time, machine_readable_timezone)


if __name__ == "__main__":

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    url = "https://wildwesthackinfest.com/conference/deadwood-2023-conference-agenda-full/"
    request = Request(url=url, headers=headers)
    html = urlopen(request).read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for conference_event in soup.find_all(attrs={"class": "tribe-events-widget-events-list__event-details"}):
        event_date = datetime.strptime(conference_event.time["datetime"], "%Y-%m-%d")
        event_timezone = timezone_converter(conference_event.find(attrs={"class": "timezone"}).string)
        start_time = calculate_datetime(conference_event.find(attrs={"class": "tribe-event-date-start"}).string, event_date, event_timezone)
        end_time = calculate_datetime(conference_event.find(attrs={"class": "tribe-event-time"}).string, event_date, event_timezone)
        event_name = conference_event.find(attrs={"class": "tribe-events-widget-events-list__event-title-link tribe-common-anchor-thin"})["title"]
        event_url = conference_event.find(attrs={"class": "tribe-events-widget-events-list__event-title-link tribe-common-anchor-thin"})["href"]
        event_location = conference_event.find(attrs={"class": "tribe-common-b2--bold tribe-common-anchor-thin tribe-events-widget-events-list__event-venue-name"}).string.strip()
        
        event = {
            'summary': event_name,
            'location': event_location,
            'description': event_url,
            'start': {
                'dateTime': str(start_time)
            },
            'end': {
                'dateTime': str(end_time),
            }
        }

        print(event)

# event = service.events().insert(calendarId='primary', body=event).execute()
# print 'Event created: %s' % (event.get('htmlLink'))