import discord
from googletrans import Translator
import aiohttp
from datetime import datetime
import os
import json

TOKEN = 'yourbotto kenhere'
WEBHOOK_URL = 'webhookhere'
BLACK_CHANNEL_IDS = [1234567890123456789]

LOG_FILE = 'message_log.json'

translator = Translator()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
message_log = {}


def load_message_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_message_log():
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(message_log, f)


message_log = load_message_log()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user or message.webhook_id is not None:
        return
        
    if message.channel.id in BLACK_CHANNEL_IDS:
        return
    translated_en = translator.translate(message.content, dest='en').text
    translated_ja = translator.translate(message.content, dest='ja').text
    
    translated_text = f":flag_us:: {translated_en}\n:flag_jp:: {translated_ja}"
    current_time = datetime.now()
    if current_time.hour >= 0 and current_time.hour <= 5:
        ismidnight = True
    else:
        ismidnight = False

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
        sent_message = await webhook.send(
            content=translated_text, 
            username=f"from: {message.author.display_name}",
            avatar_url=message.author.avatar.url if message.author.avatar else None,
            wait=True,
            silent=ismidnight
        )
        message_log[str(message.id)] = sent_message.id
        save_message_log()

@client.event
async def on_message_edit(before, after):
    if after.author == client.user or after.webhook_id is not None:
        return

    translated_en = translator.translate(after.content, dest='en').text
    translated_ja = translator.translate(after.content, dest='ja').text
    
    translated_text = f":flag_us:: {translated_en}\n:flag_jp:: {translated_ja}"

    if str(before.id) in message_log:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
            await webhook.edit_message(message_log[str(before.id)], content=translated_text)
            save_message_log()

@client.event
async def on_message_delete(message):
    if message.author == client.user or message.webhook_id is not None:
        return

    if str(message.id) in message_log:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
            await webhook.delete_message(message_log[str(message.id)])
        del message_log[str(message.id)]
        save_message_log()

client.run(TOKEN)
