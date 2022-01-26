# pinus-telebot

**Steps to set-up development**: 
1. Get a Bot-API-Token from BotFather in Telegram
2. Get Dropbox API Token from Dropbox Account
3. Get Google API Credentials from Google API
4. Create a .env file that contains the following: 
   1. BOT_API_TOKEN='Fill with Token'
   2. DROPBOX_API_TOKEN='Fill With Token'
   3. GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json

**Deployment**:

1.Heroku create on CLI

2.Add the following 2 buildpacks on Heroku: 

    1.https://github.com/gerywahyunugraha/heroku-google-application-credentials-buildpack
    
    1.https://github.com/heroku/heroku-buildpack-python


3.Set up the config variables (BOT_API_TOKEN, DROPBOX_API_TOKEN, and GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json, and GOOGLE_CREDENTIALS='Fill with JSON Content of google API Credentials Token')
