from flask import Flask, render_template, send_file
import sqlite3
import pandas as pd
import io

app = Flask(__name__)

def conectar_db():
    conexion = sqlite3.connect('data.db')
    conexion.row_factory = sqlite3.Row 
    return conexion

@app.route('/')
def index():
    db = conectar_db()
    # Fetch all companies to show as cards
    empresas = db.execute("SELECT * FROM empresas").fetchall()
    db.close()
    return render_template('index.html', empresas=empresas)



from datetime import datetime

@app.route('/empresa/<int:id>')
def detalles_empresa(id):
    db = conectar_db()
    empresa = db.execute("SELECT * FROM empresas WHERE id = ?", (id,)).fetchone()
    
    # SQLite calcula los días restantes y el estado inteligente directamente
    query = """
    SELECT 
        c.nombre AS cliente, 
        d.id, d.tipo, d.total, d.pdf_url, d.id_referencia, d.fecha,
        CASE 
            WHEN d.id_referencia IS NOT NULL THEN 'Facturado'
            ELSE COALESCE(d.estado, 'Pendiente')
        END AS estado_calculado,
        CASE 
            WHEN d.id_referencia IS NOT NULL THEN 'pagado'
            ELSE LOWER(COALESCE(d.estado, 'pendiente'))
        END AS clase_estado,
        -- Calculamos la diferencia de días directamente en SQL
        CAST(90 - (julianday('now') - julianday(substr(d.fecha, 1, 10))) AS INTEGER) AS dias_restantes
    FROM clientes c
    LEFT JOIN documentos d ON c.id = d.cliente_id
    WHERE c.empresa_id = ?
    ORDER BY d.fecha DESC
    """
    datos = db.execute(query, (id,)).fetchall()
    db.close()
    return render_template('detalles.html', empresa=empresa, datos=datos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)