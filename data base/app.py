from flask import Flask, render_template_string, send_file
import sqlite3
import pandas as pd
import io

app = Flask(__name__)

def conectar_db():
    # Tu carpeta se llama data,bd y el archivo data.db
    conexion = sqlite3.connect('data.db')
    conexion.row_factory = sqlite3.Row 
    return conexion

@app.route('/')
def inicio():
    db = conectar_db()
    
    # CONSULTA AJUSTADA: Incluimos d.id_referencia
    consulta = """
    SELECT 
        d.id AS numero_documento,
        d.id_referencia AS numero_referencia,
        e.nombre AS empresa,
        c.nombre AS cliente,
        c.telefono,
        c.email,
        d.tipo,
        d.total,
        d.pdf_url
    FROM documentos d
    JOIN empresas e ON d.empresa_id = e.id
    JOIN clientes c ON d.cliente_id = c.id;
    """
    documentos = db.execute(consulta).fetchall()
    db.close()
    
    diseño = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Control - WiFi Empresa</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: auto; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
            h1 { color: #202124; margin: 0; }
            
            /* Botón de Excel */
            .btn-excel { background: #1d6f42; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; }
            .btn-excel:hover { background: #155231; }

            table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
            th { background: #3c4043; color: white; padding: 15px; text-align: left; font-size: 14px; }
            td { padding: 12px 15px; border-bottom: 1px solid #f1f3f4; font-size: 14px; color: #3c4043; }
            tr:hover { background: #f1f3f4; }
            
            .badge { padding: 5px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; }
            .factura { background: #d2e3fc; color: #174ea6; }
            .cotizacion { background: #feefc3; color: #af5d00; }
            
            .link-pdf { color: #d93025; text-decoration: none; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Registro de Documentos</h1>
                <a href="/descargar_excel" class="btn-excel">📥 Descargar Excel</a>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Doc #</th>
                        <th>Ref #</th>
                        <th>Empresa Emisora</th>
                        <th>Cliente</th>
                        <th>Tipo</th>
                        <th>Monto Total</th>
                        <th>Documento</th>
                    </tr>
                </thead>
                <tbody>
                    {% for d in documentos %}
                    <tr>
                        <td><b>{{ d['numero_documento'] }}</b></td>
                        <td>{{ d['numero_referencia'] if d['numero_referencia'] else '---' }}</td>
                        <td>{{ d['empresa'] }}</td>
                        <td>
                            {{ d['cliente'] }}<br>
                            <small style="color: #70757a;">{{ d['email'] }}</small>
                        </td>
                        <td>
                            <span class="badge {{ d['tipo'] }}">{{ d['tipo'] }}</span>
                        </td>
                        <td><b>${{ d['total'] }}</b></td>
                        <td>
                            {% if d['pdf_url'] %}
                                <a href="{{ d['pdf_url'] }}" class="link-pdf" target="_blank">📄 Ver en Drive</a>
                            {% else %}
                                <span style="color: #bdc1c6;">No disponible</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(diseño, documentos=documentos)

@app.route('/descargar_excel')
def descargar_excel():
    # 1. Conectamos a la base de datos
    conexion = conectar_db()
    
    # 2. Usamos la MISMA consulta SQL que en la web para que los datos coincidan
    consulta = """
    SELECT 
        d.id AS numero_documento,
        d.id_referencia AS numero_referencia,
        e.nombre AS empresa,
        c.nombre AS cliente,
        d.tipo,
        d.total
    FROM documentos d
    JOIN empresas e ON d.empresa_id = e.id
    JOIN clientes c ON d.cliente_id = c.id;
    """
    
    # 3. PANDAS hace el trabajo sucio: Lee el SQL y lo convierte en una tabla (DataFrame)
    df = pd.read_sql_query(consulta, conexion)
    conexion.close()
    
    # 4. Creamos un archivo Excel en la memoria RAM (no en el disco)
    salida_memoria = io.BytesIO()
    
    # 5. Escribimos los datos en el formato Excel
    with pd.ExcelWriter(salida_memoria, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte_Documentos')
    
    # 6. Volvemos al inicio del archivo en memoria para poder enviarlo
    salida_memoria.seek(0)
    
    # 7. Enviamos el archivo al navegador del compañero que hizo clic
    return send_file(
        salida_memoria, 
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True, 
        download_name="Reporte_Empresa.xlsx"
    )



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)