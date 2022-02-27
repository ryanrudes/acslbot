import pandas as pd
import requests
import asyncio
import discord
import random
import dotenv
import math
import os
import re

from markdownify import markdownify
from bs4 import BeautifulSoup

dotenv.load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

STEAM = os.getenv('STEAM_ROSTER_ID') # senior team roster ID
ITEAM = os.getenv('ITEAM_ROSTER_ID') # intermediate team roster ID
JTEAM = os.getenv('JTEAM_ROSTER_ID') # junior team roster ID

client = discord.Client()

congratulations = ['Fantastic', 'Well done', 'Good job', 'Nice going', 'Superb', 'Congratulations', 'Nice work', 'Nice job', 'Good work', 'Nicely done', 'Keep it going', 'Keep it up']

regular_phrases = ["{salute}, **{name}**! You scored a {score} on the contest {contest} {section}!",
                   "Looks like **{name}** scored a {score} on the contest {contest} {section}! {salute}!",
                   "Hey, **{name}**, looks like you scored a {score} on the contest {contest} {section}! {salute}!"]
perfect_phrases = ["{salute}, **{name}**! You earned a *perfect score* on the contest {contest} {section}!",
                   "Looks like **{name}** earned a *perfect score* on the contest {contest} {section}! {salute}!",
                   "Hey, **{name}**, looks like you received a *perfect score* on the contest {contest} {section}! {salute}!"]

def fetch(roster: int):
    resp = requests.get(f"https://www.scores.acsl.org/roster/{roster}")
    html = resp.content
    soup = BeautifulSoup(html, features = 'lxml')
    elem = soup.find("table", {"class": "display"})
    html = str(elem)
    data = pd.read_html(html)[0]
    return data

async def update(roster):
    await client.wait_until_ready()

    channel = client.get_channel(id = 944738843029041242)
    last = fetch(roster)

    while not client.is_closed():
        data = fetch(roster)

        for contest in range(1, 5):
            for section in ['Program', 'Shorts']:
                for student in data['Student']:
                    new = float(data.loc[data['Student'] == student, section[0] + str(contest)].item())
                    old = float(last.loc[last['Student'] == student, section[0] + str(contest)].item())

                    if not math.isnan(new) and new != old:
                        score = int(new)

                        if score >= 4:
                            salute = random.choice(congratulations)

                            if score == 5:
                                message = random.choice(perfect_phrases).format(salute = salute, name = student, contest = contest, section = section.lower())
                            elif score == 4:
                                message = random.choice(regular_phrases).format(salute = salute, name = student, contest = contest, section = section.lower(), score = score)

                            await channel.send(message)

        last = data
        await asyncio.sleep(60)

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, id = GUILD)

client.loop.create_task(update(STEAM))
client.loop.create_task(update(ITEAM))
client.loop.create_task(update(JTEAM))

client.run(TOKEN)
