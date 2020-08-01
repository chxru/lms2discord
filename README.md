# LMS-2-Discord

> Notify for new items in moodle based lms

For some reasons the LMS used in my university not exposing api for students. So I had to scrap everything and compare them manually to get data about newly added content.
Script runs once per an hour. So notifications isn't real time
Script is currently hosted in heroku.

Master branch saves data in mlab (due to data presistance issue in heroku which is I am too lazy to solve).
If you prefer local storage, check tinydb branch.

## Enviromental variables

Add these variables in Heroku settings -> Config vars
| Variable | Value |
| -------- | ------|
| lms-username | moodle(lms) username |
| lms-password | moodle(lms) password |
| webhookURL | discord notification channel webhook url |
| logginURL | heroku log output channel webhook url |
| dbUser | mlab.com database username |
| dbPassword | mlab.com database password |
