import datetime
import json
import os
from io import BytesIO

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from ArtParser.ArtParser import Parser



Bot = commands.Bot(command_prefix= '?*')
Bot.remove_command('help')


@Bot.event
async def on_ready():
    print(f'[SYSTEM] Bot online!\n[SYSTEM] Name - {Bot.user}\n[SYSTEM] ID - {Bot.user.id}')


@Bot.command(aliases=['статы'])
async def stats(ctx, lang: str = None):
    if ctx.message.attachments:
        if lang in ['rus']:
            bytes = await ctx.message.attachments[0].read()
            image = Image.open(BytesIO(bytes))

            pars = Parser(image)
            parsed = pars.img_to_str(lang)

            if not parsed:
                if image.size != (1920, 1080):
                    image = image.resize((1920, 1080), Image.ANTIALIAS)

                    pars = Parser(image)
                    parsed = pars.img_to_str(lang)

                if not parsed:
                    await ctx.message.reply('Не удалось найти замок на картинке.')
                    return

            text_from_image = parsed[0]

            await ctx.send(f'Прочитаные статы: {text_from_image}')
        else:
            await ctx.message.reply('Неверный аргумент языка.')
    else:
        await ctx.message.reply('Вы не прикрепили картинку.')


Bot.run('')