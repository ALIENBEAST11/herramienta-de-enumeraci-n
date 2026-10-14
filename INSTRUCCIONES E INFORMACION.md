# Herramientas de Reconocimiento y Auditoría Web

Este proyecto reúne dos herramientas desarrolladas en Python para realizar tareas básicas de reconocimiento de dominios y auditoría de seguridad web. Ambas cuentan con una versión de terminal (CLI) y otra con interfaz gráfica (GUI).

Los resultados se pueden consultar desde la propia herramienta y exportar a informes para facilitar su análisis posterior.

## 🚀 Funcionalidades

### 1. Enumeración y reconocimiento

Archivos: `enumeracion_cli.py` y `enumeracion_gui.py`

La herramienta permite recopilar información sobre un dominio y detectar posibles puntos de interés durante las primeras fases de una auditoría.

**Recopilación pasiva**

- Consulta de información WHOIS del dominio.
- Resolución de registros DNS: A, AAAA, MX, NS, TXT, SOA y CNAME.
- Consulta de certificados SSL/TLS históricos mediante la API pública de [crt.sh](https://crt.sh/).

**Reconocimiento activo**

- Obtención de cabeceras HTTP para identificar información del servidor.
- Análisis de los datos del certificado SSL/TLS del puerto 443.
- Escaneo de puertos habituales y captura de banners.
- Comprobación de servicios de bases de datos expuestos, como MySQL, PostgreSQL, MSSQL y MongoDB.
- Búsqueda de directorios web mediante diccionarios de rutas.

**Exportación de resultados**

Al terminar el análisis, se pueden generar informes en HTML y JSON. El HTML permite revisar los resultados de forma visual, mientras que el JSON facilita su procesamiento con otras herramientas.

### 2. Auditoría de cabeceras y servidor HTTP

Archivos: `cabeceras_servidor_cli.py` y `cabeceras_servidor_gui.py`

Esta herramienta está orientada a revisar la configuración de seguridad HTTP y comprobar las peticiones recibidas por un servidor local.

**Auditoría de cabeceras**

- Comprobación de cabeceras de seguridad como:
  - `Strict-Transport-Security` (HSTS).
  - `Content-Security-Policy` (CSP).
  - `X-Frame-Options`.
  - `X-Content-Type-Options`.
  - `Referrer-Policy`.
- Identificación de cabeceras ausentes en la respuesta del servidor.

**Servidor HTTP local**

- Inicio de un servidor HTTP multihilo para recibir peticiones.
- Captura de las cabeceras `User-Agent` enviadas por los clientes.
- Visualización de información sobre las peticiones recibidas.
- Generación de un informe HTML con los resultados de la auditoría y los agentes detectados.

## ⚙️ Instalación

Las herramientas están pensadas principalmente para Linux y Kali Linux.

### 1. Instalar los paquetes necesarios

```bash
sudo apt update
sudo apt install -y whois python3-tk python3-dnspython
```

Para utilizar el fuzzing de directorios, también se puede instalar DIRB y sus diccionarios:

```bash
sudo apt install -y dirb
```

### 2. Instalar las dependencias de Python

Clona el repositorio y accede a su directorio:

```bash
git clone https://github.com/ALIENBEAST11/herramienta-de-enumeraci-n
cd herramienta-de-enumeraci-n
```

Instala las dependencias indicadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

Si el sistema utiliza un entorno Python administrado por el sistema, es recomendable crear un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si no existe un archivo `requirements.txt`, las dependencias indicadas para la instalación manual son:

```bash
pip install requests dnspython colorama
```

## 🕹️ Uso

### Herramienta 1: Enumeración y reconocimiento

#### Versión CLI

Ejecuta el siguiente comando:

```bash
python enumeracion_cli.py
```

Una vez iniciada la herramienta:

1. Introduce el dominio que quieres analizar, por ejemplo, `scanme.nmap.org`.
2. Selecciona el tipo de análisis: pasivo, activo o completo.
3. Espera a que terminen las comprobaciones.
4. Revisa los resultados obtenidos y los informes generados.

#### Versión GUI

Inicia la interfaz gráfica con:

```bash
python enumeracion_gui.py
```

Desde la ventana principal puedes:

1. Introducir el dominio objetivo.
2. Seleccionar el diccionario que se utilizará durante la búsqueda de directorios.
3. Activar o desactivar los módulos de análisis disponibles.
4. Pulsar **Iniciar** para comenzar el reconocimiento.
5. Consultar los resultados y exportarlos en los formatos disponibles.

### Herramienta 2: Cabeceras de seguridad y servidor HTTP

#### Versión CLI

Ejecuta:

```bash
python cabeceras_servidor_cli.py
```

Introduce la URL que deseas auditar y configura el puerto local de escucha. El puerto predeterminado es `8080`.

Para comprobar el funcionamiento del servidor, abre otra terminal y ejecuta:

```bash
curl -A "MiNavegadorDePrueba/1.0" http://localhost:8080/clase
```

La petición aparecerá en el servidor con el `User-Agent` utilizado.

Cuando hayas terminado, pulsa `Ctrl + C` para detener el servidor y generar el informe, si así lo contempla la implementación.

#### Versión GUI

Inicia la interfaz gráfica:

```bash
python cabeceras_servidor_gui.py
```

La ventana permite trabajar con las dos funciones principales:

- **Auditoría web:** introduce una URL para comprobar las cabeceras de seguridad.
- **Servidor HTTP local:** inicia el servidor, realiza peticiones de prueba y consulta las conexiones recibidas junto con sus respectivos `User-Agent`.

Los resultados se pueden consultar desde la interfaz y exportar a un informe HTML.

## 📂 Informes generados

Los informes permiten guardar los resultados de cada ejecución para revisarlos más adelante o incorporarlos a la documentación de una auditoría.

| Formato | Uso                                                         |
| ------- | ----------------------------------------------------------- |
| HTML    | Consulta visual de los resultados.                          |
| JSON    | Almacenamiento estructurado para su análisis posterior.     |
| TXT     | Exportación de resultados en texto, cuando está disponible. |

Los formatos concretos y la ubicación de los archivos dependen de la herramienta y de su implementación.

