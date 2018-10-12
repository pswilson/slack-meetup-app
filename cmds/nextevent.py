import logging

import requests

import meetup
import config

# Intializations that are not specific to each run
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# Next Event(s)

cmd_name = 'next'


def next_group_events(group_url, num_events=1):
    """
    To get the next event ...
    scroll=next_upcoming
    page=1

    https://api.meetup.com/Frederick-Startup-Community/events?scroll=next_upcoming&page=1
    """
    filter_params = {'page': num_events, 'scroll': 'next_upcoming'}

    # For Testing
    # filter_params = {'page': num_events, 'no_earlier_than': '2018-10-20T00:00:00.000'}
    # date_range_params = {'no_later_than': '2018-10-21T00:00:00.000'}

    request_url = '{}/{}/{}'.format(meetup.api_base, group_url, meetup.events_api_path)
    r = requests.get(request_url, params=filter_params)
    if r.status_code != 200:
        # TODO: Implement on a better error handling approach
        if r.status_code == 429:
            logger.error('Rate limited: {}'.format(r.text()))
        else:
            logger.error('Error fetching data: {}'.format(r.status_code))
        return None

    return r.json()


def format_event_short(event):
    if event:
        event_out = {
            'text': '',
            'color': '#0576b9',
            'fields': [
                {
                    'value': '{} - <{}|{}>\n<!date^{}^{{time}} {{date_long}}|{} @{}>'.format(event['group']['name'], event['link'], event['name'], int(event['time']/1000),  event['local_date'],  event['local_time']),
                    'short': False
                }
            ]
        }
        return event_out
    else:
        return {}


def format_event(event):
    if event:
        event_out = {
            'title': event['name'],
            'title_link': event['link'],
            'fallback': '{}: {}'.format(event['name'], event['link']),
            'text': '{}\n<!date^{}^{{time}} {{date_long}}|{} @{}> at {}'.format(event['group']['name'], int(event['time']/1000), event['local_date'], event['local_time'], event['venue']['name']),
            'fields': [
                {
                    'title': 'RSVPs',
                    'value':  event['yes_rsvp_count'],
                    'short': True
                },
                {
                    'title': 'Waitlist',
                    'value':  event['waitlist_count'],
                    'short': True
                }
            ],
            'color': '#008952'
        }
        return event_out
    else:
        return {}


def format_events(events, formatter):
    # Note: We may have more than one event at the same time
    formatted_events = []
    for event in events:
        formatted_events.append(formatter(event))
    return formatted_events


def next_event(args):
    resp = {
        'attachments': [
            {
                'mrkdwn_in': ['pretext'],
                'pretext': '*Next:*'
            }
        ]
    }

    all_events = {}
    for url_name in sorted(config.group_urls):
        # Getting 2 next events for each group in case no other groups have a next event
        # That way we're more likely to always fill out the next and upcoming blocks
        events = next_group_events(url_name, 2)
        for event in events:
            if event and 'time' in event:
                event_time = event['time']
                if event_time not in all_events:
                    all_events[event_time] = []
                all_events[event_time].append(event)

    sorted_times = sorted(all_events.keys())

    if len(sorted_times) > 0:
        resp['attachments'] += format_events(all_events[sorted_times[0]], format_event)
        if len(sorted_times) > 1:
            resp['attachments'].append({
                'mrkdwn_in': ['pretext'],
                'pretext': '*Upcoming:*'
            })
            resp['attachments'] += format_events(all_events[sorted_times[1]], format_event_short)
    else:
        resp['attachments'].append({'text': 'No upcoming events scheduled'})

    return resp


def help_cmd():
    return '{} - gets the next upcoming event(s) across all configured groups.'.format(cmd_name)


def get_registration():
    return (cmd_name, next_event, help_cmd)
