# Heroku Deploy

**Important Notes**
1. Generate all your private files from master branch (token.pickle, config.env, drive_folder, cookies.txt, accounts, .netrc) since the generators not available in heroku branch but you should add the private files in heroku branch not in master or use variables links in `config.env`.
2. Don't add variables in heroku Environment, you can only add `CONFIG_FILE_URL`.
3. Don't deploy using hmanager or github integration.
4. To avoid idling fill `BASE_URL_OF_BOT` or you can use [corn-job](http://cron-job.org) to ping your Heroku app.
5. If you want to edit anything in code, so u should edit [h-code branch](https://github.com/anasty17/mirror-leech-telegram-bot/tree/h-code). After that u should add fill `UPSTREAM_REPO` of your fork and leave `UPSTREAM_BRANCH` empty since it's by default `h-code`.
6. This branch use megasdkrest and latest version of qBittorrent.

