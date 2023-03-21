# This example requires the 'message_content' intent.
import os
import discord
from discord import app_commands
import chess
import chess.svg
from cairosvg import svg2png
import sqlite3

from dotenv import load_dotenv, find_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

boards = {}
players = []
billboard = {}

DB_CONN = sqlite3.connect("main.db")
DB_CURSOR = DB_CONN.cursor()

def setup_db():
    global billboard
    DB_CURSOR.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGET NOT NULL
        )
        """
    )
    DB_CURSOR.execute("SELECT * FROM users")
    db_result = DB_CURSOR.fetchall()
    for entry in db_result:
        billboard[entry[1]] = entry[2]

# def load_db():
#     global billboard

def add_to_db():
    global billboard
    for key, value in billboard.items():
        DB_CURSOR.execute(f"SELECT id FROM users WHERE name = '{key}'")
        select_result = DB_CURSOR.fetchall()
        if len(select_result):
            user_id = select_result[0][0]
            DB_CURSOR.execute(f"""
                UPDATE users
                SET points = {value}
                WHERE id = {user_id}
            """)
        else:
            DB_CURSOR.execute(f"INSERT INTO users (name, points) VALUES ('{key}', '{value}')")
    DB_CONN.commit()

def add_to_billboard(user):
    user = str(user)
    if user not in billboard.keys():
        billboard[user] = 0
    billboard[user] += 1
    add_to_db()

def display_board(_board):
    if _board == None:
        return "No game has started"
    screen = str(_board)
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
    screen = screen.splitlines()
    letters = '12345678'[::-1]
    letters = list(letters)
    collor = 0
    for i in screen:
        index = screen.index(i)
        i = i.split()
        for j in i:
            index_j = i.index(j)
            if j == '.':
                if (index + index_j) % 2:
                    # branco
                    i[index_j] = '⬛'
                else:
                    # preto
                    i[index_j] = '⬜'
                collor += 1
        collor += 1
        i = " ".join(i)
        i = letters[index] + "\t" + i
        screen[index] = i
    screen = "\n".join(screen)
    screen += "\n\t\tA\tB\tC\tD\t E\t F\t G\t H\n"
    return screen

def is_user_in_game(_user, _list):
    for i in _list:
        if _user in i:
            return True
    return False

def get_board_by_user(_user, _list):
    for i in _list:
        if _user in i:
            return i

def display_billboard(_billboard:dict):
    result = ''
    for key, value in _billboard.items():
        result += f"*{key}* = `{value}`\n"
    if result == '':
        return "No user has won a game yet"
    return result

def end_game(user):
    global boards
    board_key = get_board_by_user(user, boards)
    boards.pop(board_key)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    setup_db()
    await tree.sync()

@tree.command(name="hi", description="says hi to chat")
async def on_hi(interaction):
    await interaction.response.send_message("Hi chat!")

@tree.command(name="clean", description="clean games")
async def on_clean(interaction):
    global players, boards
    players = []
    boards = {}
    await interaction.response.send_message("all games has been cleaned")

@tree.command(name="start_game", description="start a new game")
async def on_game(interaction: discord.Interaction):
    global players, boards
    if is_user_in_game(interaction.user, boards):
        return await interaction.response.send_message("User already in match")
    players.append(interaction.user)
    if len(players) != 2:
        return await interaction.response.send_message("Waiting next player")
    current_board = chess.Board()
    boards[(players[0], players[1])] = current_board
    players = []
    await interaction.response.send_message(display_board(current_board))

@tree.command(name="play", description="play a move in the current game")
@app_commands.describe(movement = "target position to move")
async def on_play(interaction: discord.Interaction, movement:str):
    global billboard
    username = interaction.user
    if not is_user_in_game(username, boards.keys()):
        return await interaction.response.send_message("User not in game")
    board_key = get_board_by_user(username, boards.keys())
    board = boards[board_key]
    try:
        board.push_san(movement)
    except Exception as ex:
        print(ex)
        return await interaction.response.send_message("Movement is ilegal")
    if board.is_checkmate():
        end_game(username)
        add_to_billboard(username)
        await interaction.response.send_message(display_board(board))
        return await interaction.followup.send(f"Checkmate! user *{username.mention}* has won, having `{billboard[username]}` victories")
    other_player = board_key[0] if board_key[1] == username else board_key[1]
    await interaction.response.send_message(display_board(board))
    await interaction.followup.send(f"It's your turn {other_player.mention}")

@tree.command(name="billboard", description="show ranking players of server")
async def on_billboard(interaction: discord.Interaction):
    global billboard
    await interaction.response.send_message(display_billboard(billboard))

@tree.command(name="surrender", description="give up on the match")
async def on_surrender(interaction: discord.Interaction):
    global billboard, players, boards
    username = interaction.user
    board_key = get_board_by_user(username, boards.keys())
    other_player = board_key[0] if board_key[1] == username else board_key[1]
    add_to_billboard(other_player)
    await interaction.response.send_message(f"{username.mention} has surrendered, {other_player.mention} won!, having `{billboard[other_player]}` victories")


client.run(TOKEN)