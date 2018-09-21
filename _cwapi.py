# -*- coding: utf-8 -*-

import pika

parameters = pika.URLParameters('amqps://Alvareaux_magicactions4CW:IKLxXIF0yl4B464m5XutybLsTzrVNDEY@api.chtwrs.com:5673/')
connection = pika.BlockingConnection(parameters)
channel = connection.channel()


def get_auth(m):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{"action": "createAuthCode","payload": {"userId": %s }}''' % m.from_user.id)


def get_auth2(m, code):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{
  "action": "grantToken",
  "payload": {
    "userId": %s,
    "authCode": "%s"
  }
}''' % (m.from_user.id, code))


def get_auth_profile(token):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{
  "token": "%s", 
  "action": "authAdditionalOperation",
  "payload": {
    "operation": "GetUserProfile"
  }
}''' % token)


def get_auth_profile2(token, rid, code):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{  
  "token": "%s",
  "action": "grantAdditionalOperation",  
  "payload": {  
    "requestId": "%s",
    "authCode": "%s"
   }  
}''' % (token, rid, code))


def get_auth_stock(m):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{
  "token": "abcdefgh12345768", 
  "action": "authAdditionalOperation",
  "payload": {
    "operation": "GetUserProfile"
  }
}''' % m.from_user.id)


def get_auth_stock2(m):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{
  "token": "abcdefgh12345768", 
  "action": "authAdditionalOperation",
  "payload": {
    "operation": "GetUserProfile"
  }
}''' % m.from_user.id)


def check_auth(m, trade):

    if (trade.cw_id == '') or (trade.cw_token == ''):
        get_auth(m)


def get_profile(cw_token):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{
  "token": "%s",
  "action": "requestProfile"
}''' % cw_token)


def wtb(token, i_code, i_number, i_cost):
    channel.basic_publish(exchange='Alvareaux_magicactions4CW_ex',
                          routing_key='Alvareaux_magicactions4CW_o',
                          body='''{
  "token": "%s",
  "action": "wantToBuy",
  "payload": {
    "itemCode": "%s", 
    "quantity": %s,
    "price": %s,
    "exactPrice": true
  }
}''' % (token, i_code, i_number, i_cost))

