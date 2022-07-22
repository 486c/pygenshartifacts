import io
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont

from typing import Optional
from typing import Union
from typing import Any

import string

allowed_symbols = {
    'eng': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ%+,.0123456789 ',
    'rus': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ%+,.0123456789 ',
}

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

""" Clear stats value from unexpected symbols """
def clear_value(value: str) -> str:
    temp = value
    temp = temp.strip()
    temp = temp.replace('%', '')

    if ',' in temp:
        temp = temp.replace('.', '')

    temp = temp.replace(',', '.')
    return temp

""" Get value from cleared value """
def get_value(value: str) -> Any:
    if value.__contains__("."):
        try:
            return float(value)
        except:
            return None
    else:
        try:
            return int(value)
        except:
            return None

""" Reconstructs line with only allowed symbols """
def clear_line(value: str, lang: str) -> str:
    temp = ""
    for ch in value:
        if ch in allowed_symbols[lang]:
            temp += ch
    return temp.strip()

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
                # Clear string from not wanted symbols
                cleared_item = clear_line(item, lang)

                # Check if item is stat 
                if cleared_item.startswith(stat_name):
                    splitted_stat = cleared_item.split("+")
                    
                    # Check if item is substat
                    if len(splitted_stat) == 2:
                        stat_value = clear_value(splitted_stat[1])
                        v = get_value(stat_value)
                        if v is not None:
                            cls.sub_stats[stat_name] = v
                            continue

                    # Check if item is main stat
                    else:
                        if index+1 > len(text):
                            continue

                        stat_value = clear_value(text[index+1])
                        v = get_value(stat_value)
                        if v is not None:
                            cls.stat[stat_name] = v
                            continue
        return cls


class ArtifactsParser:
    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = 'tesseract'

    def set_output_language(self, lang: str) -> None:
        pass

    def get_text_from_image(self, image: Union[str, io.BytesIO], lang: str) -> Optional[dict]:
        content: bytearray = bytearray()

        # If image is path
        if isinstance(image, str): 
            with open(image, "rb") as f:
                content = bytearray(f.read())
        # If image is bytes
        if isinstance(image, io.BytesIO): 
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
