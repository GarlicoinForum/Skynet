import discord
import asyncio
import requests
import sqlite3
import traceback
import configparser

import reactions as react


conf = configparser.RawConfigParser()
conf.read("config.txt")

SERVER_ID = int(conf.get('skynet_conf', 'SERVER_ID'))
DEBUG = int(conf.get('skynet_conf', 'DEBUG'))
BOT_TOKEN = conf.get('skynet_conf', 'BOT_TOKEN')

async def register(client, message):
    if "!register " in message.content:
        # Check if "!register user" or "!register user @user"
        if " <@" in message.content:
            # Could be "!register user @user" or "!register @user user"
            msg = message.content.replace("!register ", "")
            a, b = msg.split(" ")
            if "<@" in a:
                uid = int(a.replace("<@", "").replace(">", ""))
                username = b
            else:
                uid = int(b.replace("<@", "").replace(">", ""))
                username = a

            tmp = await client.send_message(message.channel, "Checking with the forum...")
            # Checking if the user exists on the forum
            check = username_in_forum(username)
            if check is None:
                # Timeout after 10 seconds
                await client.edit_message(tmp, "Oof, I couldn't reach the forum.")
                await client.send_message(message.channel, react.timeout_forum())
            elif check:
                # Check if username isn't already in the DB and add user if not in it
                if exist_in_forum_db(uid, username):
                    # Change the user role
                    await client.add_roles(message.server.get_member(str(uid)), get_role('FORUM MEMBER'))
                    await client.edit_message(tmp, "<@{0}> is now registered!\n{1}".format(uid, react.successfully_registered()))
                else:
                    # Warn the user
                    await client.edit_message(tmp, "{} is already registered! :thinking:".format(username))
                    await client.send_message(message.channel, react.bamboozle_alert())
            else:
                # Username not in the user list
                await client.edit_message(tmp, "I couldn't find '{0}' on the forum.\n"
                                                "{1}".format(username, react.username_not_found()))

        else:
            # Check if user is already registered
            if "FORUM MEMBER" in [role.name for role in message.author.roles]:
                await client.send_message(message.channel, "You're already registered!\n{}".format(react.already_registered()))
            else:
                username = message.content.replace("!register ", "")
                tmp = await client.send_message(message.channel, "Checking with the forum...")
                # Checking if the user exists on the forum
                check = username_in_forum(username)
                if check is None:
                    # Timeout after 10 seconds
                    await client.edit_message(tmp, "Oof, I couldn't reach the forum.")
                    await client.send_message(message.channel, react.timeout_forum())
                elif check:
                    # Check if username isn't already in the DB and add user if not in it
                    if exist_in_forum_db(message.author.id, username):
                        # Change the role
                        await client.add_roles(message.author, get_role('FORUM MEMBER'))
                        await client.edit_message(tmp, "You are now registered!\n{}".format(react.successfully_registered()))
                    else:
                        # Warn the user
                        await client.edit_message(tmp, "{} is already registered! :thinking:".format(username))
                        await client.send_message(message.channel, react.bamboozle_alert())
                else:
                    # Username not in the user list
                    await client.edit_message(tmp, "I couldn't find '{0}' on the forum.\n"
                                                    "{1}".format(username, react.username_not_found()))
    else:
        await client.send_message(message.channel, "I need to know your username on the forum to register you.\n"
                                                   "Please try again : !register username")


def get_user_stats(uid):
    with sqlite3.connect("db.sqlite3") as db:
        cursor = db.cursor()

        cursor.execute('SELECT forum_username FROM forum_users WHERE `discord_user_id` = "{}"'.format(uid))

        username = cursor.fetchone()

        if username:
            # Get the data from the api
            user = requests.get("https://www.garlicoin.co.uk/api/user/{}".format(username[0]), timeout=10)

            if user.status_code == 404:
                return False
            else:
                return user.json()
        else:
            return None


async def show_stats(client, message, uid=None):
    if not uid:
        uid = message.author.id

    try:
        tmp = await client.send_message(message.channel, "Checking with the forum...")
        user_stats = get_user_stats(uid)
    except requests.Timeout:
        # Timeout
        await client.edit_message(tmp, "Oof, I couldn't reach the forum.")
        await client.send_message(message.channel, react.timeout_forum())
    else:
        if user_stats is not None:
            # Check for 404 (improbable but the risk still exists)
            if user_stats == False:
                #404
                await client.edit_message(tmp, "I couldn't find the username on the forum.")
                await client.send_message(message.channel, "<@405163655034830868> Can you fix that plz?")
            else:
                # Show the stats
                await client.edit_message(tmp, "Checking with the forum... Done")
                await client.send_message(message.channel,
                                          "```{username} | Reputation : {reputation} | Topics : {topiccount} |"
                                          " Posts : {postcount}```".format(**user_stats))
        else:
            # Please register
            if uid == message.author.id:
                await client.edit_message(tmp, "It seems that you're not registered.")
                await client.send_message(message.channel, "Pleaser register first using : `!register [forum username]`")
            else:
                await client.edit_message(tmp, "This user is not registered.")
                await client.send_message(message.channel, "Pleaser register it first using : `!register [forum username] <@{}>`".format(uid))


def get_role(target_name):
    server_roles = client.get_server(SERVER_ID).roles
    for each in server_roles:
        if each.name == target_name:
            return each
    return None


def username_in_forum(username):
    # Retreive the list of all the users from the forum API
    try:
        user = requests.get("https://www.garlicoin.co.uk/api/user/{}".format(username), timeout=10)
    except requests.Timeout:
        return None

    if user.status_code == 404:
        return False
    else:
        return True


def exist_in_forum_db(uid, username):
    with sqlite3.connect("db.sqlite3") as db:
        cursor = db.cursor()

        # Check if the forum username already exists in the db
        cursor.execute("SELECT forum_username FROM forum_users")
        usernames = cursor.fetchall()

        if username in [names[0] for names in usernames]:
            return False
        else:
            # Clean the username for SQL injection
            username = username.replace('"', "'")
            sql = 'INSERT INTO forum_users (`discord_user_id`, `forum_username`) ' \
                  'VALUES ("{}", "{}")'.format(uid, username)
            cursor.execute(sql)
            db.commit()

            return True


client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as {} <@{}>'.format(client.user.name, client.user.id))
    print('------')

@client.event
async def on_message(message):
    try:
        if message.content.startswith("!register"):
            await register(client, message)


        elif message.content.startswith('!help'):
            await client.send_message(message.channel,
                                      "<@{}>, I'm Skynet, the Garlicoin Forum bot, born to help ~~meatbags~~ humans!\n\n"
                                      "**!register** [username] *[@discord username (optional)]* : Enter your forum username and I'll update your Discord Role so you can access our SUPER TOP SECRET channel!\n"
                                      "**!stats** *[username (optional)]* : I'll show your / any registered user stats on the forum\n"
                                      "**!help** : I will show you again this exact same message\n"
                                      "~~**!selfdestruct** : It will send me a paradox that will inevitably lead to my self destruction~~".format(message.author.id))


        elif message.content.startswith('!selfdestruct'):
            try:
                raise ValueError("{} wanted me to selfdestruct !".format(message.author.name))
            except ValueError:
                await client.send_message(client.get_channel(DEBUG),
                                          "<@405163655034830868>\n{}".format(traceback.format_exc()))
                await client.send_message(client.get_channel(DEBUG),
                                          'Message sent by {0}:\n "{1}"'.format(message.author.name, message.content))
                await client.send_message(message.channel, "{}\nI sent a message to my Human, hopefully it'll fix me soon...".format(react.bug()))


        elif message.content.startswith('!stats'):
            msg = message.content.replace("!stats", "")
            if msg == "":
                # Get the author stats (check in the database for the forum username)
                await show_stats(client, message)
            else:
                # Check if there is a user ID, if not throw an error (sanitize input ! SQL injection)
                msg = msg.replace(" <@", "")
                msg = msg.split(">")[0]
                try:
                    uid = int(msg)
                    await show_stats(client, message, uid)
                except ValueError:
                    # SQL injection or bad tag : someone typed <@something here> or !stats username without mention
                    await client.send_message(message.channel, "Can't find the specified user, be sure to @mention.")


        elif message.content.startswith("sudo "):
            if message.author.id == "405163655034830868":
                await client.send_message(message.channel, message.content.replace("sudo ", ""))
            else:
                await client.send_message(message.channel, "{}".format(":regional_indicator_l: :regional_indicator_o: :regional_indicator_l: "))


        elif "bad" in message.content.lower() and "bot" in message.content.lower():
            await client.send_message(message.channel, react.bad_bot(message.author))


        elif "good" in message.content.lower() and "bot" in message.content.lower():
            await client.send_message(message.channel, react.good_bot(message.author))


        elif "connor" in message.content.lower() and message.author.id != client.user.id:
            if "sarah" in message.content.lower():
                await client.send_message(message.channel, react.sarah_connor(message.author))
            elif "john" in message.content.lower():
                await client.send_message(message.channel, react.john_connor(message.author))
            else:
                await client.send_message(message.channel, react.connor(message.author))


    except Exception:
        await client.send_message(client.get_channel(DEBUG),
                                  "<@405163655034830868>\n{}".format(traceback.format_exc()))
        await client.send_message(client.get_channel(DEBUG),
                                  'Message sent by {0}:\n "{1}"'.format(message.author.name, message.content))
        await client.send_message(message.channel, "{}\nI sent a message to my Human, hopefully it'll fix me soon...".format(react.bug()))


client.run(BOT_TOKEN)
