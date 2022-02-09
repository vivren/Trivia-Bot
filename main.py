import discord
from discord.ext import commands
import json
import random
import requests
import html
import time

bot = commands.Bot(command_prefix = "$")
client = discord.Client()

TOKEN = 'OTI3NzM3NTk5OTE1ODg0NTg2.YdOk-A.F2ANRDuk3q0ma6IDnr71s3uyWFY'

def embed(description):
    embed=discord.Embed(title="Trivia Bot", description=f"{description}", color=discord.Color.blue())
    return embed

@bot.event
async def on_ready():
    print("Ready")

@bot.event
async def on_message(message):
    if message.author == client.user:
        return

@bot.command()
async def game(ctx):
    categoriesUrl = requests.get("https://opentdb.com/api_category.php").text
    categories = json.loads(categoriesUrl)
    category = "Select category by entering a number. \n"
    count = 1
    for j in categories['trivia_categories']:
        category += f"\n {count}. {j['name']}"
        count+=1
    category += "\n 25. All categories."
    embedMessage = embed(category)
    await ctx.send(embed=embedMessage)
    userCategory = await bot.wait_for("message", check=lambda  m: m.channel == ctx.channel)

    embedMessage = embed("Select difficulty by entering a number.\n \n1. Easy 2. Medium 3. Hard 4. All difficulties")
    await ctx.send(embed = embedMessage)
    userDifficulty = await bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
    if userDifficulty.content == "1":
        difficulty = "easy"
    elif userDifficulty.content == "2":
        difficulty = "medium"
    elif userDifficulty.content == "3":
        difficulty = "hard"

    embedMessage = embed("Select how many questions you would like (Please enter a # between 1-50).")
    await ctx.send(embed=embedMessage)
    userNoQuestions = await bot.wait_for("message", check=lambda m: m.channel == ctx.channel)

    if userCategory.content == "25" and userDifficulty.content == "4":
        questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}").text
    elif userCategory.content == "25":
        questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}&difficulty={difficulty}&type=multiple").text
    elif userDifficulty.content == "4":
        questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}&category={int(userCategory.content) + 8}&type=multiple").text
    else:
        questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}&category={int(userCategory.content)+8}&difficulty={difficulty}&type=multiple").text

    questions = json.loads(questionsUrl)

    embedMessage = embed("React with the thumbs up to join the game. React with the checkmark to start the game!")
    startMessage = await ctx.send(embed=embedMessage)
    cacheStartMessage = discord.utils.get(bot.cached_messages, id=startMessage.id)
    thumbsUp = '\N{THUMBS UP SIGN}'
    checkMark = '✅'
    await startMessage.add_reaction(thumbsUp)
    await startMessage.add_reaction(checkMark)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == checkMark

    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

    players = {}
    if str(reaction.emoji) == checkMark:
        for i in range(0,len(cacheStartMessage.reactions)):
            if str(cacheStartMessage.reactions[i]) == thumbsUp:
                async for user in cacheStartMessage.reactions[i].users():
                    players[user.display_name] = 0

    players.pop("Lisa")

    for i in questions['results']:
        answers = i['incorrect_answers']
        answers.append(i['correct_answer'])
        await ctx.send(i['correct_answer'])
        random.shuffle(answers)
        question = f"You have 10 seconds to answer. \nCategory: {i['category']} \nDifficulty: {i['difficulty']} \n \n{i['question']} \n1. {answers[0]} \n2. {answers[1]} \n3. {answers[2]} \n4.{answers[3]} "
        question = html.unescape(question)
        embedMessage = embed(question)
        await ctx.send(embed=embedMessage)

        time.sleep(5)
        tempAnswers = {}
        async for message in startMessage.channel.history(limit=len(players)):
            if message.author.display_name in players:
                tempAnswers[message.author.display_name] = message.content

        for player in tempAnswers:
            if answers[int(tempAnswers[player])-1] == i['correct_answer']:
                players[player] += 1

        currentScore = "Current Scores:"
        for player in players:
            currentScore += f"\n{player}: {players[player]} / {userNoQuestions.content}"
        embedMessage = embed(currentScore)
        await ctx.send(embed=embedMessage)

    sortedPlayers = sorted(players.items(), key=lambda item: item[1])
    print(sortedPlayers)
    finalScore = "Final Scores:"
    for i in range(0,len(sortedPlayers)):
        finalScore += f"\n {sortedPlayers[i][0]}: {sortedPlayers[i][1]} / {userNoQuestions.content} ({int(sortedPlayers[i][1])/int(userNoQuestions.content)*100:.2f}%)"
    embedMessage = embed(finalScore)
    await ctx.send(embed=embedMessage)


bot.run(TOKEN)
