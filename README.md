# A Slack app for accessing Meetup info

### The Basics

This project implements a Slack / command for getting information across multiple Meetup groups.

### Configuration

A list of the urls (for the Meetup API) for the Meetup groups we are interested in is in config.py. You can tinker with this list as you want without needing to tweak any other code. Eventually this list could be in a db with additional commands for adding or removing groups. But this is a simple start.

#### Commands

Each of the commands is implemented in it's own file in the cmds directory. All of the commands in the directory are loaded at initialization time. For now the only requirement for a command is that it implements a get_registration() function which returns a tuple of the command name (str), command handler (func(args)), and a help command (func()). This could have been done (and was in an alternate version) with  classes but this should do as a basic start.

The commands that are currently implemented are (assuming you've created the Slack slash command as /meetup):

    /meetup stats

Shows membership counts for each of the configured Meetup groups.

    /meetup next

Shows the next scheduled Meetup for the configured groups. If the configured groups have concurrently scheduled events (either as a co-hosted event or as separate events but starting at the same time) all events will be listed.

### Building / Deploying

This uses the Serverless Framework to deploy to AWS. Find more [here](https://serverless.com). I'll eventually add some project specific notes.

### Installing

After deploying to AWS you'll need to configure Slack. Look [here](https://api.slack.com/slash-commands) for more on adding the app to Slack. Like building and deploying, I'll eventually add some notes here as well.

NOTE: The code does expect to get the slack signing secret from the environment. The current deployment doesn't do this for you. You'll need to add the key to the lambda environment (or fix up this project to do some better deployment.)

### Usage

Once all the pieces are in place you can use the command like other Slack / commands. If you don't specify a recognized (sub)command (i.e. currently stats or next) you'll be prompted with a list of the currently loaded commands.

### Future Enhancements (and ToDos)

- Update the README
- Add error handling
- Add logging
- Better signing secret management
- Command Enhancements
  - show unique member counts across groups
  - show unique rsvp counts across concurrent events
  - allow setting a default Meetup group per Slack channel
  - add time frame and/or count for next events

### License

All code for these implementations is released under the [MIT](https://choosealicense.com/licenses/mit/) license.