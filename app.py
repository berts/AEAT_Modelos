import os
import configparser
from flask import Flask, request, jsonify, render_template_string, send_from_directory

app = Flask(__name__)

# ========================================================
# Carga de la configuración desde config.ini
# ========================================================
config = configparser.ConfigParser()
config.read('config.ini')

try:
    UPLOAD_FOLDER = config.get('GENERAL', 'UPLOAD_FOLDER')
except Exception as e:
    print("Error leyendo UPLOAD_FOLDER desde config.ini. Se usará './uploads' por defecto.")
    UPLOAD_FOLDER = './uploads'

MODELOS = {}
if 'MODELOS' in config:
    for key in config['MODELOS']:
        MODELOS[key.strip()] = config['MODELOS'][key].strip()

ESTRUCTURAS = {}
if 'ESTRUCTURAS' in config:
    for key in config['ESTRUCTURAS']:
        ESTRUCTURAS[key.strip()] = config['ESTRUCTURAS'][key].strip()

EXTENSION = {}
if 'EXTENSION' in config:
    for key in config['EXTENSION']:
        EXTENSION[key.strip()] = config['EXTENSION'][key].strip()

# ========================================================
# Función para extraer datos de una línea de archivo
# ========================================================
def parse_line(line, structure):
    result = {}
    fields = structure.split(',')
    for field in fields:
        field = field.strip()
        if not field:
            continue
        try:
            key, pos = field.split(':')
            start, end = pos.split('-')
            start = int(start)
            end = int(end)
            result[key.strip()] = line[start:end].strip()
        except Exception as e:
            print(f"Error al procesar el campo '{field}': {e}")
    return result

# ========================================================
# Ruta principal: interfaz web
# ========================================================
@app.route('/')
def index():
    # Se pasa la lista de modelos para llenar el desplegable
    return render_template_string('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Gestión de Modelos Fiscales</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.9.3/css/bulma.min.css">
</head>
<body>
<section class="section">
    <div class="container">
        <h1 class="title">Gestión de Modelos Fiscales</h1>
        
        <!-- Selección de modelo -->
        <div class="field">
            <label class="label">Selecciona un Modelo Fiscal</label>
            <div class="control">
                <div class="select">
                    <select id="modeloSelect">
                        <option value="">-- Selecciona un modelo --</option>
                        {% for key, valor in modelos.items() %}
                        <option value="{{ key }}">{{ key }} - {{ valor }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
        </div>
        
        <!-- Botón para renombrar el directorio completo -->
        <div class="field">
            <button id="renameAllBtn" class="button is-info" disabled>Renombrar Directorio</button>
        </div>

        <table class="table is-fullwidth is-striped">
            <thead>
                <tr>
                    <th>Archivo</th>
                    <th>CIF</th>
                    <th>Nombre</th>
                    <th>Ejercicio</th>
                    <th>Ruta</th>
                    <th>Procesado</th>
                </tr>
            </thead>
            <tbody id="fileTable">
            </tbody>
        </table>
    </div>
</section>

<script>
// Cuando se selecciona un modelo, se solicita la lista de archivos
const modeloSelect = document.getElementById('modeloSelect');
const renameAllBtn = document.getElementById('renameAllBtn');

modeloSelect.addEventListener('change', function() {
    const modelo = this.value;
    if (!modelo) {
        document.getElementById('fileTable').innerHTML = '';
        renameAllBtn.disabled = true;
        return;
    }
    // Habilitamos el botón de "Renombrar Directorio"
    renameAllBtn.disabled = false;
    
    fetch('/listar?modelo=' + modelo)
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById('fileTable');
            table.innerHTML = '';
            data.forEach(item => {
                const row = document.createElement('tr');
                
                // Columna: Nombre del archivo
                const nameCell = document.createElement('td');
                nameCell.textContent = item.nombre_archivo;
                row.appendChild(nameCell);
                
                // Columna: CIF
                const cifCell = document.createElement('td');
                cifCell.textContent = item.CIF;
                row.appendChild(cifCell);
                
                // Columna: Nombre (comunidad o empresa)
                const nombreCell = document.createElement('td');
                nombreCell.textContent = item.NOMBRE;
                row.appendChild(nombreCell);
                
                // Columna: Ejercicio fiscal
                const ejercicioCell = document.createElement('td');
                ejercicioCell.textContent = item.EJERCICIO;
                row.appendChild(ejercicioCell);
                
                // Columna: Ruta del archivo con enlace directo
                const rutaCell = document.createElement('td');
                const link = document.createElement('a');
                link.href = '/archivo/' + item.nombre_archivo;
                link.textContent = item.ruta;
                rutaCell.appendChild(link);
                row.appendChild(rutaCell);
                
                // Columna: Checkbox para marcar como procesado
                const procesadoCell = document.createElement('td');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                // Está procesado si empieza por 'procesado_'
                checkbox.checked = item.nombre_archivo.startsWith('procesado_');
                checkbox.addEventListener('change', function() {
                    fetch('/procesar', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({archivo: item.nombre_archivo, procesado: checkbox.checked})
                    })
                    .then(response => response.json())
                    .then(result => {
                        // Tras procesar, recargamos la lista
                        modeloSelect.dispatchEvent(new Event('change'));
                    });
                });
                procesadoCell.appendChild(checkbox);
                row.appendChild(procesadoCell);
                
                table.appendChild(row);
            });
        });
});

// Evento para renombrar todos los archivos del modelo seleccionado
renameAllBtn.addEventListener('click', function() {
    const modelo = modeloSelect.value;
    if (!modelo) return;
    if (!confirm('¿Estás seguro de renombrar todos los archivos del modelo ' + modelo + '?')) {
        return;
    }
    fetch('/renombrar_directorio', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({modelo: modelo})
    })
    .then(response => response.json())
    .then(result => {
        alert(result.mensaje);
        // Recargamos la lista para ver los nuevos nombres
        modeloSelect.dispatchEvent(new Event('change'));
    })
    .catch(err => {
        alert('Error al renombrar directorio: ' + err);
    });
});
</script>
</body>
</html>
    ''', modelos=MODELOS)

# ========================================================
# Ruta para listar archivos según el modelo seleccionado
# ========================================================
@app.route('/listar')
def listar():
    modelo = request.args.get('modelo')
    if not modelo or modelo not in MODELOS:
        return jsonify([])

    extension = EXTENSION.get(modelo, '')
    archivos = []

    for filename in os.listdir(UPLOAD_FOLDER):
        # 1. Filtramos solo por extensión
        if not filename.endswith(extension):
            continue

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 2. Leemos la primera línea
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline()
        except Exception as e:
            print(f"Error al leer el archivo {filename}: {e}")
            continue

        if not first_line:
            continue

        # 3. Extraemos el modelo de la línea
        # Ajusta el slice [1:4] (o el que corresponda)
        file_model = first_line[1:4].strip()

        if file_model != modelo:
            continue

        # 4. Parseamos la línea según config.ini
        structure = ESTRUCTURAS.get(modelo, '')
        datos = parse_line(first_line, structure) if structure else {}

        datos.setdefault('CIF', '')
        datos.setdefault('NOMBRE', '')
        datos.setdefault('EJERCICIO', '')

        datos['nombre_archivo'] = filename
        datos['ruta'] = os.path.abspath(filepath)
        archivos.append(datos)

    return jsonify(archivos)

# ========================================================
# Ruta para renombrar (procesar) todos los archivos del modelo
# ========================================================
@app.route('/renombrar_directorio', methods=['POST'])
def renombrar_directorio():
    """
    Renombra todos los archivos de un modelo a:
    M<modelo>_<CIF>_<NOMBRE>.<ext>
    (si no están ya procesados).
    """
    data = request.get_json()
    modelo = data.get('modelo')
    if not modelo or modelo not in MODELOS:
        return jsonify({"mensaje": "Modelo no válido"}), 400

    extension = EXTENSION.get(modelo, '')
    count = 0

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith('procesado_'):
            # Si ya está procesado, no lo renombramos
            continue
        if not filename.endswith(extension):
            continue

        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Leemos la primera línea
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline()
        except Exception as e:
            print(f"Error al leer {filename}: {e}")
            continue

        if not first_line:
            continue

        file_model = first_line[1:4].strip()
        if file_model != modelo:
            continue

        # Parseamos para obtener CIF y NOMBRE
        structure = ESTRUCTURAS.get(modelo, '')
        datos = parse_line(first_line, structure) if structure else {}
        cif = datos.get('CIF', '').replace(' ', '_')
        nombre = datos.get('NOMBRE', '').replace(' ', '_')

        # (Opcional) Elimina caracteres conflictivos para nombres de archivo
        # Por ejemplo, podrías hacer algo más robusto:
        # import re
        # cif = re.sub(r'[^A-Za-z0-9_-]+', '', cif)
        # nombre = re.sub(r'[^A-Za-z0-9_-]+', '', nombre)

        # Construimos el nuevo nombre: M<modelo>_<CIF>_<NOMBRE>.<ext>
        new_name = f"M-{modelo}_{cif}.{extension}"
        new_path = os.path.join(UPLOAD_FOLDER, new_name)

        # Evita choques de nombres (si ya existe un archivo igual)
        if os.path.exists(new_path):
            print(f"El archivo {new_name} ya existe. Saltando...")
            continue

        os.rename(filepath, new_path)
        count += 1

    return jsonify({"mensaje": f"Renombrados {count} archivos del modelo {modelo}."})

# ========================================================
# Ruta para marcar/desmarcar un archivo como procesado
# ========================================================
@app.route('/procesar', methods=['POST'])
def procesar():
    data = request.get_json()
    archivo = data.get('archivo')
    procesado = data.get('procesado')
    ruta_actual = os.path.join(UPLOAD_FOLDER, archivo)
    
    if not os.path.exists(ruta_actual):
        return jsonify({"error": "Archivo no encontrado"}), 404

    # Si se marca como procesado, añadimos prefijo 'procesado_'
    if procesado:
        if not archivo.startswith('procesado_'):
            nuevo_nombre = 'procesado_' + archivo
            ruta_nueva = os.path.join(UPLOAD_FOLDER, nuevo_nombre)
            os.rename(ruta_actual, ruta_nueva)
            archivo = nuevo_nombre
    else:
        # Si se desmarca, quitamos el prefijo 'procesado_'
        if archivo.startswith('procesado_'):
            nuevo_nombre = archivo[len('procesado_'):]
            ruta_nueva = os.path.join(UPLOAD_FOLDER, nuevo_nombre)
            os.rename(ruta_actual, ruta_nueva)
            archivo = nuevo_nombre

    return jsonify({"mensaje": "Actualización exitosa", "archivo": archivo})

# ========================================================
# Ruta para acceder a los archivos directamente
# ========================================================
@app.route('/archivo/<path:filename>')
def archivo(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ========================================================
# Ejecución de la aplicación Flask
# ========================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
