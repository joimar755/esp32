############# importar librerias o recursos#####
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
import serial
# initializations
app = Flask(__name__)
CORS(app)

'''
pip install Flask
pip install Flask-MySQLdb
pip install Flask-Cors
'''


# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'esp32'
mysql = MySQL(app)

# settings A partir de ese momento Flask utilizará esta clave para poder cifrar la información de la cookie
app.secret_key = "mysecretkey"
ser = None




# ruta para consultar todos los registros
@app.route('/getDatos', methods=['GET'])
def getAll():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM datos')
        rv = cur.fetchall()
        cur.close()
        payload = []
        content = {}
        for result in rv:
            content = {'id': result[0], 'fechahora': result[1], 'valor': result[2]}
            payload.append(content)
            content = {}
        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion":e})

  

# ruta para consultar por parametro
@app.route('/getDato/<id>',methods=['GET'])
def getDato(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM datos WHERE id = %s', (id,))
        rv = cur.fetchall()
        cur.close()
        payload = []
        content = {}
        for result in rv:
            content = {'id': result[0], 'fechahora': result[1], 'valor': result[2]}
            payload.append(content)
            content = {}
        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion":e})
    

#### ruta para crear un registro########
@app.route('/api/motion/data/create', methods=['POST'])
def sendDato():
    try:
        if request.method == 'POST':
           
            if 'valor' in request.json:
                valor = request.json['valor']  # Acceder al campo "valor" del JSON
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO datos (fechahora, valor) VALUES (NOW(), %s)", (valor,))
                mysql.connection.commit()
                return jsonify({"informacion": "Registro exitoso"})
            else:
                return jsonify({"informacion": "Campo 'valor' no encontrado en el JSON"}), 400
        
        
    except Exception as e:
        print(e)
        return jsonify({"informacion":e})

@app.route('/api/motion/data/bombillos', methods=['POST'])
def recibir_bombillos():
    data = request.get_json()
    print("📥 Datos recibidos:", data)

    # Obtener solo los campos que lleguen
    led1 = data.get("led1")
    led2 = data.get("led2")
    led3 = data.get("led3")

    try:
        cur = mysql.connection.cursor()
        query = "INSERT INTO bombillos (led1, led2, led3) VALUES (%s, %s, %s)"
        cur.execute(query, (led1, led2, led3))
        mysql.connection.commit()
        mysql.connection.close()

        return jsonify({"status": "ok", "mensaje": "Dato guardado"}), 200
    except Exception as e:
        print("❌ Error en BD:", e)
        return jsonify({"status": "error", "mensaje": "Error en BD"}), 500

    
######### ruta para actualizar################
@app.route('/updateDato/<id>', methods=['PUT'])
def updateDato(id):
    try:
        if 'valor' in request.json:
                    valor = request.json['valor']
                    cur = mysql.connection.cursor()
                    cur.execute("""
                    UPDATE datos
                    SET fechahora = (select now()),
                        valor = %s
                    WHERE id = %s
                    """, (valor, id))
                    mysql.connection.commit()
                    return jsonify({"informacion":"Registro actualizado"})
        else:
                return jsonify({"informacion": "Campo 'valor' no encontrado en el JSON"}), 400
       
    except Exception as e:
        print(e)
        return jsonify({"informacion":e})



@app.route('/deleteDato/<id>', methods = ['DELETE'])
def delete_contact(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM datos WHERE id = %s', (id,))
        mysql.connection.commit()
        return jsonify({"informacion":"Registro eliminado"}) 
    except Exception as e:
        print(e)
        return jsonify({"informacion":e})


# starting the app
if __name__ == "__main__":
   ## app.run(port=3000, debug=True)
    app.run(debug=True, host='0.0.0.0')