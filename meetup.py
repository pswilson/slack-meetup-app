import os
import re
import json
from urllib.parse import parse_qs
import hmac
import hashlib

import requests


signing_secret = os.environ['SLACK_SIGNING_SECRET']

api_base = 'https://api.meetup.com'

events_api_path = 'events'
members_api_path = 'members'
rsvps_api_path = 'rsvps'


#
# Helpers

def parse_link_header(hdr):

    # NOTE: Multiple link header values may be returned
    #       which will be combined into a single comma separated list by the requests library

    # link header will look something like this ...
    #   <https://api.meetup.com/Frederick-Startup-Community/members?sign=true&page=100&offset=1>; rel="next"
    # or possibly ..
    #   <https://api.meetup.com/Frederick-Startup-Community/members?sign=true&page=100&offset=1>; rel="prev", <https://api.meetup.com/Frederick-Startup-Community/members?sign=true&page=100&offset=3>; rel="next"

    # Basic regex pattern to handle a correctly formatted link header value
    pattern = '<(?P<url>(.+))> *; *rel="(?P<ref>(prev|next))"'

    links = {}

    if len(hdr) > 0:
        hdr_parts = hdr.split(',')
        for hdr_part in hdr_parts:
            m = re.search(pattern, hdr_part)
            if m:
                links[m.group('ref')] = m.group('url')

    return links


def get_paged_results(start_url):
    # Note: Need to use page and offset to get more than 200 users
    # page is max number of items returned per request (max of 200)
    # offset is 0 based page number
    # (NOTE: an offset greater than the actual number of pages based on the
    #        number of possible results seems to always return the last page of data)
    # Total number of possible responses is in the header "x-total-count"
    # link header contains a link to the "next" and/or "prev" page

    members = {}

    print("Getting members from {} ".format(start_url), end='', flush=True)

    next_url = start_url
    while next_url:
        r = requests.get(next_url)
        if r.status_code != 200:
            if r.status_code == 429:
                print('Rate limited: {}'.format(r.text()))
            else:
                print('Error fetching data: {}'.format(r.status_code))
            break

        batch_members = r.json()
        # For now we're just keeping the id and name
        for member in batch_members:
            members[str(member['id'])] = member['name']

        next_url = ''
        if 'link' in r.headers:
            links = parse_link_header(r.headers['link'])
            if 'next' in links:
                next_url = links['next']
                print('.', end='', flush=True)

    print()  # finish out the line

    return members

#
# Message verification

def calc_signature(req_timestamp, req_body):
    hash_data = str.encode('v0:' + str(req_timestamp) + ':' + req_body)
    request_hash = 'v0=' + \
        hmac.new(str.encode(signing_secret),
                 hash_data, hashlib.sha256).hexdigest()
    return request_hash


def verify_request(event):
    slack_timestamp = ''
    slack_signature = ''
    if 'headers' in event:
        if 'X-Slack-Request-Timestamp' in event['headers']:
            slack_timestamp = event['headers']['X-Slack-Request-Timestamp']
        if 'X-Slack-Signature' in event['headers']:
            slack_signature = event['headers']['X-Slack-Signature']
    # TODO: Add a timestamp check to prevent replays
    req_body = ''
    if 'body' in event:
        req_body = event['body']
    sig = calc_signature(slack_timestamp, req_body)

    return hmac.compare_digest(slack_signature, sig)
