import os
import importlib
import logging
import json
from urllib.parse import parse_qs

import meetup

# Intializations that are not specific to each run
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# General help

def general_help(args):
    return 'Available commands: {}.'.format(', '.join(cmd_handlers.keys()))


def help_help():
    # TODO: Should the help be <cmd> help or help <cmd> ??
    return 'For help on a specific command enter: <cmd> help'


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
            cmd_handlers[cmd_name] = (cmd_hndlr, cmd_help)
    # Add in the 'help' command
    cmd_handlers['help'] = (general_help, help_help)


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
            # all text after the / command is a sinngle string so split out the cmd and any args
            all_args = data['text'][0].split()
            cmd = all_args[0]
            args = all_args[1:]

    if cmd in cmd_handlers:
        logger.info('Received command \'{}\' with args {}'.format(cmd, args))
        if len(args) > 0 and args[0] == 'help':
            # Get the command specific help
            body_text += cmd_handlers[cmd][1]()
        else:
            # Run the requested command and pass any additional args
            body_text += cmd_handlers[cmd][0](args)
    else:
        # We don't know how to do what the user wants
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
