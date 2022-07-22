import os

import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image, ImageDraw, ImageFont
from fuzzywuzzy import fuzz

from typing import Optional
from typing import Union
from typing import Any
import io

""" Clear value from unexpected symbols """
def clear_value(value: str) -> str:
    temp = value
    temp = temp.strip()
    temp = temp.replace('%', '')
    temp = temp.replace('.', '')

    temp = temp.replace(',', '.')
    return temp

""" Get value from cleared value """
def get_value(value: str) -> Any:
    if value.__contains__("."):
        return float(value)
    else:
        return int(value)

artifacts_sets = {
    'eng': [
        "Adventurer", "Resolution of Sojourner", "Traveling Doctor", "Brave Heart",
        "Martial Artist", "Berserker"
    ]
}

stats_names_dicts = {
    'rus': {
        'HP': 'HP',
        'Сила атаки': 'ATK',
        'Защита': 'DEF',
        'Мастерство стихий': 'Elemental Mastery',
        'Восст. энергии': 'Energy Recharge',
        'Шанс крит. попадания': 'Crit Rate',
        'Крит. урон': 'Crit Dmg'
    },
    'eng': {
        'HP': 'HP',
        'ATK': 'ATK',
        'DEF': 'DEF',
        'Elemental Mastery': 'Elemental Mastery',
        'Energy Recharge': 'Energy Recharge',
        'CRIT Rate': 'Crit Rate',
        'CRIT DMG': 'Crit Dmg'
    }
}

class Artifact:
    def __init__(self):
        self.type: str = ""
        self.stat: dict = {} # Main stat
        self.sub_stats: dict = {} # All substats

    @classmethod
    def from_raw_text(cls, text: str, lang: str):
        cls = cls()

        for index, item in enumerate(text):
            for stat_name in stats_names_dicts[lang]:
                # Check if item is stat 
                if item.startswith(stat_name):
                    splitted_stat = item.split("+")
                    
                    # Check if item is substat
                    if len(splitted_stat) == 2:
                        stat_value = clear_value(splitted_stat[1])
                        cls.sub_stats[stat_name] = get_value(stat_value)
                        continue
                    else:
                        #TODO out of range
                        stat_value = clear_value(text[index+1])
                        cls.stat[stat_name] = get_value(stat_value)
                # Check if item is artifact set name
        return cls


class ArtifactsParser:
    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = 'tesseract'

    def set_output_language(self, lang: str) -> None:
        pass

    def get_text_from_image(self, image: Union[str, io.BytesIO], lang: str) -> Optional[dict]:
        content: bytearray = bytearray()

        if isinstance(image, str): # If image is path
            with open(image, "rb") as f:
                content = bytearray(f.read())

        if isinstance(image, io.BytesIO): # If image is bytes
            content = bytearray(image)

        img = cv2.imdecode(np.asarray(content, dtype=np.uint8), -1)

        text = []
        for line in pytesseract.image_to_string(image, lang=lang).split('\n'):
            if line and line != '\x0c':
                text.append(
                    line.replace('НР', 'HP').lstrip('-').lstrip('.').lstrip('*').lstrip('+').strip()
                )
            else:
                pass

        return text

    def sort_text(self, text: str):
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

