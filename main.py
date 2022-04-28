import os

import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image, ImageDraw, ImageFont
from fuzzywuzzy import fuzz


def get_text_from_image(url: str, lang: str):
    r = requests.get(url)

    image = cv2.imdecode(np.asarray(bytearray(r.content), dtype= np.uint8), -1)
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    stats = []
    text = []
    for line in pytesseract.image_to_string(image, lang= lang).split('\n'):
        if line and line != '\x0c':
            text.append(
                line.replace('НР', 'HP').lstrip('-').lstrip('.').lstrip('*').lstrip('+').strip()
            )
        else:
            pass

    stats_names_dicts = {
        'rus': {
            'HP': 'HP',
            'Сила атаки': 'Сила атаки',
            'Защита': 'Защита',
            'Мастерство стихий': 'Мастерство стихий',
            'Восст. энергии': 'Восст. энергии',
            'Шанс крит. попадания': 'Шанс крит. попадания',
            'Крит. урон': 'Крит. урон'
        },
        'eng': {
            'HP': 'HP',
            'ATK': 'Сила атаки',
            'DEF': 'Защита',
            'Elemental Mastery': 'Мастерство стихий',
            'Energy Recharge': 'Восст. энергии',
            'CRIT Rate': 'Шанс крит. попадания',
            'CRIT DMG': 'Крит. урон'
        }
    }

    for stat in text:
        stat_list = stat.split('+')

        if len(stat_list) == 2:
            stat_name_from_text = stat_list[0].replace('%', '').strip()

            for stat_name in stats_names_dicts[lang]:
                if fuzz.ratio(stat_name, stat_name_from_text) > 90:
                    stats.append(stats_names_dicts[lang][stat_name] + ' +' + stat_list[1])
                else:
                    pass
        else:
            pass

    if len(stats) == 4:
        return stats
    else:
        return False


def sort_text(text: str):
    max_roll = {
        'HP %': '5.80%',
        'HP': '299',
        'Сила атаки %': '5.80%',
        'Сила атаки': '19',
        'Защита %': '7.30%',
        'Защита': '23',
        'Мастерство стихий': '23',
        'Восст. энергии %': '6.50%',
        'Шанс крит. попадания %': '3.90%',
        'Крит. урон %': '7.80%'
    }
    stats_in_art = {}
    stats_quality = {}
    stats_vs_max_roll = {}

    to_send = ''

    for stat in text:
        stat_list = stat.split('+')

        stat_value = \
            stat_list[1].strip().replace(',', '.').replace('З', '3').replace('?', '7').replace('П', '11').replace('|', '1').replace('О', '0').replace('‚', '.').replace('/', '.').replace(' ', '').replace('х', '').replace('x', '').replace('..', '.')
        stat_name = \
            stat_list[0].strip() + ' %' if '%' in stat_value else stat_list[0].strip()
        stat_value = \
            float(stat_value.replace('%', '').strip())

        if stat_value < float(max_roll[stat_name].replace('%', '')) / 2:
            stat_value += 10

        stats_in_art[stat_name] = stat_value

    for stat_name, stat_value in stats_in_art.items():
        max_roll_for_stat = float(max_roll[stat_name].replace('%', ''))

        stats_quality[stat_name] = float('%.2f' % (stat_value / (max_roll_for_stat * 6) * 100))

    for stat_name, stat_value in stats_in_art.items():
        max_roll_for_stat = float(max_roll[stat_name].replace('%', ''))

        stats_vs_max_roll[stat_name] = float('%.2f' % (stat_value / max_roll_for_stat * 100))

    for stat_name, stat_value in stats_in_art.items():
        to_send += f'{stat_name.replace("%", "")} - {str(stat_value) + "%" if "%" in stat_name else stat_value} [ {stats_quality[stat_name]}% ]\n'

    to_send += '\n'

    to_send += 'Качество артефакта - %.2f' % (sum(stats_vs_max_roll.values()) / 9) + '%\n'
    to_send += f'Крит. масса - {stats_in_art.get("Шанс крит. попадания %", 0) * 2 + stats_in_art.get("Крит. урон %", 0)}\n'
    to_send += 'Качество крита - %.2f' % ((stats_vs_max_roll.get('Шанс крит. попадания %', 0) + stats_vs_max_roll.get('Крит. урон %', 0)) / 7) + '%'

    return to_send


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))

    return result


def unborder(pic):
    phone = Image.open(pic).convert('RGB')
    iw, il = phone.size
    obj = phone.load()
    crop = []

    def check_pixels(m, n, vertical, reverse):
        if reverse:
            m = m[::-1]
            n = n[::-1]
        for i in m:
            for j in n:
                if vertical:
                    if not obj[j, i] == (0, 0, 0):
                        if reverse:
                            crop.append(i + 1)
                        else:
                            crop.append(i)

                        return
                else:
                    if not obj[i, j] == (0, 0, 0):
                        if reverse:
                            crop.append(i + 1)
                        else:
                            crop.append(i)

                        return

    check_pixels(range(iw), range(il), False, False)
    check_pixels(range(il), range(iw), True, False)
    check_pixels(range(iw), range(il), False, True)
    check_pixels(range(il), range(iw), True, True)

    cropped = phone.crop(crop)
    add_margin(cropped, 20, 20, 20, 20, (0, 0, 0)).save(pic)


def make_image(text: str, user_id: int):
    colors = {
        'grey': (120, 120, 120),
        'blue': (0, 180, 255),
        'purple': (133, 71, 255),
        'gold': (255, 215, 0)
    }

    img = Image.open(os.path.abspath(os.getcwd()) + '\\stat_analyzer\\BG.png').convert('RGBA')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.abspath(os.getcwd()) + '\\stat_analyzer\\font.ttf', size=42, encoding='UTF-8')

    x_draw, y_draw = 20, 14

    for line in text.split('\n'):
        if not line:
            y_draw += 60
        else:
            if 'Качество артефакта' in line:
                draw.text((x_draw, y_draw), line, font=font)
                y_draw += 60
            elif 'Крит. масса' in line:
                sub_line = line.split(' - ')
                sub_line[0] += ' - '

                stat_value = float(sub_line[1].replace('%', ''))

                if stat_value >= 45:
                    color = colors['gold']
                elif stat_value >= 40:
                    color = colors['purple']
                elif stat_value >= 30:
                    color = colors['blue']
                else:
                    color = colors['grey']

                text_size = draw.textsize(sub_line[0], font=font)[0]

                draw.text((x_draw, y_draw), sub_line[0], font=font)
                draw.text((x_draw + text_size, y_draw), str(stat_value), font=font, fill=color)

                if stat_value >= 50:
                    text_size = draw.textsize(sub_line[0] + str(stat_value), font=font)[0]
                    draw.text((x_draw + text_size, y_draw), ' У ВАС МЕРТВА МАТЬ', font=font, fill= (255, 0, 0))
                else:
                    pass

                y_draw += 60
            else:
                if '[' in line:
                    sub_line = line.split(' [')
                    sub_line[0] += ' '
                    sub_line[1] = '[' + sub_line[1]

                    stat_value = float(sub_line[1].replace('[', '').replace(']', '').replace('%', ''))
                else:
                    sub_line = line.split(' - ')
                    sub_line[0] += ' - '

                    stat_value = float(sub_line[1].replace('%', ''))

                if stat_value >= 80:
                    color = colors['gold']
                elif stat_value >= 60:
                    color = colors['purple']
                elif stat_value >= 40:
                    color = colors['blue']
                else:
                    color = colors['grey']

                text_size = draw.textsize(sub_line[0], font=font)[0]

                draw.text((x_draw, y_draw), sub_line[0], font=font)
                draw.text((x_draw + text_size, y_draw), sub_line[1], font=font, fill=color)

                y_draw += 60

    img.save(f'artefact_{user_id}.png')
    unborder(f'artefact_{user_id}.png')
