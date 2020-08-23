# LMS-2-Discord

> Notify for new items in moodle based lms

For some reasons the LMS used in my university not exposing api for students. So I had to scrap everything and compare them manually to get data about newly added content.
Script runs once per an hour. So notifications isn't real time
Script is currently hosted in heroku.

Master branch saves data in mlab (due to data presistance issue in heroku which is I am too lazy to solve).
If you prefer local storage, check tinydb branch.

## Hosting this script in heroku
1. Clone or fork this repo
2. Update the `courses` list with your own courses  
    To find the id, go to lms then click on a course module. ID will be displayed at the end of the URL  
    eg: `lms.com/course/view.php?id=[courseIDhere]`
3. If you forked this repo before, commit the changes
4. Goto heroku and create a new app
5. Goto deploy tab and choose 'heroku git' if you clone the repo, or 'github' if you forked the repo
6. Follow the instruction given by heroku
7. After deploying app set below enviromental variables  

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
