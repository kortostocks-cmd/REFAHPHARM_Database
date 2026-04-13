from flask import Flask, render_template, send_file
import sqlite3
import pandas as pd
import io
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

def conectar_db():
    conexion = sqlite3.connect('data.db')
    conexion.row_factory = sqlite3.Row 
    return conexion

@app.route('/')
def index():
    db = conectar_db()
    try:
        empresas = db.execute("SELECT * FROM empresas").fetchall()
        return render_template('index.html', empresas=empresas)
    finally:
        db.close()

@app.route('/empresa/<int:id>')
def detalles_empresa(id):
    db = conectar_db()
    try:
        empresa = db.execute("SELECT * FROM empresas WHERE id = ?", (id,)).fetchone()
        
        query = """
        SELECT c.nombre AS cliente, d.id, d.tipo, d.total, d.pdf_url, d.id_referencia, d.fecha, d.estado
        FROM clientes c
        LEFT JOIN documentos d ON c.id = d.cliente_id
        WHERE c.empresa_id = ?
        ORDER BY d.fecha DESC
        """
        filas = db.execute(query, (id,)).fetchall()
        
        grupos_por_mes = defaultdict(list)
        facturas_fiscales = []
        hoy = datetime.now()

        for f in filas:
            doc = dict(f)
            # Lógica de Facturado: Si tiene referencia, es Facturado
            if doc['id_referencia']:
                doc['estado_calculado'] = 'Facturado'
                doc['clase_estado'] = 'pagado'
                facturas_fiscales.append(doc)
            else:
                doc['estado_calculado'] = doc['estado'] or 'Pendiente'
                doc['clase_estado'] = doc['estado'].lower() if doc['estado'] else 'pendiente'

            # Cálculo de tiempo y agrupación por carpetas (meses)
            if doc['fecha']:
                try:
                    fecha_dt = datetime.strptime(doc['fecha'][:10], '%Y-%m-%d')
                    doc['dias_restantes'] = max(0, 90 - (hoy - fecha_dt).days)
                    mes_nombre = fecha_dt.strftime('%B %Y').capitalize()
                    grupos_por_mes[mes_nombre].append(doc)
                except:
                    grupos_por_mes["Sin Fecha"].append(doc)
            else:
                grupos_por_mes["Sin Fecha"].append(doc)

        # El return debe ir FUERA del bucle for
        return render_template('detalles.html', 
                            empresa=empresa, 
                            grupos=grupos_por_mes, 
                            facturas=facturas_fiscales)
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)