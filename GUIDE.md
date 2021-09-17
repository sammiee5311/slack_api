## Server
- download [ngrok](https://ngrok.com)
- `ngrok http 5000` command

## Create a new app
- go to [slack app](https://api.slack.com/apps/) and create a new app.

## Slash commands
- add slash commands
    - `/message-count`
    - `/weather`
    - `/vote`
    - `/translation`
    - `/help`
    - `/classify`

## Interactivity & Shortcuts
- create a shortcut with `vote_team_leader` callback id 
- set the request url to `{website}/interactions`

## OAuth & Permissions
- add scopes
    - `channels:history`, `channels:read`, `chat:write`
    - `chat:write.customize`, `emoji:read`, `files:read`
    - `groups:read`, `im:read`, `im:write`, `mpim:read`

## Event Subscriptions
- set the request url to `{website}/slack/events`

## Slack
- add slack bot in the slack channels