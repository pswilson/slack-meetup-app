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


def next_group_event(group_url):
    """
    To get the next event ...
    scroll=next_upcoming
    page=1

    https://api.meetup.com/Frederick-Startup-Community/events?scroll=next_upcoming&page=1
    """
    filter_params = {'page': 1, 'scroll': 'next_upcoming'}

    # For Testing
    # filter_params = {'page': 1, 'no_earlier_than': '2018-10-20T00:00:00.000'}
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

    events = r.json()
    if len(events) == 0:
        return None

    return events[0]


def format_event(event):
    if event:
        text = '{} @{}\n'.format(
            event['local_date'], event['local_time'])
        text += '{}\n{}\n'.format(
            event['group']['name'], event['name'])
        if 'venue' in event:
            text += 'at {}\n'.format(
                event['venue']['name'])
        text += '{} yes RSVPs\n'.format(event['yes_rsvp_count'])
        text += '({})\n'.format(event['link'])
    else:
        text = 'No Event\n'

    return text


def next_event(args):
    all_events = {}
    for url_name in config.group_urls:
        event = next_group_event(url_name)
        if event and 'time' in event:
            event_time = event['time']
            if event_time not in all_events:
                all_events[event_time] = []
            all_events[event_time].append(event)

    if len(all_events) > 0:
        next_events_key = sorted(all_events.keys())[0]
        # Note: We may have more than one event at the same time
        next_events = all_events[next_events_key]

        msg_text = 'Next Meetup:\n'
        for next_event in next_events:
            msg_text += format_event(next_event) + '\n'
    else:
        msg_text = 'No upcoming events'

    return msg_text


def help_cmd():
    return '{} - gets the next upcoming event(s) across all configured groups.'.format(cmd_name)


def get_registration():
    return (cmd_name, next_event, help_cmd)
