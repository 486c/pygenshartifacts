import pytest

from genshartifacts import Artifact

from genshartifacts import clear_value, get_value, clear_line

def test_clear_value():
    assert clear_value("46,6%") == "46.6"
    assert clear_value("46.6%%") == "46.6"
    assert clear_value("%%%4%6.6%%") == "46.6"
    assert clear_value("    %%%4%6.6%%       ") == "46.6"
    assert clear_value("%%%4%6.6%%         ") == "46.6"
    assert clear_value("                    %%%4%6.6%%") == "46.6"

def test_get_value():
    assert get_value("46.6") == 46.6
    assert get_value("2") == 2
    assert get_value("2.0") == 2.0
    assert isinstance(get_value("2"), int)
    assert isinstance(get_value("2.0"), float)
    assert get_value("2aaqa") == None
    assert get_value("testtest") == None

def test_clear_line():
    assert clear_line(">>>>>>>>>>>value***---123", "eng") == "value123"
    assert clear_line("Пески времени", "rus") == "Пески времени"


def test_artifacts_class_raw_text1():
    example_input = ['Пески времени', 'Сила атаки', '46,6%', 'ЖЖЖи', '20 |8|', 'Крит. урон +46,8%', 'Восст. энергии +5,2%', 'HP +269', 'Сила атаки +14.']
    a = Artifact.from_raw_text(example_input, "rus")

    assert len(a.sub_stats) == 4
    assert len(a.main_stat) == 1

    assert a.main_stat['ATK'] == 46.6
    
    assert a.sub_stats['Crit Dmg'] == 46.8
    assert a.sub_stats['HP'] == 269
    assert a.sub_stats['ATK'] == 14
    assert a.sub_stats['Energy Recharge'] == 5.2

    assert a.type == None

