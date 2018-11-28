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
    # filter_params = {'page': num_events, 'no_earlier_than': '2018-11-15T11:00:00.000'}
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


# Format a single event
def format_event(event):
    if event:
        if 'venue' in event:
            venue_name = event['venue']['name']
        else:
            venue_name = 'TBD'

        event_out = {
            'mrkdwn_in': ['text', 'pretext'],
            'pretext': '*Next Meetup:*',
            'title': event['name'],
            'title_link': event['link'],
            'fallback': '{}: {}'.format(event['name'], event['link']),
            'text': '{}\n*<!date^{}^{{time}} {{date_long}}|{} @{}>* at {}'.format(event['group']['name'], int(event['time']/1000), event['local_date'], event['local_time'], venue_name),
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


def format_no_next_events():
    return {
        'pretext': 'Next Meetup:',
        'text': 'No upcoming events scheduled'
    }


'''
        {
            "mrkdwn_in": ["text", "pretext"],
            "pretext": "*Next Meetup - Concurrent Events:*\n<!date^1539640800^{time} {date_long}|2018-10-15 @18:00>"
        },
        {
            "mrkdwn_in": ["text", "pretext"],
            "color": "#008952",
            "text": "at *FITCI (downtown location)*\nFrederick Web Tech - <https://www.meetup.com/Frederick-Infosec/events/255294157/|Open Workshop>\nFrederick Startup Community - <https://www.meetup.com/Frederick-Infosec/events/255294157/|Open Workshop>\nFrederick Startup Community - <https://www.meetup.com/Frederick-Infosec/events/255294157/|Open Workshop>\nFrederick Startup Community - <https://www.meetup.com/Frederick-Infosec/events/255294157/|Open Workshop>",
            "footer": "28 total RSVPs (with 24 unique)"
        },
        {
            "mrkdwn_in": ["text", "pretext"],
            "color": "#008952",
            "text": "at *Hood College*\nFrederick WordPress Meetup - <https://www.meetup.com/Frederick-Infosec/events/255294157/|Open Workshop>",
            "footer": "6 RSVPs"
        },
'''
def format_next_events(events):
    # Assumption is that the events passed in here are all at the same time but may be at different venues
    formatted_events = []

    if events and len(events) > 0:
        if len(events) > 1:
            # Add Concurrent event header
            hdr_blk = {
                'mrkdwn_in': ['text', 'pretext']
            }
            pretext = '*Next Meetup - Concurrent Events:*'
            # Get time/date from first event
            pretext += '\n*<!date^{}^{{time}} {{date_long}}|{} @{}>*'.format(
                int(events[0]['time']/1000), events[0]['local_date'], events[0]['local_time'])
            hdr_blk['pretext'] = pretext
            formatted_events.append(hdr_blk)

            # group events by venue
            by_venue = {}
            for event in events:
                if 'venue' in event:
                    venue_id = event['venue']['id']
                else:
                    venue_id = -1
                if venue_id not in by_venue:
                    by_venue[venue_id] = []
                by_venue[venue_id].append(event)

            # Add each venue and events at that venue
            for venue_id in by_venue.keys():
                venue_blk = {
                    'mrkdwn_in': ['text', 'pretext'],
                    'color': '#008952'
                }
                total_rsvps = 0
                # Get the venue name from the first event
                event = by_venue[venue_id][0]
                if 'venue' in event:
                    venue_name = event['venue']['name']
                else:
                    venue_name = 'TBD'

                fmt_text = 'at *{}*'.format(venue_name)
                for event in by_venue[venue_id]:
                    fmt_text += '\n{}\n<{}|{}>'.format(event['group']['name'], event['link'], event['name'])
                    total_rsvps += event['yes_rsvp_count']
                    # (opt - get attendees/ids to determine a unique count)
                venue_blk['text'] = fmt_text
                venue_blk['footer'] = '{} total \'yes\' RSVPs'.format(total_rsvps)
                formatted_events.append(venue_blk)
        else:
            formatted_events.append(format_event(events[0]))

    return formatted_events

'''
        {
            "mrkdwn_in": ["text", "pretext"],
            "pretext": "*Upcoming - Concurrent Events:*\n<!date^1539640800^{time} {date_long}|2018-10-15 @18:00>"
        },
        {
            "fallback": "Single Packet Authorization (SPA): https://www.meetup.com/Frederick-Infosec/events/255294157/",
            "text": "Frederick Infosec - <https://www.meetup.com/Frederick-Infosec/events/255294157/|Single Packet Authorization (SPA)>\nCrypto and Blockchain - <https://www.meetup.com/Frederick-Infosec/events/255294157/|Intro to Bitcoin and Blockchain (SPA)>"
        }
'''
def format_upcoming_events(events):
    formatted_events = []

    if events and len(events) > 0:
        formatted_event = {
            'mrkdwn_in': ['text', 'pretext']
        }

        if len(events) > 1:
            pretext = '*Upcoming - Concurrent Events:*'
        else:
            pretext = '*Upcoming:*'

        # Get time/date from first event
        pretext += '\n*<!date^{}^{{time}} {{date_long}}|{} @{}>*'.format(
            int(events[0]['time']/1000), events[0]['local_date'], events[0]['local_time'])
        formatted_event['pretext'] = pretext

        fmt_text = ''
        for event in events:
            if fmt_text != '':
                fmt_text += '\n'
            fmt_text += '{} - <{}|{}>'.format(
                event['group']['name'], event['link'], event['name'])
        formatted_event['text'] = fmt_text

        formatted_events.append(formatted_event)

    return formatted_events


def build_resp(events):

    resp = {'attachments': []}

    if events and len(events) > 0:
        # get the event times in order
        sorted_times = sorted(events.keys())
        resp['attachments'] += format_next_events(events[sorted_times[0]])
        if len(events) > 1:
            resp['attachments'] += format_upcoming_events(events[sorted_times[1]])
    else:
        resp['attachments'].append(format_no_next_events())

    return resp


def next_event(args):
    all_events = {}
    for url_name in sorted(config.group_urls):
        # Getting 2 next events for each group in case no other groups have a next event
        # That way we're more likely to always fill out the next and upcoming blocks
        events = next_group_events(url_name, 2)
        # We're grouping events by time
        for event in events:
            if event and 'time' in event:
                event_time = event['time']
                if event_time not in all_events:
                    all_events[event_time] = []
                all_events[event_time].append(event)

    return build_resp(all_events)


def help_cmd():
    return '{} - gets the next upcoming event(s) across all configured groups.'.format(cmd_name)


def get_registration():
    return (cmd_name, next_event, help_cmd)
