import json
import os
import random
import threading
import time
import sys
from typing import Literal
import discord
import datetime
import cryptocode

from discord.ext.commands import has_permissions, CheckFailure
from discord.utils import get
from discord.ext import commands
from discord import app_commands

SNAKE = b'\xf0\x9f\x90\x8d'.decode()
DATA = json.load(open("data.json", "r"))

HELP_TEXT = discord.Embed(title="Help", color=discord.Color.blue())
HELP_TEXT.add_field(name="Commands", value=" - /mute [User]: Mutes a user\n - /warn [User]: Warns a user\n - /invite: Gives you a link to invite the bot to your server\n - /blacklist [word]: Blacklists a word\n - /ticket [reason]: Creates a ticket")
HELP_TEXT.add_field(name="Tutorial", value="Begin command with <@1039407578104475709>")
HELP_TEXT.add_field(name="Change Log", value="Added Embeds, Looks nicer right?\nAdded detection for user in a server\nLTecher admin bot has moved to slash commands", inline=False)

NEW_LINE = "\n"
NEW_LINE_STR = "\\n"
GAME_TEXT = discord.Embed(title="Select Game", color=discord.Color.green())
GAME_TEXT.add_field(name="Games", value=f"Snake = {SNAKE}", inline=False)

global select_game
select_game = False

pending = []

class Logger():
    def __init__(self, name=None):
        self.name = name
        
    def info(self, message):
        if self.name == None:
            print(f"[{datetime.datetime.now()}] [INFO] {message}")
        else:
            print(f"[{self.name}] [INFO] {message}")

    def warn(self, message):
        if self.name == None:
            print(f"[{datetime.datetime.now()}] [WARN] {message}")
        else:
            print(f"[{self.name}] [WARN] {message}")

    def error(self, message):
        if self.name == None:
            print(f"[{datetime.datetime.now()}] [ERROR] {message}")
        else:
            print(f"[{self.name}] [ERROR] {message}")

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="Button",style=discord.ButtonStyle.gray)
    async def blurple_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        button.style=discord.ButtonStyle.green
        await interaction.response.edit_message(content=f"This is an edited button response!",view=self)

LOGGER = Logger()

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)

TOKEN = open("token.txt", "r").read()

commands = {
    "stop": ["/stop", "Saves the bot data and ends the bot session"],
    "help": ["/help", "Shows help for the bot commands"]
}

def console_thread():
    while True:
        try:
            command = str(input(""))
            
            if command.startswith("/"):
                command = str(command[1:])
                command = command.split(" ")
            
                if command[0] == "stop":
                    print("[Terminating the bot]")
                    json.dump(DATA, open("data.json", "w"))
                    print("[Process Closed]")
                    os._exit(0)
                elif command[0] == "help":
                    print("Commands\n--------------------------------")
                    for k, v in commands.items():
                        print(f"Command: /{k}\nDescription: {v[1]}\nUsage: {v[0]}\n--------------------------------")
                else:
                    print(f"Unknown command \"{command[0]}\"")
        except IndexError:
            print(f"Usage: {commands[command[0]][0]}")

def main_thread():
    while True:
        for guild in client.guilds:
            try:
                DATA[str(guild.id)]
            except KeyError:
                DATA[str(guild.id)] = {"banned_words": [], "vault": {}}
                json.dump(DATA, open("data.json", "w"))

                print(f"- {guild.id} (name: {guild.name})")

@client.event
async def on_ready():
    console = threading.Thread(target=console_thread)
    console.demon = True
    console.start()
    threading.Thread(target=main_thread).start()
    await client.change_presence(activity=discord.Game("Type /help for more info"))

    await tree.sync()
    LOGGER.info("Bot successsfully initlized!")

    guild_count = 0

    for guild in client.guilds:
        print(f"- {guild.id} (name: {guild.name})")

        if not get(guild.roles, name="WARN 1"):
            await guild.create_role(name="WARN 1", colour=discord.Colour(0xfff700))

        if not get(guild.roles, name="WARN 2"):
            await guild.create_role(name="WARN 2", colour=discord.Colour(0xff3300))

        if not get(guild.roles, name="WARN 3"):
            await guild.create_role(name="WARN 3", colour=discord.Colour(0x330000))

        guild_count += 1

@client.event
async def on_message(message: discord.Message):
    try:
        message.guild.id
    except:
        if message.author != client.user:
            await message.reply("Some commands will not work in private message mode!\nCreated by: Lawrence#0586")
            LOGGER.warn("Private message mode does not support most of the bot's features!")
            
        return

    for mute in DATA["mutes"]:
        if mute[0] == message.author.id and mute[2] == str(message.guild.id):
            await message.reply(embed=discord.Embed(title="Muted", color=discord.Color.red(), description=f"{message.author.mention}, You have been muted for reason \"{mute[1]}\" and cannot talk whilst muted!"))
            await message.delete()

            return

    if str(message.content) in DATA[str(message.guild.id)]["banned_words"]:
        await message.reply(embed=discord.Embed(title="Blacklisted", color=discord.Color.red(), description="One of the words in that message is blacklisted!"))
        return

    print(f"{str(message.author)}: {str(message.content)}")

    


@tree.command(name="invite", description="Get an invite link to add me to your server") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def invite(message):
    await message.response.send_message(embed=discord.Embed(title="Invite", color=discord.Colour(0xffffff), description="https://discord.com/api/oauth2/authorize?client_id=1039407578104475709&permissions=4398046511095&scope=bot"))

@tree.command(name="contact", description="Gives you info the contact the bot's creator") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def contact(message):
    await message.response.send_message(embed=discord.Embed(title="Contact", color=discord.Colour(0xffffff), description="Email: lawrencewilliams1030@gmail.com\nDiscord: Lawrence#0586"))

@tree.command(name="mute", description="Mute/Unmute a user")
@has_permissions(manage_messages=True) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def mute(message, user: discord.Member, reason: str = "none"):
    if user.id == client.user.id:
        await message.response.send_message(embed=discord.Embed(title="Error", color=discord.Color.red(), description=f"Cannot mute {client.user.mention}!"))
        return

    if not message.user.guild_permissions.manage_messages:
        await message.response.send_message(embed=discord.Embed(title="Permission Denied!", color=discord.Color.red(), description=f"Permission denied!"))
        return


    for mute in DATA["mutes"]:
        if mute[0] == user.id and mute[2] == str(message.guild.id):
            DATA["mutes"].remove(mute)
            json.dump(DATA, open("data.json", "w"))

            await message.response.send_message(embed=discord.Embed(title="Success!", color=discord.Color.green(), description=f"Successfully unmuted {user.mention}"))
            return
    
    DATA["mutes"].append([user.id, reason, str(message.guild.id)])
    json.dump(DATA, open("data.json", "w"))

    await message.response.send_message(embed=discord.Embed(title="Success!", color=discord.Color.green(), description=f"Successfully muted {user.mention} for reason \"{reason}\""))

@tree.command(name="ticket", description="Creates or removes a ticket") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def ticket(message: discord.Interaction, reason: str):
    if any("tickets" in channel.name for channel in message.guild.channels): # if there's any henry-logs channels, it will return True
        for channel in message.guild.channels:
            channel: discord.TextChannel = channel
            if channel.name == "tickets":
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = False
                overwrite.read_messages = False

                try:
                    await channel.set_permissions(message.guild.default_role, overwrite=overwrite)
                except discord.errors.Forbidden:
                    pass
                
                try:
                    class SelectedButton(discord.ui.View):
                        def __init__(self, *, timeout=None):
                            super().__init__(timeout=timeout)
                        
                        @discord.ui.button(label="Handled",style=discord.ButtonStyle.green,disabled=True)
                        async def blurple_button(self,button:discord.ui.Button,interaction:discord.Interaction):
                            pass


                    class Buttons(discord.ui.View):
                        def __init__(self, *, timeout=None):
                            super().__init__(timeout=timeout)

                            self.handled = False
                        
                        @discord.ui.button(label="Handle",style=discord.ButtonStyle.gray)
                        async def blurple_button(self,button:discord.ui.Button,interaction:discord.Interaction):
                            if self.handled == True:
                                await message.channel.send(embed=discord.Embed(title="Error", description="This ticket is already being handled by someone else!", color=discord.Color.red()))
                                return
                            
                            self.style = discord.ButtonStyle.green
                            dm = message.user.create_dm()
                            await dm.send("Your ticket will be handled by ")
                            await handle_message.edit(view=SelectedButton())

                            self.handled = True
                            

                    handle_message = await channel.send(embed=discord.Embed(title="Ticket", description=f"{message.user.mention} created a ticket!\n```{reason.replace(NEW_LINE_STR, NEW_LINE)}```", color=discord.Color.green()), view=Buttons())
                    await message.response.send_message(embed=discord.Embed(title="Success!", description="Ticket successfully created!", color=discord.Color.green()))
                except Exception as e:
                    if str(e) == "403 Forbidden (error code: 50001): Missing Access":
                        await message.response.send_message(embed=discord.Embed(title="Error", description=f"Failed to create ticket: {client.user.mention} must have the permissions to access {channel.mention} to create a ticket!", color=discord.Color.red()))
                        return
                    
                    await message.response.send_message(embed=discord.Embed(title="Error", description=f"Failed to create ticket: {str(e.__class__)}: {str(e)}", color=discord.Color.red()))
    else:
        await message.response.send_message(embed=discord.Embed(title="Tickets channel not found!", color=discord.Color.red(), description="Tickets channel not found, in order to use this command please create a channel named **EXACTLY**\n```tickets```"))

@tree.command(name="help", description="Show help for LTecher Admin Bot") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def help(message):
    await message.response.send_message(embed=HELP_TEXT)

@tree.command(name="rps", description="Play a game of rock paper scissors") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def rps(message: discord.Interaction, choice: Literal["Rock", "Paper", "Scissors"], user: discord.Member = None):
    choices = ["Rock", "Paper", "Scissors"]

    computer = random.choice(choices)

    if user != None:
        for request in pending:
            if request[1] == str(user.id) and request[2] == message.guild.id:
                dm: discord.DMChannel = request[3]

                if choice == request[0]:
                    await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.yellow(), description="Tie!"), ephemeral=True)
                elif choice == "Rock":
                    if request[0] == "Paper":
                        await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} covers {request[0]}"))
                        await dm.send(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {choice} covers {request[0]}"))
                    else:
                        await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {choice} covers {request[0]}"))
                        await dm.send(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} covers {request[0]}"))
                elif choice == "Paper":
                    if request[0] == "Scissors":
                        await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} covers {request[0]}"))
                        await dm.send(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {choice} covers {request[0]}"))
                    else:
                        await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {choice} covers {request[0]}"))
                        await dm.send(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} covers {request[0]}"))
                elif choice == "Scissors":
                    if request[0] == "Rock":
                        await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {request[0]} smashes {choice}"))
                        await dm.send(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {request[0]} smashes {choice}"))
                    else:
                        await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {choice} smashes {request[0]}"))
                        await dm.send(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} smashes {request[0]}"))
                else:
                    await message.response.send_message(embed=discord.Embed(title="Error", color=discord.Color.red(), description="Not a valid move!"))

                pending.remove(request)
                return

        send = [choice, str(user.id), message.guild.id, await user.create_dm()]
        dm: discord.DMChannel = send[3]
        await dm.send(f"You have been asked a rock paper scissors request by {str(message.user)},\nTo accept: go on \"{str(message.guild.name)}\" and type /rps [Choice] @{str(message.user).split('#')[0]}")

        pending.append(send)
        await message.response.send_message(embed=discord.Embed(title="Request Sent!", color=discord.Color.green(), description="Successfully sent Rock Paper Scissors request!"))
        return

    if choice == computer:
        await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.yellow(), description="Tie!"), ephemeral=True)
    elif choice == "Rock":
        if computer == "Paper":
            await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {computer} covers {choice}"), ephemeral=True)
        else:
            await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} smashes {computer}"), ephemeral=True)
    elif choice == "Paper":
        if computer == "Scissors":
            await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {computer} cuts {choice}"), ephemeral=True)
        else:
            await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} covers {computer}"), ephemeral=True)
    elif choice == "Scissors":
        if computer == "Rock":
            await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.red(), description=f"You lose! {computer} smashes {choice}"), ephemeral=True)
        else:
            await message.response.send_message(embed=discord.Embed(title="Result", color=discord.Color.green(), description=f"You win! {choice} cuts {computer}"), ephemeral=True)
    else:
        await message.response.send_message(embed=discord.Embed(title="Error", color=discord.Color.red(), description="Not a valid move!"))

@tree.command(name="vault", description="Stores info in a guild vault with a password") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def vault(message: discord.Interaction, name: str, password: str, data: str = "None", delete: bool = False):
    if delete == True:
        if cryptocode.decrypt(DATA[str(message.guild.id)]["vault"][name], password) != False:
            del DATA[str(message.guild.id)]["vault"][name]
            json.dump(DATA, open("data.json", "w"))

            await message.response.send_message(embed=discord.Embed(title="Success!", color=discord.Color.green(), description=f"Successfully deleted \"{name}\""), ephemeral=True)
        else:
            await message.response.send_message(embed=discord.Embed(title="Error", color=discord.Color.red(), description=f"The password to delete \"{name}\" is invalid!"), ephemeral=True)

        return

    try:
        if cryptocode.decrypt(DATA[str(message.guild.id)]["vault"][name], password) != False:
            await message.response.send_message(embed=discord.Embed(title=f"Value of \"{name}\"", description=cryptocode.decrypt(DATA[str(message.guild.id)]["vault"][name], password)), ephemeral=True)
        else:
            await message.response.send_message(embed=discord.Embed(title=f"Error", color=discord.Color.red(), description=f"The root \"{name}\" exists but the password is invalid!"), ephemeral=True)
        
        return
    except:
        pass
    
    DATA[str(message.guild.id)]["vault"][name] = cryptocode.encrypt(data, password)
    json.dump(DATA, open("data.json", "w"))

    await message.response.send_message(embed=discord.Embed(title="Success!", color=discord.Color.green(), description=f"Successfully created \"{name}\"!"), ephemeral=True)



@tree.command(name="blacklist", description="Blacklist a word") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def blacklist(message, word: str):
    if not message.user.guild_permissions.manage_messages:
        await message.response.send_message(embed=discord.Embed(title="Permission Denied!", color=discord.Color.red(), description=f"Permission denied!"))
        return
    
    if word in DATA[str(message.guild.id)]["banned_words"]:
        DATA[str(message.guild.id)]["banned_words"].remove(word)
        await message.response.send_message(embed=discord.Embed(title="Success!", color=discord.Color.green(), description=f"Successfully whitelisted the word \"{word}\"!"))
        json.dump(DATA, open("data.json", "w"))

        return

    DATA[str(message.guild.id)]["banned_words"].append(word)
    json.dump(DATA, open("data.json", "w"))

    await message.response.send_message(embed=discord.Embed(title="Success!", color=discord.Color.green(), description=f"Successfully blacklisted the word \"{word}\"!"))

try:
    client.run(TOKEN)
except Exception as ex:
    LOGGER.error(f"Error logging in: {str(ex.__class__)}: {ex}")
    exit(1)