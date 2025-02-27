# AEAT Modelos

Este repositorio contiene una aplicación Flask para la gestión de modelos fiscales. La aplicación permite listar, procesar y renombrar archivos de modelos fiscales según una configuración definida en un archivo `config.ini`.

## Funcionalidades

- **Carga de configuración**: La aplicación carga la configuración desde un archivo `config.ini` que define las carpetas de subida, modelos, estructuras y extensiones de archivo.
- **Interfaz web**: Una interfaz web que permite seleccionar un modelo fiscal, listar los archivos correspondientes y renombrar los archivos según un formato específico.
- **Listar archivos**: La aplicación lista los archivos en la carpeta de subida que coinciden con el modelo seleccionado y extrae información relevante de cada archivo.
- **Renombrar archivos**: Permite renombrar todos los archivos de un modelo a un formato específico.
- **Marcar como procesado**: Permite marcar o desmarcar archivos como procesados, añadiendo o quitando el prefijo `procesado_`.
- **Acceso directo a archivos**: Permite acceder y descargar los archivos directamente desde la interfaz web.

## Configuración

El archivo `config.ini` debe tener la siguiente estructura:

```ini
[GENERAL]
UPLOAD_FOLDER = ./uploads

[MODELOS]
modelo1 = Descripción del modelo 1
modelo2 = Descripción del modelo 2

[ESTRUCTURAS]
modelo1 = CIF:0-9,NOMBRE:10-29,EJERCICIO:30-33
modelo2 = CIF:0-9,NOMBRE:10-29,EJERCICIO:30-33

[EXTENSION]
modelo1 = .txt
modelo2 = .csv
```

## Ejecución

Para ejecutar la aplicación, asegúrate de tener Flask instalado y ejecuta el script `app.py`:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`.

## Uso

1. **Seleccionar un modelo**: En la interfaz web, selecciona un modelo fiscal del desplegable.
2. **Listar archivos**: La lista de archivos correspondientes al modelo seleccionado se mostrará en una tabla.
3. **Renombrar directorio**: Haz clic en el botón "Renombrar Directorio" para renombrar todos los archivos del modelo seleccionado.
4. **Marcar como procesado**: Usa los checkboxes para marcar o desmarcar archivos como procesados.

## Notas

- Asegúrate de que la carpeta de subida (`UPLOAD_FOLDER`) existe y contiene los archivos a procesar.
- La estructura de los archivos debe coincidir con la definida en `config.ini` para que la extracción de datos funcione correctamente.
