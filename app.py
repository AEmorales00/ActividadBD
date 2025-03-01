from flask import Flask, request, redirect, url_for, flash, render_template
import pandas as pd
import os
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración de la carpeta de subidas
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de la base de datos
DATABASE_URI = 'mysql+pymysql://root:@localhost/actividadbd'  # Usuario: root, sin contraseña
engine = create_engine(DATABASE_URI)

# Asegúrate de que la carpeta de subidas exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica si se ha subido un archivo
        if 'archivo' not in request.files:
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)
        
        archivo = request.files['archivo']
        
        # Verifica si el archivo tiene un nombre
        if archivo.filename == '':
            flash('No se ha seleccionado ningún archivo', 'error')
            return redirect(request.url)
        
        # Guarda el archivo temporalmente
        if archivo and archivo.filename.endswith('.xlsx'):
            ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
            archivo.save(ruta_archivo)
            
            try:
                # Lee el archivo Excel
                datos = pd.read_excel(ruta_archivo)
                
                # Carga los datos en la base de datos
                datos.to_sql('datos_excel', con=engine, if_exists='append', index=False)
                
                flash('Archivo subido y datos cargados en la base de datos', 'success')
            except Exception as e:
                flash(f'Error al procesar el archivo: {str(e)}', 'error')
            finally:
                # Elimina el archivo temporal
                os.remove(ruta_archivo)
        else:
            flash('Formato de archivo no válido. Solo se permiten archivos .xlsx', 'error')
        
        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)