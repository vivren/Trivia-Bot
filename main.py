import discord
from discord.ext import commands
from discord.ext.commands import Bot
import json
import random
import asyncio
import requests

bot = commands.Bot(command_prefix = "$")
client = discord.Client()

TOKEN = 'OTI3NzM3NTk5OTE1ODg0NTg2.YdOk-A.Mq_Fs59rGfROE-23Cq1D4Ofzg70'
#channel = client.get_channel(877043351877193810)

@bot.event
async def on_ready():
    print("Ready")

# @bot.event
# async def on_message(message):
#     if message.author == client.user:
#         return

    # if message.content.startswith('!Trivia'):
    #     await message.channel.send("Type 1 to start a game.")

    #await client.process_commands(message)

@bot.command()
async def category(ctx):
    channel = ctx.channel
    await channel.send("Set category")
    category = await client.wait_for('message')
    await channel.send("Category has been set to", category)
    # category = category.content
    # print(category)

@bot.command()
async def game(ctx):
    categoriesUrl = requests.get("https://opentdb.com/api_category.php").text
    categories = json.loads(categoriesUrl)
    category = "Select category by entering a number.\n"
    count = 1
    for j in categories['trivia_categories']:
        category += f"\n {count}. {j['name']}"
        count+=1
    await ctx.send(category)
    userCategory = await bot.wait_for("message", check=lambda  m: m.channel == ctx.channel)


    await ctx.send("Select difficulty by entering a number.\n \n1. Easy 2. Medium 3. Hard")
    userDifficulty = await bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
    if userDifficulty.content == "1":
        userDifficulty = "easy"
    elif userDifficulty.content == "2":
        userDifficulty = "medium"
    else:
        userDifficulty = "hard"

    await ctx.send(f"Select how many questions you would like (Please enter a # between 1-50.")
    userNoQuestions = await bot.wait_for("message", check=lambda m: m.channel == ctx.channel)


    questionsUrl = requests.get(f"https://opentdb.com/api.php?amount={userNoQuestions.content}&category={int(userCategory.content)+8}&difficulty={userDifficulty}&type=multiple").text

    questions = json.loads(questionsUrl)
    for i in questions['results']:
        answers = i['incorrect_answers']
        answers.append(i['correct_answer'])
        random.shuffle(answers)
        await ctx.send(f"Category: {i['category']} \nDifficulty: {i['difficulty']} \n \n{i['question']} \n1. {answers[0]} \n2. {answers[1]} \n3. {answers[2]} \n4.{answers[3]} ")

        try:
            userAnswer = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30.0)

        except asyncio.TimeoutError:
            await ctx.send("Out of time.")

        else:
            if int(userAnswer.content)>0 and int(userAnswer.content)<5:
                if answers[int(userAnswer.content)-1] == i['correct_answer']:
                    await ctx.send("Correct")
                else:
                    await ctx.send("Incorrect")
            else:
                await ctx.send("Incorrect")
    #
    #     def check(m: discord.Message):
    #         print('hi')
    #         return m.author.id == ctx.author.id


# @bot.command
# async def gameSettings(ctx):
#     #country = await client.wait_for('message', check=lambda message: message.author == ctx.author)
#     await ctx.send("Enter difficulty below.")
#     #country = gameSettings.content
#
#     #
#     # if message.content.startswith('!1'):
#     #     await message.channel.send("")
bot.run(TOKEN)
