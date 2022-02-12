import discord
from discord.ext import commands
import json
import random
import requests
import html
import time

bot = commands.Bot(command_prefix = "$")
client = discord.Client()

TOKEN = ''

def embed(description, subheading, text):
    embed=discord.Embed(title="Trivia Bot", description=f"{description}", color=discord.Color.blue())
    embed.set_thumbnail(url="https://play-lh.googleusercontent.com/r1BdZXKHH87GTCWLI9-OU1AWltnPrZr8Lg-lrG_BOZAlC_nRky6wk_qUCrUuMOt2v5k")
    embed.add_field(name=subheading, value=text)
    return embed

@bot.event
async def on_ready():
    print("Ready")

@bot.event
async def on_message(message):
    if message.author == client.user:
        return
    await bot.process_commands(message)

@bot.command()
async def game(ctx):
    categoriesUrl = requests.get("https://opentdb.com/api_category.php").text
    categories = json.loads(categoriesUrl)
    #category = "Select category by entering a number. \n"
    category=""
    for i, j in enumerate(categories['trivia_categories']):
        category += f"\n {i+1}. {j['name']}"
    category += "\n 25. All Categories"
    embedMessage = embed("Select Category By Entering a Number", "\nCategories", category)
    await ctx.send(embed=embedMessage)
    userCategory = await bot.wait_for("message", check=lambda  m: m.channel == ctx.channel and m.author == ctx.author)

    embedMessage = embed("Select Difficulty By Entering a Number", "\nDifficulties", "\n1. Easy\n 2. Medium\n 3. Hard\n 4. All Difficulties")
    await ctx.send(embed=embedMessage)
    userDifficulty = await bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    if userDifficulty.content == "1":
        difficulty = "easy"
    elif userDifficulty.content == "2":
        difficulty = "medium"
    elif userDifficulty.content == "3":
        difficulty = "hard"

    embedMessage = embed("Set Number Of Questions", "To Set", "Please enter a number between 1-50.")
    await ctx.send(embed=embedMessage)
    userNoQuestions = await bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author)

    embedMessage = embed("Set Time Limit To Answer Questions", "To Set", "Please enter a number in seconds.")
    await ctx.send(embed=embedMessage)
    userTimeLimit = await bot.wait_for("message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author)

    try:
        if userCategory.content == "25" and userDifficulty.content == "4":
            questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}").text
        elif userCategory.content == "25":
            questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}&difficulty={difficulty}&type=multiple").text
        elif userDifficulty.content == "4":
            questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}&category={int(userCategory.content) + 8}&type=multiple").text
        else:
            questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}&category={int(userCategory.content)+8}&difficulty={difficulty}&type=multiple").text

            questions = json.loads(questionsUrl)

        embedMessage = embed("Start The Game!", "Options", "React with the thumbs up to join the game.\nReact with the checkmark to start the game!" )
        startMessage = await ctx.send(embed=embedMessage)
        cacheStartMessage = discord.utils.get(bot.cached_messages, id=startMessage.id)
        thumbsUp = '\N{THUMBS UP SIGN}'
        checkMark = '✅'
        await startMessage.add_reaction(thumbsUp)
        await startMessage.add_reaction(checkMark)

        def check(reaction, user):
            return str(reaction.emoji) == checkMark and user == ctx.author

        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        players = {}
        if str(reaction.emoji) == checkMark:
            for i in range(0,len(cacheStartMessage.reactions)):
                if str(cacheStartMessage.reactions[i]) == thumbsUp:
                    async for user in cacheStartMessage.reactions[i].users():
                        players[user.display_name] = 0

        players.pop("Lisa")

        for j, i in enumerate(questions['results']):
            answers = i['incorrect_answers']
            answers.append(i['correct_answer'])
            random.shuffle(answers)
            time.sleep(1)
            question = f"\n\n1. {answers[0]} \n2. {answers[1]} \n3. {answers[2]} \n4. {answers[3]} "
            embedMessage = embed(f"{i['category']}", html.unescape(i['question']), html.unescape(question))
            await ctx.send(embed=embedMessage)

            time.sleep(int(userTimeLimit.content))
            tempAnswers = {}
            async for message in startMessage.channel.history(limit=len(players)):
                if message.author.display_name in players:
                    tempAnswers[message.author.display_name] = message.content

            for player in tempAnswers:
                if answers[int(tempAnswers[player])-1] == i['correct_answer']:
                    players[player] += 1

            if i != questions['results'][-1]:
                time.sleep(1)
                players = {k: v for k, v in sorted(players.items(), reverse=True, key=lambda item: item[1])}
                currentScore = ""

                for k,l in enumerate(players):
                    currentScore += f"\n{k+1}. {l.capitalize()}: {players[l]}/{j+1}"
                embedMessage = embed(f"Times Up!\n\n The correct answer was '{i['correct_answer']}'.\n", "Scoreboard", currentScore)
                await ctx.send(embed=embedMessage)

                time.sleep(3)

        players = {k: v for k, v in sorted(players.items(), reverse=True, key=lambda item: item[1])}
        finalScore = "Final Scores:"
        for m,n in enumerate(players):
            if m == 1:
                winner = n.capitalize()
            finalScore += f"\n {m+1}. {n.capitalize()}: {players[n]}/{userNoQuestions.content}"
        embedMessage = embed("Game Over!", f"Winner: {winner}!", f"\n\n {finalScore}")
        await ctx.send(embed=embedMessage)

    except:
        embedMessage = embed("Game Not Started.", "Why?", "Invalid game settings have been selected. Type $game to start a new game.")
        await ctx.send(embed=embedMessage)

bot.run(TOKEN)
