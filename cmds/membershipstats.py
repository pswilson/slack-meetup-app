import logging

import requests

import meetup
import config

# Intializations that are not specific to each run
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# Membership Stats

cmd_name = 'stats'


def format_group(group):
    group_fields = []

    # If we have a group to work with ...
    # Send back an array of two fields - name/link, membership count
    # These two fields end up as a row in the output
    if group:
        group_fields += [{
            'value': '<{}|{}>'.format(group['link'], group['name']),
            'short': True
        }]
        group_fields += [{
            'value': '{} members'.format(group['members']),
            'short': True
        }]
    else:
        logger.error('No group info provided')

    return group_fields


def get_group_info(group_url):
    request_url = '{}/{}'.format(meetup.api_base, group_url)
    r = requests.get(request_url)
    if r.status_code != 200:
        # TODO: Implement on a better error handling approach
        if r.status_code == 429:
            logger.error('Rate limited: {}'.format(r.text()))
        else:
            logger.error('Error fetching data: {}'.format(r.status_code))
        return None

    return r.json()


def membership_stats(args):
    # TODO: Might want to use some sort of templating for the output??
    # We're going to build up a message with attachements for each group and membership count
    # See the Slack Messages docs (https://api.slack.com/docs/messages) for more info on the structure of the response
    resp = {
        'attachments': [
            {
                'mrkdwn_in': ['text', 'pretext'],
                'pretext': '*Membership Stats:*',
                'fields': [],
                'color': 'good'
            }
        ]
    }

    for url_name in config.group_urls:
        group_info = get_group_info(url_name)
        resp['attachments'][0]['fields'] += (format_group(group_info))

    return resp


def help_cmd():
    return '{} - gets membership counts for all configured groups.'.format(cmd_name)


def get_registration():
    return (cmd_name, membership_stats, help_cmd)
