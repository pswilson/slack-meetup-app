import os
import importlib
import json
from urllib.parse import parse_qs

import meetup


cmds_dir = 'cmds'
cmd_handlers = {}


def load_commands():
    # check the commands directory
    lst = os.listdir(cmds_dir)
    for fname in lst:
        if not fname.startswith('__') and fname.endswith('.py'):
            m = importlib.import_module(
                '{}.{}'.format(cmds_dir, fname.split('.')[0]))
            # TODO: Verify this module has a registration method
            cmd_name, cmd_hndlr, cmd_help = m.get_registration()
            # TODO: Save the help handler
            cmd_handlers[cmd_name] = cmd_hndlr


# Call this outside the handler so it only happens on a cold start rather than every call
load_commands()


#
# Entry point for Lambda ... start here!

def handler(event, context):
    if not meetup.verify_request(event):
        body = {
            'response_type': 'ephemeral',
            'text': 'Forbidden'
        }

        response = {
            'statusCode': 403,
            'body': json.dumps(body)
        }

        return response

    body_text = ''
    data = []
    cmd = ''
    args = []

    if 'body' in event:
        data = parse_qs(event['body'])
        if 'text' in data:
            cmd = data['text'][0]
            args = data['text'][1:]

    if cmd in cmd_handlers:
        body_text += cmd_handlers[cmd](args)
    else:
        body_text += 'Command not recognized. Try one of ({}).'.format('|'.join(cmd_handlers.keys()))

    # TODO: Encode body text (specifically &, <, and >)

    body = {
        'response_type': 'in_channel',
        'text': body_text
    }

    response = {
        'statusCode': 200,
        'body': json.dumps(body)
    }

    return response
