from flask import Flask, request, Response
import json

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    print(request.json)
    res = Response(json.dumps({"nome_empresa" : "Softex-Recife", "liberar": 1, "hora_inicio" : "15:00", "hora_fim" : "16:00"}))
    res.headers["Access-Control-Allow-Origin"] = '*'
    res.headers["Access-Control-Allow-Headers"] = '*'
    return res



app.run(debug=True)