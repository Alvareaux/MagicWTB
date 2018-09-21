# -*- coding: utf-8 -*-

from _script import *
from _cwapi import *
from _text import *
from _personal import *

import multiprocessing
import math
import ast
import time
from os.path import exists
from multiprocessing import *

import telebot
from telebot import types
from telebot.apihelper import ApiException

import pytz
from peewee import *

# Token creation

if exists('token.txt'):
    with open('token.txt') as f:
        token = f.readline().strip()
else:
    msg = SysMsgText.Token.nofile
    token = input(msg)
    with open('token.txt', 'w') as f:
        f.write(token)
    print(SysMsgText.Token.saved)

# Lib const
bot = telebot.AsyncTeleBot(token)
bot_id = int(token.split(':')[0])

db = SqliteDatabase('bot.db')

tz = pytz.timezone(tz_name)

global boost_enable
boost_enable = multiprocessing.Value('i', 0)


def listener(messages):
    for m in messages:
        print('%s[%s]:%s – %s' % (m.from_user.username, m.from_user.id, m.text if m.text else m.content_type,
                                  time_string(m.date)))
        with open('{}.txt'.format(m.from_user.id), 'a', encoding='utf-8') as file:
            file.write('%s[%s]:%s – %s' % (m.from_user.username, m.from_user.id, m.text if m.text else m.content_type,
                                           time_string(m.date))
                       + '\n')


bot.set_update_listener(listener)


# Peewee database instance
class BaseModel(Model):
    class Meta:
        database = db


class Trade(BaseModel):
    user_id = DateField(unique=True)

    cw_id = CharField(default='')
    cw_token = CharField(default='')
    rid = CharField(default='')
    allow = BooleanField(default=False)

    priority = DateField(default=0)
    adv_priority = DateField(default=0)

    enable = BooleanField(default=False)
    status = DateField(default=1)

    list = CharField(default='')
    list_text = CharField(default='')


class Profile(BaseModel):
    atk = CharField(default='')
    ddef = CharField(default='')
    castle = CharField(default='')
    cclass = CharField(default='')
    exp = CharField(default='')
    lvl = CharField(default='')
    gold = CharField(default='')
    guild = CharField(default='')
    guild_tag = CharField(default='')
    mana = CharField(default='')
    pouches = CharField(default='')
    stamina = CharField(default='')
    userName = CharField(default='')
    userId = CharField(default='')


if exists('bot.db'):
    print(SysMsgText.DB.load)
else:
    print(SysMsgText.DB.nofile)
    db_file()


@bot.message_handler(commands=['start'])
def bot_start(m):
    db_check(m)

    trade = Trade.get(Trade.user_id == m.from_user.id)

    check_auth(m, trade)

    if (trade.cw_id == '') or (trade.cw_token == ''):
        bot.send_message(m.chat.id, TgMsgText.no_auth, parse_mode='Markdown')
        return False

    markup, k_priority = keyboard_markup(trade)

    if k_priority == -1:
        bot.send_message(m.chat.id, TgMsgText.Priority.User.ban, reply_markup=markup)
    elif k_priority == 0:
        bot.send_message(m.chat.id, TgMsgText.Priority.User.add, reply_markup=markup)
    elif k_priority in [1, 2]:
        bot.send_message(m.chat.id, TgMsgText.Priority.User.accept, reply_markup=markup)
    elif k_priority == 3:
        bot.send_message(m.chat.id, TgMsgText.Priority.User.accept, reply_markup=markup)


@bot.message_handler(commands=['help'])
def bot_help(m):
    if db_userid_check(m):

        trade = Trade.get(Trade.user_id == m.from_user.id)

        if trade.priority == -1:
            bot.send_message(m.chat.id, TgMsgText.Priority.User.ban)
        elif trade.priority == 0:
            bot.send_message(m.chat.id, TgMsgText.Priority.User.add)
        elif trade.priority in [1, 2, 3]:
            bot.send_message(m.chat.id, TgMsgText.Priority.User.nohelp)
    else:
        db_check(m)


@bot.message_handler(commands=['update'])
def bot_update(m):
    if m.from_user.id in owner_list:
        admin_update()
        bot.send_message(m.chat.id, TgMsgText.Help.update)


@bot.message_handler(commands=['update_profile'])
def bot_update(m):
    db_check(m)

    update = Trade.update(cw_id='', cw_token='').where(Trade.user_id == m.from_user.id)
    update.execute()

    trade = Trade.get(Trade.user_id == m.from_user.id)

    bot.send_message(m.chat.id, TgMsgText.no_auth)

    check_auth(m, trade)


@bot.message_handler(commands=['g_boost'])
def global_boost(m):
    if m.from_user.id in owner_list:

        trade_old = Trade
        if boost_enable.value == 1:
            boost_enable.value = 0

            bot.send_message(m.from_user.id, TgMsgText.Priority.User.g_boost_no)

            trade = Trade.get(Trade.user_id == m.from_user.id)

            for t in trade_old.select().where((Trade.adv_priority == 1)):

                markup, k_priority = keyboard_markup(trade)

                if k_priority in [1, 2]:
                    bot.send_message(t.user_id, TgMsgText.Priority.User.boost_no, reply_markup=markup)
                elif k_priority == 3:
                    bot.send_message(t.user_id, TgMsgText.Priority.User.boost_no, reply_markup=markup)

        elif boost_enable.value == 0:
            boost_enable.value = 1

            bot.send_message(m.from_user.id, TgMsgText.Priority.User.g_boost)

            trade = Trade.get(Trade.user_id == m.from_user.id)

            for t in Trade.select().where((Trade.adv_priority == 1)):

                markup, k_priority = keyboard_markup(trade)

                if k_priority in [1, 2]:
                    bot.send_message(t.user_id, TgMsgText.Priority.User.boost, reply_markup=markup)
                elif k_priority == 3:
                    bot.send_message(t.user_id, TgMsgText.Priority.User.boost, reply_markup=markup)
        else:
            boost_enable.value = 0


@bot.message_handler(commands=['set'])
def bot_set(m):
    if m.from_user.id in owner_list:
        try:
            text = m.text.split(' ', 1)[1]

            user_id = text.split(' ')[0].strip()
            priority = int(text.split(' ', 1)[1].strip())

            try:
                trade = Trade.get(Trade.user_id == user_id)
            except:
                pass

            if trade:
                if priority in [-1, 0, 1, 2, 3]:
                    update = Trade.update(priority=priority).where(Trade.user_id == user_id)
                    update.execute()

                    try:
                        trade = Trade.get(Trade.user_id == user_id)
                    except:
                        pass

                    if trade:

                        markup, k_priority = keyboard_markup(trade)

                        if k_priority == -1:
                            bot.send_message(user_id, TgMsgText.Priority.User.ban, reply_markup=markup)
                        elif k_priority == 0:
                            bot.send_message(user_id, TgMsgText.Priority.User.add, reply_markup=markup)
                        elif k_priority in [1, 2]:
                            bot.send_message(user_id, TgMsgText.Priority.User.accept, reply_markup=markup)
                        elif k_priority == 3:
                            bot.send_message(user_id, TgMsgText.Priority.User.accept, reply_markup=markup)
                else:
                    bot.send_message(m.chat.id, TgMsgText.Table.miss_priority)
            else:
                bot.send_message(m.chat.id, TgMsgText.Table.miss_userid)
        except:
            bot.send_message(m.chat.id, TgMsgText.Table.miss_set)
    else:
        bot.send_message(m.chat.id, TgMsgText.not_owner)


@bot.message_handler(commands=['boost'])
def bot_set(m):
    if m.from_user.id in owner_list:
        try:
            text = m.text.split(' ', 1)[1]

            user_id = text.split(' ')[0].strip()
            priority = int(text.split(' ', 1)[1].strip())

            try:
                trade = Trade.get(Trade.user_id == user_id)
            except:
                pass

            if trade:
                if trade.priority in [1, 2, 3]:
                    if priority in [1, 0]:
                        update = Trade.update(adv_priority=priority).where(Trade.user_id == user_id)
                        update.execute()

                        try:
                            trade = Trade.get(Trade.user_id == user_id)
                        except:
                            pass

                        markup, k_priority = keyboard_markup(trade)

                        if trade:
                            if (priority == 1) and (boost_enable == 1):
                                if k_priority in [1, 2]:
                                    bot.send_message(user_id, TgMsgText.Priority.User.boost, reply_markup=markup)
                                elif k_priority == 3:
                                    bot.send_message(user_id, TgMsgText.Priority.User.boost, reply_markup=markup)
                            elif (priority == 0) or (boost_enable == 0):
                                if k_priority in [1, 2]:
                                    bot.send_message(user_id, TgMsgText.Priority.User.boost_no, reply_markup=markup)
                                elif k_priority == 3:
                                    bot.send_message(user_id, TgMsgText.Priority.User.boost_no, reply_markup=markup)
                    else:
                        bot.send_message(m.chat.id, TgMsgText.Table.miss_boost_value)
                else:
                    bot.send_message(m.chat.id, TgMsgText.Table.miss_priority_enable)
            else:
                bot.send_message(m.chat.id, TgMsgText.Table.miss_userid)
        except:
            bot.send_message(m.chat.id, TgMsgText.Table.miss_boost)
    else:
        bot.send_message(m.chat.id, TgMsgText.not_owner)


@bot.message_handler(commands=['switch'])
def bot_set(m):
    if m.from_user.id in owner_list:
        try:
            text = m.text.split(' ', 1)[1]

            user_id = text.split(' ')[0].strip()
            switch = int(text.split(' ', 1)[1].strip())

            try:
                trade = Trade.get(Trade.user_id == user_id)
            except:
                pass

            if trade:
                if trade.priority in [1, 2, 3]:
                    if switch in [1, 0]:
                        update = Trade.update(enable=switch).where(Trade.user_id == user_id)
                        update.execute()

                        if switch == 1:
                            bot.send_message(m.chat.id, TgMsgText.Enable.on)
                        elif switch == 0:
                            bot.send_message(m.chat.id, TgMsgText.Enable.off)
                    else:
                        bot.send_message(m.chat.id, TgMsgText.Table.miss_enable_value)
                else:
                    bot.send_message(m.chat.id, TgMsgText.Table.miss_priority_enable)
            else:
                bot.send_message(m.chat.id, TgMsgText.Table.miss_userid)
        except:
            bot.send_message(m.chat.id, TgMsgText.Table.miss_enable)
    else:
        bot.send_message(m.chat.id, TgMsgText.not_owner)


@bot.message_handler(commands=['all'])
def bot_all(m):
    if m.from_user.id in owner_list:
        text = TgMsgText.Priority.Admin.text
        for users in Trade.select():
            text = text + ''.join('`' + str(users.user_id) + '` – `' + str(users.priority) + '` – `' +
                                  str(users.adv_priority) + '` – `' + str(users.enable) + '`' + '\n')
        text = text + ''.join(TgMsgText.Priority.Admin.text_end)
        bot.send_message(m.chat.id, text, parse_mode='Markdown')
    else:
        bot.send_message(m.chat.id, TgMsgText.not_owner)


@bot.message_handler(func=lambda m: True)
def grinder(m):
    if db_userid_check(m):
        trade = Trade.get(Trade.user_id == m.from_user.id)

        get_profile(trade.cw_token)

        if trade.priority == -1:
            bot.send_message(m.chat.id, TgMsgText.Priority.User.ban)
        elif trade.priority == 0:
            bot.send_message(m.chat.id, TgMsgText.Priority.User.add)
        else:
            if (trade.cw_id == '') or (trade.cw_token == ''):
                if '- issue a wtb/wts/rm commands on your behalf' in m.text:
                    code = get_code(m)

                    get_auth2(m, code)
                else:
                    bot.send_message(m.chat.id, TgMsgText.no_auth, parse_mode='Markdown')
            else:
                if '- read your profile information' in m.text:

                    code = get_code(m)

                    trade = Trade.get(Trade.user_id == m.from_user.id)

                    get_auth_profile2(trade.cw_token, trade.rid, code)

                if trade.priority in [1, 2, 3]:
                    if trade.status == 1:

                        markup, k_priority = keyboard_markup(trade)

                        if m.text == '📖Помощь':
                            if k_priority in [1, 2]:

                                text = TgMsgText.Help.user + '\n' + TgMsgText.full_list_markdown + \
                                       ''.join(trade.list_text) + '\n'

                                if (trade.adv_priority == 1) and (global_boost == 1):
                                    boost_personal_enable = '*True*'
                                elif (trade.adv_priority == 0) or (global_boost == 0):
                                    boost_personal_enable = '*False*'
                                else:
                                    boost_personal_enable = '*False*'

                                bot.send_message(m.chat.id, text.format(boost_personal_enable), reply_markup=markup,
                                                 parse_mode='Markdown')
                            elif k_priority == 3:

                                text = TgMsgText.Help.user + '\n' + TgMsgText.full_list_markdown + \
                                       ''.join(trade.list_text) + '\n'

                                if boost_enable.value == 1:
                                    boost_personal_enable = '*True*'
                                elif boost_enable.value == 0:
                                    boost_personal_enable = '*False*'
                                else:
                                    boost_personal_enable = '*False*'

                                if trade.adv_priority == 1:
                                    boost_personal_enable = boost_personal_enable + ''.join('(True)')
                                elif trade.adv_priority == 0:
                                    boost_personal_enable = boost_personal_enable + ''.join('(False)')

                                bot.send_message(m.chat.id, text.format(boost_personal_enable), reply_markup=markup,
                                                 parse_mode='Markdown')
                        elif m.text == '⚙️Администрирование':
                            if k_priority == 3:
                                bot.send_message(m.chat.id, TgMsgText.Help.admin, reply_markup=markup, parse_mode='HTML')
                        elif m.text == '✅️On':
                            update = Trade.update(enable=True).where(Trade.user_id == m.from_user.id)
                            update.execute()

                            trade = Trade.get(Trade.user_id == m.from_user.id)
                            markup, k_priority = keyboard_markup(trade)

                            if (trade.cw_id == '') or (trade.cw_token == ''):
                                bot.send_message(m.chat.id, TgMsgText.no_auth, parse_mode='Markdown')
                                return False

                            if k_priority in [1, 2]:
                                bot.send_message(m.chat.id, TgMsgText.Enable.on, reply_markup=markup)
                            elif k_priority == 3:
                                bot.send_message(m.chat.id, TgMsgText.Enable.on, reply_markup=markup)
                        elif m.text == '❌Off':
                            update = Trade.update(enable=False).where(Trade.user_id == m.from_user.id)
                            update.execute()

                            trade = Trade.get(Trade.user_id == m.from_user.id)
                            markup, k_priority = keyboard_markup(trade)

                            if (trade.cw_id == '') or (trade.cw_token == ''):
                                bot.send_message(m.chat.id, TgMsgText.no_auth, parse_mode='Markdown')
                                return False

                            if k_priority in [1, 2]:
                                bot.send_message(m.chat.id, TgMsgText.Enable.off, reply_markup=markup)
                            elif k_priority == 3:
                                bot.send_message(m.chat.id, TgMsgText.Enable.off, reply_markup=markup)
                        elif m.text == '📋Редактор списка':

                            update = Trade.update(status=2).where(Trade.user_id == m.from_user.id)
                            update.execute()

                            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                            b_back = types.KeyboardButton('⬅️Назад')
                            markup.row(b_back)
                            bot.send_message(m.chat.id, TgMsgText.edit_list, reply_markup=markup, parse_mode='Markdown')

                            full_list = TgMsgText.full_list + ''.join(trade.list_text) + '\n'

                            time.sleep(0.1)

                            bot.send_message(m.chat.id, full_list, reply_markup=markup, parse_mode='HTML')
                    elif trade.status == 2:
                        if m.text == '⬅️Назад':

                            update = Trade.update(status=1).where(Trade.user_id == m.from_user.id)
                            update.execute()
                            markup, k_priority = keyboard_markup(trade)

                            if k_priority in [1, 2]:
                                bot.send_message(m.chat.id, TgMsgText.Priority.User.accept, reply_markup=markup)
                            elif k_priority == 3:
                                bot.send_message(m.chat.id, TgMsgText.Priority.User.accept, reply_markup=markup)
                        else:
                            try:

                                s, list, list_text = parse(m.text)

                                if s is False:
                                    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                                    b_back = types.KeyboardButton('⬅️Назад')
                                    markup.row(b_back)
                                    bot.send_message(m.chat.id, TgMsgText.Priority.User.error, reply_markup=markup)
                                else:

                                    update = Trade.update(status=1, list=list, list_text=list_text).where(Trade.user_id == m.from_user.id)
                                    update.execute()

                                    trade = Trade.get(Trade.user_id == m.from_user.id)
                                    markup, k_priority = keyboard_markup(trade)

                                    if k_priority in [1, 2]:
                                        bot.send_message(m.chat.id, TgMsgText.list_edited, reply_markup=markup,
                                                         parse_mode='Markdown')
                                    elif k_priority == 3:
                                        bot.send_message(m.chat.id, TgMsgText.list_edited, reply_markup=markup,
                                                         parse_mode='Markdown')
                            except:
                                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                                b_back = types.KeyboardButton('⬅️Назад')
                                markup.row(b_back)
                                bot.send_message(m.chat.id, TgMsgText.Priority.User.error, reply_markup=markup)
    else:
        db_check(m)


def telepol():
    try:
        bot.polling(none_stop=True, timeout=10)
    except ApiException:
        bot.stop_polling()
        time.sleep(1)
        telepol()


def sequence_sender(boost_enable, sleep_time):

    while True:

        users = []
        if boost_enable.value == 1:
            for user in Trade.select().where((Trade.priority == 3) & (Trade.enable == 1) & (Trade.adv_priority == 0)):
                get_profile(user.cw_token)

                profile = Profile.get(Profile.userId == user.user_id)

                local = []

                if int(profile.gold) > 0:

                    local.append(user.cw_token)
                    local.append(ast.literal_eval(user.list))
                    local.append(profile.gold)
                    users.append(local)
        else:
            for user in Trade.select().where((Trade.priority == 3) & (Trade.enable == 1)):
                get_profile(user.cw_token)

                profile = Profile.get(Profile.userId == user.user_id)

                local = []

                if int(profile.gold) > 0:
                    local.append(user.cw_token)
                    local.append(ast.literal_eval(user.list))
                    local.append(profile.gold)
                    users.append(local)

        #        time1 = time.time()
        for i in range(10):
            for cw_token in users:
                for pair in cw_token[1]:
                    wtb(cw_token[0], pair[0], (math.floor(int(cw_token[2]) / int(pair[1]))), pair[1])
                    time.sleep(sleep_time)


#        time2 = time.time()
#        print('{:s} function took {:.3f} ms'.format('s2', (time2 - time1) * 1000.0))
#        sys.stdout.flush()


def boost(boost_enable):
    while True:
        if boost_enable.value == 1:

            users = []

            for user in Trade.select().where((Trade.adv_priority == 1) & (Trade.enable == 1)):

                get_profile(user.cw_token)

                profile = Profile.get(Profile.userId == user.user_id)

                local = []

                if int(profile.gold) > 0:
                    local.append(user.cw_token)
                    local.append(ast.literal_eval(user.list))
                    local.append(profile.gold)
                    users.append(local)

            #        time1 = time.time()
            for i in range(10):
                for cw_token in users:
                    for pair in cw_token[1]:
                        wtb(cw_token[0], pair[0], (math.floor(int(cw_token[2]) / int(pair[1]))), pair[1])
                        time.sleep(PriorityTime.boost)
        #        time2 = time.time()
        #        print('{:s} function took {:.3f} ms'.format('s2', (time2 - time1) * 1000.0))
        #        sys.stdout.flush()
        else:
            time.sleep(10)


def sequence_grinder():
    while True:
        method_frame, header_frame, body = channel.basic_get('Alvareaux_magicactions4CW_i')
        if method_frame:
            channel.basic_ack(method_frame.delivery_tag)
            print(body)
            if '"action":"grantToken","result":"Ok"' in str(body):
                userid, cw_id, cw_token = get_token(str(body))

                update = Trade.update(cw_id=cw_id, cw_token=cw_token).where(Trade.user_id == userid)
                update.execute()

                get_auth_profile(cw_token)

            elif '"action":"authAdditionalOperation","result":"Ok"' in str(body):
                uuid, userid = get_uuid(str(body))

                update = Trade.update(rid=uuid).where(Trade.user_id == userid)
                update.execute()

            elif '"action":"grantAdditionalOperation","result":"Ok"' in str(body):
                userid = get_userid(body)

                update = Trade.update(allow=True).where(Trade.user_id == userid)
                update.execute()

            elif '"action":"requestProfile","result":"Ok"' in str(body):
                atk, ddef, castle, cclass, exp, lvl, gold, guild, guild_tag, mana, pouches, stamina, userName, \
                userId = get_profile_stats(str(body))

                update = Profile.update(atk=atk, ddef=ddef, castle=castle, cclass=cclass, exp=exp, lvl=lvl, gold=gold,
                                        guild=guild, guild_tag=guild_tag, mana=mana, pouches=pouches, stamina=stamina,
                                        userName=userName).where(Profile.userId == userId)
                update.execute()

            elif '"action":"wantToBuy","result":"Ok"' in str(body):
                item, user_id = get_wtb_text(body)

                bot.send_message(user_id, TgMsgText.gratz.format(item))


        time.sleep(0.1)


if __name__ == '__main__':

    admin_update()

    g_boost = Process(target=boost, args=(boost_enable,))
    sp3 = Process(target=sequence_sender, args=(boost_enable, PriorityTime.p3))
    sp2 = Process(target=sequence_sender, args=(boost_enable, PriorityTime.p2))
    sp1 = Process(target=sequence_sender, args=(boost_enable, PriorityTime.p1))

    amqp = Process(target=sequence_grinder)

    g_boost.start()
    sp3.start()
    sp2.start()
    sp1.start()

    amqp.start()

    telepol()

