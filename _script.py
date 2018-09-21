# -*- coding: utf-8 -*-

import re
from _config import *
from datetime import datetime


def time_string(stamp):

    from main import tz

    date = datetime.fromtimestamp(stamp, tz).strftime("%A, %B %d, ""%Y %H:%M:%S")
    return date


def db_file():

    from main import Trade, Profile, db

    with db:
        db.create_tables([Trade, Profile])


def db_check(m):

    from main import Trade, Profile, bot
    from _text import TgMsgText

    user_list = []
    for user in Trade.select().where(Trade.user_id == m.from_user.id):
        user_list.append(user.user_id)

    if m.from_user.id in user_list:
        pass

    else:
        Trade.create(user_id=m.from_user.id)
        Profile.create(userId=m.from_user.id)
        bot.send_message(65706097, TgMsgText.Priority.Admin.add.format('@' + m.from_user.username, m.from_user.id),
                         parse_mode='HTML')


def db_userid_check(m):

    from main import Trade

    user_list = []
    for user in Trade.select().where(Trade.user_id == m.from_user.id):
        user_list.append(user.user_id)

    if m.from_user.id in user_list:
        return True
    else:
        return False


def lines_count(s):
    return len(s.splitlines())


def parse(text):

    from _text import id_list

    local_list = []
    global_list = []
    text_list = ''

    s, global_list, text_list = False, global_list, text_list

    if lines_count(text) > 5:
        return s, global_list
    else:
        try:

            text_split = text.split('\n')
            for row in text_split:
                r = re.search('(\d+) - (\d+)', row).group(1)
                c = re.search('(\d+) - (\d+)', row).group(2)
                if r in id_list:
                    local_list.append(r)
                    local_list.append(c)
                else:
                    break
                global_list.append(local_list)
                local_list = []

            s = True
            text_list = text

            return s, global_list, text_list

        except:

            return s, global_list, text_list


def admin_update():

    from main import Trade
    from _personal import owner_list

    for t in Trade.select().where((Trade.priority == 3)):
        owner_list.add(t.user_id)


def get_code(m):
    code = re.search('Code (\d+) to authorize Alvareaux_magicactions4CW', m.text).group(1)

    return code


def get_json(body):

    import json

    xinvalid = re.compile(r'\\x([0-9a-fA-F]{2})')

    def fix_xinvalid(m):
        return chr(int(m.group(1), 16))

    def fix(s):
        return xinvalid.sub(fix_xinvalid, s)

    return json.loads(fix(body[2:-1]))


def get_token(body):

    text = get_json(body)

    userid = text['payload']['userId']
    cw_id = text['payload']['id']
    cw_token = text['payload']['token']

    return userid, cw_id, cw_token


def get_uuid(body):

    text = get_json(body)

    uuid = text['uuid']
    userid = text['payload']['userId']

    return uuid, userid


def get_userid(body):

    text = get_json(body)

    userid = text['payload']['userId']

    return userid


def get_profile_stats(body):

    text = get_json(body)

    atk = text['payload']['profile']['atk']
    ddef = text['payload']['profile']['def']
    castle = text['payload']['profile']['castle']
    cclass = text['payload']['profile']['class']
    exp = text['payload']['profile']['exp']
    lvl = text['payload']['profile']['lvl']
    gold = text['payload']['profile']['gold']
    guild = text['payload']['profile']['guild']
    guild_tag = text['payload']['profile']['guild_tag']
    mana = text['payload']['profile']['mana']
    try:
        pouches = text['payload']['profile']['pouches']
    except KeyError:
        pouches = 0
    stamina = text['payload']['profile']['stamina']
    userName = text['payload']['profile']['userName']
    userId = text['payload']['userId']

    return atk, ddef, castle, cclass, exp, lvl, gold, guild, guild_tag, mana, pouches, stamina, userName, userId


def get_wtb_text(body):

    text = get_json(body)

    item = text['payload']['itemName']
    userId = text['payload']['userId']

    return item, userId


def keyboard_markup(trade):

    from telebot import types

    if trade.priority == -1:
        markup = types.ReplyKeyboardRemove(selective=False)

    elif trade.priority == 0:
        markup = types.ReplyKeyboardRemove(selective=False)

    elif trade.priority in [1, 2]:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        b_help = types.KeyboardButton('📖Помощь')
        b_edit = types.KeyboardButton('📋Редактор списка')
        if trade.enable:
            b_start = types.KeyboardButton('❌Off')
        else:
            b_start = types.KeyboardButton('✅️On')
        markup.row(b_help, b_edit, b_start)

    elif trade.priority == 3:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        b_help = types.KeyboardButton('📖Помощь')
        b_edit = types.KeyboardButton('📋Редактор списка')
        b_admin = types.KeyboardButton('⚙️Администрирование')
        if trade.enable:
            b_start = types.KeyboardButton('❌Off')
        else:
            b_start = types.KeyboardButton('✅️On')
        markup.row(b_help, b_edit, b_start)
        markup.row(b_admin)

    else:
        markup, trade.priority = False

    return markup, trade.priority

