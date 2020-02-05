# -*- coding: utf-8 -*-
#!/usr/bin/python

from flask import Flask, request, Response
import json
#from eventDAO import EventDAO

#dao = EventDAO()


app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    
    response_dict = {"nome_empresa" : "Softex-Recife", "liberar": "0", "hora_inicio" : "15:00", "hora_fim" : "16:00", "mensagem": "Não existe reserva"}
    if(request.method == "POST"):
        room = request.json["cod_sala_reuniao"]
        password = request.json["senha"]
        print(room, password)
        #event = dao.read(room)
        event = {"password" : "1234","name": "ITBC", "start" : "12:00", "end" : "13:00"}
        if event:
            event_pwd = event["password"]
            if event_pwd == password:
                response_dict["nome_empresa"] = event["name"]
                response_dict["liberar"] = "1"
                response_dict["hora_inicio"] = event["start"]
                response_dict["hora_fim"] = event["end"]
            else:
                response_dict["mensagem"] = "Senha incorreta"
    
    res = Response(json.dumps(response_dict)) 
    res.headers["Access-Control-Allow-Origin"] = '*'
    res.headers["Access-Control-Allow-Headers"] = '*'
    return res

@app.route("/")
def hello():
    return "Hello World"

if __name__ == "__main__":
    app.run()