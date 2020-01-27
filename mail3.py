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
import base64

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


CREATE_EVENT = "nova"
UPDATE_EVENT = "atualizada"
DELETE_EVENT = "eliminada"

event_dao = EventDAO()

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
	id_reserva_index = mail.find("ID")
	nome_reserva_index = mail.find("Nome completo")
	telefone_index = mail.find("Telefone")
	obs_index = mail.find("Observação")
	criado_index = mail.find("Criada")
	fim_index = mail.find("Pode acessar à agenda:")

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

def main():
	store = file.Storage('token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)
	service = build('gmail', 'v1', http=creds.authorize(Http()))
	
	# Call the Gmail API to fetch INBOX
	results = service.users().messages().list(userId='me',labelIds = ['UNREAD', 'INBOX'], maxResults=10).execute()
	messages = results.get('messages', [])
	if not messages:
		pass
	#print ("No messages found.")
	else:
		#print ("Message snippets:")
		for message in messages:
			msg = get_mail(service, message)
			tipo, begin, end, room, id_reserva, name, phone, obs, emails = get_info_from_mail(msg) 
			event_pwd = id_reserva[:4]
			event = Event(id_reserva, name, begin, end, room, phone, emails, event_pwd)
			if tipo == CREATE_EVENT:
				event_dao.create(event)
			elif tipo == UPDATE_EVENT:
				event_dao.update(event)
			elif tipo == DELETE_EVENT:
				event_dao.delete(event)
			print(event)
			print(msg)


if __name__ == '__main__':
	while True:
		main()