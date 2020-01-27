# -*- coding: utf-8 -*-
#!/usr/bin/python

import time
from itertools import chain
import email
import imaplib
from datetime import datetime
from urllib.parse import unquote
import re
from event import Event
from eventDAO import EventDAO

CREATE_EVENT = "nova"
UPDATE_EVENT = "atualizada"
DELETE_EVENT = "eliminada"

event_dao = EventDAO()

imap_ssl_host = 'imap.gmail.com'  # imap.mail.yahoo.com
imap_ssl_port = 993
username = 'softexwhatsapp1@gmail.com'
password = '246810@softexrecife'

# Restrict mail search. Be very specific.
# Machine should be very selective to receive messages.
criteria = {
	'FROM':    'naoresponda@supersaas.com'
}
uid_max = 0


def search_string(uid_max, criteria):
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
    return '(%s)' % ' '.join(chain(*c))
    # Produce search string in IMAP format:
    #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)


def get_first_text_block(msg):
    type = msg.get_content_maintype()

    if type == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif type == 'text':
        return msg.get_payload()


server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
server.login(username, password)
server.select('INBOX')

result, data = server.uid('search', None, search_string(uid_max, criteria))
uids = [int(s) for s in data[0].split()]
if uids:
    uid_max = max(uids)
    # Initialize `uid_max`. Any UID less than or equal to `uid_max` will be ignored subsequently.

server.logout()

def get_values(text):
    splited = text.split("\\t:")
    #print(splited)
    splited = splited[1].replace("\\r\\n", " ")
    return splited

def get_tipo(text):
    text = text.replace(":\\r\\n", "")
    tipo = text.split(" ")[-1]
    return tipo

def get_schedule(text):
    text = get_values(text)
    splited = text.split()
    begin = datetime.strptime(f'{splited[1]} {splited[2]}', "%d/%m/%Y %H:%M") 
    end = datetime.strptime(f'{splited[1]} {splited[4]}', "%d/%m/%Y %H:%M")
    return begin, end

def get_room(text):
    text = get_values(text)
    text = text.replace("=", "%").replace(" ", "")
    text = unquote(text)
    return text

def get_id_reserva(text):
    text = get_values(text)
    text = text.replace(" ", "")
    return text

def get_booking_name(text):
    text = get_values(text)
    text = text.strip()
    return text

def get_phone(text):
	text = get_values(text)
	text = text.strip()
	return text

def get_obs(text):
	text = get_values(text)
	text = text.strip()
	return text

def get_mail_value(obs_field):
	emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", get_obs(obs_field).lower())
	if (emails):
		return emails
	else:
		return False

def get_info_from_mail(mail):
    tipo_index = mail.find("Dados da reserva")
    quando_index = mail.find("Quando")
    local_index = mail.find("ITBC - Reservas")
    id_reserva_index = mail.find("ID             \\t")
    nome_reserva_index = mail.find("Nome completo")
    telefone_index = mail.find("Telefone")
    obs_index = mail.find("Observa=C3=A7=C3=A3o")
    criado_index = mail.find("Criada")
    fim_index = mail.find("Pode acessar =C3=A0 agenda:")

    tipo = get_tipo(mail[tipo_index:quando_index])
    begin, end = get_schedule(mail[quando_index:local_index])
    room = get_room(mail[local_index:id_reserva_index])
    id_reserva = get_id_reserva(mail[id_reserva_index:nome_reserva_index])
    name = get_booking_name(mail[nome_reserva_index:telefone_index])
    phone = get_phone(mail[telefone_index:obs_index])
    obs = get_obs(mail[obs_index:criado_index])
    emails = get_mail_value(mail[obs_index:criado_index])
    #print(tipo, schedule, room, id_reserva, name, phone, obs, emails)
    return tipo, begin, end, room, id_reserva, name, phone, obs, emails



# Keep checking messages ...
# I don't like using IDLE because Yahoo does not support it.
while 1:
    # Have to login/logout each time because that's the only way to get fresh results.
    server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
    server.login(username, password)
    server.select('INBOX')

    result, data = server.uid('search', None, search_string(uid_max, criteria))

    uids = [int(s) for s in data[0].split()]
    for uid in uids:
        # Have to check again because Gmail sometimes does not obey UID criterion.
        if uid > uid_max:
            result, data = server.fetch(str(uid), '(RFC822)')  # fetch entire message
            msg = email.message_from_string(str(data[0][1]))    
            uid_max = uid
            tipo, begin, end, room, id_reserva, name, phone, obs, emails = get_info_from_mail(str(msg))
            event_pwd = id_reserva[:4]
            event = Event(id_reserva, name, begin, end, room, phone, emails, event_pwd)
            if tipo == CREATE_EVENT:
				event_dao.create(event)
			elif tipo == UPDATE_EVENT:
				event_dao.update(event)
			elif tipo == DELETE_EVENT:
				event_dao.delete(event)
            print(event)

    server.logout()
    time.sleep(1)