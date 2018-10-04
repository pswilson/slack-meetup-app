import requests

import meetup
import config

#
# Membership Stats

cmd_name = 'stats'


def format_group(group):
    if group:
        text = '{}  ({} members)\n'.format(group['name'], group['members'])
    else:
        text = "No Group\n"

    return text


def get_group_info(group_url):
    request_url = '{}/{}'.format(meetup.api_base, group_url)
    r = requests.get(request_url)
    if r.status_code != 200:
        if r.status_code == 429:
            print('Rate limited: {}'.format(r.text()))
        else:
            print('Error fetching data: {}'.format(r.status_code))

    return r.json()


def membership_stats(args):
    body_text = 'Membership Stats:\n'

    for url_name in config.group_urls:
        group_info = get_group_info(url_name)
        body_text += format_group(group_info)

    return body_text


def help_cmd():
    return '{} - gets membership counts for all configured groups.'.format(cmd_name)


def get_registration():
    return (cmd_name, membership_stats, help_cmd)