# mabi-ah-discord
Mabinogi Auction House Watcher using Discord Bot + MongoDB Atlas 

# Creating and Inviting a Private Discord Bot

1. Navigate to https://discord.com/developers/applications to create a new bot
2. Click on `New Application` on top right
3. Enter name for your Discord bot, accept ToS and click `Create`
4. Go to `OAuth2` tab on the left and perform the following:
  - Under `Client Information`:
    - Click on `Reset Secret`
  - Under `OAuth2 URL Generator`:
    - Check `Bot`
  - Under `Bot Permissions`:
    - Check `Administrator` 
  - Under `Integration Type`:
    - Select `Guild Install`
5. This will generate an invite link. Copy this and paste to your browser. Select the server you want to add this bot to and click `Continue` and then `Authorize`
6. Go back to the Developer Portal. Go to `Installation` on the left and select `None` in the dropdown under `Install Link`
7. Go to `Bot` tab on the left and perform the following:
  - Under `Authorization Flow`:
    - Disable `Public Bot`
    - Enable `Requires OAUTH2 Code Grant`
  - Under `Priviledged Gateway Intents`:
    - Enable `Presence Intent`
    - Enable `Server Members Intent`
    - Enable `Message Content Intent`
  - Under `Bot Permissions`:
    - Check `Administrator` 
8. Generate a `Token` by going to `Bot` tab and click on `Reset Token` under `Token`. Save this token to use in the app.