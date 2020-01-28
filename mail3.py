# -*- coding: utf-8 -*-
#!/usr/bin/python

import time
from itertools import chain
import email
import imaplib
from datetime import datetime
import re
#from event import Event
#from eventDAO import EventDAO
import base64

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def get_mail(service, message):
	labelIds = {"removeLabelIds": ["UNREAD"]}
	msg = service.users().messages().get(userId='me', id=message['id']).execute()
	msgData = msg['payload']['body']['data']
	msgData = base64.urlsafe_b64decode(msgData.encode("utf-8")).decode('utf-8')
	unread = service.users().messages().modify(userId='me', id=message['id'], body=labelIds).execute()
	return msgData


CREATE_EVENT = "nova"
UPDATE_EVENT = "atualizada"
DELETE_EVENT = "eliminada"

event_dao = EventDAO()

def get_type(mail):
	mail_type = list(filter(lambda x: "Dados da reserva" in x, mail))
	if(len(mail_type) == 0):
		return None
	mail_type = mail_type[0].split(" ")[-1]
	mail_type = mail_type.replace(":", "")
	mail_type = mail_type.strip()
	return mail_type

def get_schedule(mail):
	text = list(filter(lambda x: "Quando" in x, mail))
	if(len(text) == 0):
		return None, None
	text = text[0].split("\t:")[1]
	splited = text.split()
	begin = datetime.strptime(splited[1] + " " + splited[2], "%d/%m/%Y %H:%M") 
	end = datetime.strptime(splited[1] + " " + splited[4], "%d/%m/%Y %H:%M")
	return begin, end

def get_room(mail):
	text = list(filter(lambda x: "ITBC - Reservas" in x, mail))
	if(len(text) == 0):
		return None
	text = text[0].split("\t:")[1]
	return text.strip()

def get_booking_name(mail):
	text = list(filter(lambda x: "Nome completo" in x, mail))
	if(len(text) == 0):
		return None
	text = text[0].split("\t:")[1]
	text = text.strip()
	return text

def get_id_reserva(mail):
	text = list(filter(lambda x: "ID" in x, mail))
	if(len(text) == 0):
		return None
	text = text[0].split("\t:")[1]
	text = text.strip()
	return text

def get_phone(mail):
	text = list(filter(lambda x: "Telefone" in x, mail))
	if(len(text) == 0):
		return None
	text = text[0].split("\t:")[1]
	text = text.strip()
	return text

def get_mail_value(mail):
	text = " ".join(mail)
	emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text.lower())
	if (emails):
		return emails
	return None


def get_info_from_mail(mail):
	mail_splited = mail.split("\r\n")

	tipo = get_type(mail_splited)
	begin, end = get_schedule(mail_splited)
	room = get_room(mail_splited)
	id_reserva = get_id_reserva(mail_splited)
	name = get_booking_name(mail_splited)
	phone = get_phone(mail_splited)
	emails = get_mail_value(mail_splited)
	#print(tipo, schedule, room, id_reserva, name, phone, obs, emails)
	return tipo, begin, end, room, id_reserva, name, phone, emails

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
			tipo, begin, end, room, id_reserva, name, phone, emails = get_info_from_mail(msg) 
			if(tipo and begin and end and room and id_reserva and emails):
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