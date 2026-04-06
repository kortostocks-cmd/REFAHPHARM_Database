from flask import Flask #importnte para el servidor en un wifi
import sqlite3 #viene ya instalado solo falta el import

# creacion de la app
app = Flask(__name__)

#funcion para leer la base de datos conectada
def conectar_db():
    conexion = sqlite3.connect('data.db')
    conexion.row_factory = sqlite3.Row #hace que cuando pidamos datos, podamos llamarlos por el nombre de su columna (ej. fila['nombre']) en lugar de por números.
    return conexion

#ruta de la pagina principal
@app.route('/')
def inicio():
    return "<h1>funciona el servidor</h1>"

#encender motor
if __name__ == '__main__':#main es este archivo osea si no es este archivo no funciona
    
    app.run(host='0.0.0.0', port=5000, debug=True)
    #host = acepta visitas de quien este conectadp al wifi
    #port = numero de carril o puesto de la pagina
    #debug explica los fallos en consola y automaticamente se actualiza



