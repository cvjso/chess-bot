# This example requires the 'message_content' intent.
import os
import discord
from discord import app_commands
import chess
import chess.svg
from cairosvg import svg2png


from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


TOKEN = os.environ.get("TOKEN")
CLIENT_ID = os.environ.get("CLIENT_ID")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@tree.command(name="hi", description="says hi to chat")
async def on_message(interaction):
    await interaction.response.send_message("Hi chat!")


@tree.command(name="user", description="says hi to chat")
async def on_message(interaction):
    board = chess.Board()
    screen = str(board)
    screen = screen.replace("p", "🐀")
    screen = screen.replace("n", "🐎")
    screen = screen.replace("r", "🐂")
    screen = screen.replace("q", "🐉")
    screen = screen.replace("k", "🐣")
    screen = screen.replace("b", "🐍")


    screen = screen.replace("P", "🐦")
    screen = screen.replace("N", "🐬")
    screen = screen.replace("R", "🐫")
    screen = screen.replace("Q", "🦅")
    screen = screen.replace("K", "🐛")
    screen = screen.replace("B", "🦒")
    
    screen = screen.replace(".", "🔳")

    screen = screen.splitlines()
    letters = '12345678'[::-1]
    letters = list(letters)
    for i in screen:
        index = screen.index(i)
        i = letters[index] + "\t" + i
        screen[index] = i
    screen = "\n".join(screen)
    screen += "\n\t\tA\t B\t C\t D\t E\t F\tG\t H\n"

    await interaction.response.send_message(screen)

client.run(TOKEN)
