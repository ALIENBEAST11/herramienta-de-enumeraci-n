import socket
import ssl
import os
import sys
import subprocess
import time
from datetime import datetime
import requests
import dns.resolver
from colorama import init, Fore, Style

# Inicializar colorama para soporte de colores en terminal
init(autoreset=True)

def banner_hacker():
    print(Fore.CYAN + Style.BRIGHT + """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║        [+] TACTICAL RECON & ENUMERATION SUITE v3.5                ║
    ║        [+] Módulos: Pasiva (WHOIS/DNS/CRT.SH) & Activa            ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)

def barra_progreso(actual, total, prefijo='Progreso', longitud=30):
    if total <= 0:
        total = 1
    porcentaje = min(float(actual) / float(total), 1.0)
    completado = int(round(longitud * porcentaje))
    barra = Fore.GREEN + '█' * completado + Fore.DARKGRAY + '-' * (longitud - completado) + Style.RESET_ALL
    sys.stdout.write(f'\r{Fore.YELLOW}{prefijo} [{barra}] {int(porcentaje * 100)}% ({actual}/{total}){Style.RESET_ALL}')
    sys.stdout.flush()
    if actual >= total:
        print()

def exportar_dashboard_html(dominio, ip_obj, datos_html):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = f"dashboard_enumeracion_{dominio.replace('.', '_')}.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Ciberseguridad - {dominio}</title>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --accent-green: #10b981;
            --accent-cyan: #06b6d4;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border-color: #1f2937;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #111827, #1f2937);
            border: 1px solid var(--border-color);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            color: var(--accent-cyan);
            font-size: 1.8rem;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .meta-card {{
            background: rgba(17, 24, 39, 0.7);
            border: 1px solid var(--border-color);
            padding: 12px 18px;
            border-radius: 8px;
        }}
        .meta-card span {{
            color: var(--text-muted);
            font-size: 0.85rem;
            display: block;
        }}
        .meta-card strong {{
            color: var(--text-main);
            font-size: 1rem;
        }}
        .section-title {{
            color: var(--accent-green);
            font-size: 1.3rem;
            margin: 30px 0 15px 0;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 8px;
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin-top: 0;
            color: #93c5fd;
            font-size: 1.1rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }}
        ul {{
            margin: 0;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 6px;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            word-break: break-all;
        }}
        .badge {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-green);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border-color);
            padding-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Dashboard de Reconocimiento y Enumeración</h1>
        <div class="meta-grid">
            <div class="meta-card">
                <span>Objetivo Analizado</span>
                <strong>{dominio}</strong>
            </div>
            <div class="meta-card">
                <span>Dirección IP</span>
                <strong>{ip_obj if ip_obj else 'No resuelta'}</strong>
            </div>
            <div class="meta-card">
                <span>Fecha del Informe</span>
                <strong>{timestamp}</strong>
            </div>
        </div>
    </div>

    <div class="section-title">🕵️ Fase Pasiva (OSINT & DNS)</div>
    <div class="card-grid">
        <div class="card">
            <h3>Registros DNS Principales</h3>
            <ul>"""
    for item in datos_html.get("dns", []):
        html_content += f"<li>{item}</li>"
    html_content += """</ul></div>
        <div class="card">
            <h3>Información WHOIS</h3>
            <ul>"""
    for item in datos_html.get("whois", []):
        html_content += f"<li>{item}</li>"
    html_content += """</ul></div>
        <div class="card">
            <h3>Transparencia de Certificados (crt.sh)</h3>
            <ul>"""
    for item in datos_html.get("crtsh", []):
        html_content += f"<li>{item}</li>"
    html_content += """</ul></div>
    </div>

    <div class="section-title">⚡ Fase Activa (Servicios y Red)</div>
    <div class="card-grid">
        <div class="card">
            <h3>Cabeceras HTTP & SSL</h3>
            <ul>"""
    for item in datos_html.get("activa", []):
        html_content += f"<li>{item}</li>"
    html_content += """</ul></div>
        <div class="card">
            <h3>Puertos Abiertos & Banners</h3>
            <ul>"""
    for item in datos_html.get("puertos", []):
        html_content += f"<li><span class='badge'>{item}</span></li>"
    html_content += """</ul></div>
        <div class="card">
            <h3>Bases de Datos & Fuzzing Web</h3>
            <ul>"""
    for item in datos_html.get("bbdd_fuzz", []):
        html_content += f"<li>{item}</li>"
    html_content += """</ul></div>
    </div>
    <div class="footer">Generado automáticamente por la herramienta táctica CLI.</div>
</body>
</html>"""

    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n{Fore.GREEN}[✔] ¡Dashboard HTML visual generado con éxito: {nombre_archivo}!{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[✖] Error al exportar el HTML: {e}{Style.RESET_ALL}")

datos_informe = {"dns": [], "whois": [], "crtsh": [], "activa": [], "puertos": [], "bbdd_fuzz": []}

def consultar_whois(dominio):
    print(f"\n{Fore.CYAN}┌── [ 🕵️ MÓDULO PASIVO: CONSULTA WHOIS ]{Style.RESET_ALL}")
    try:
        resultado = subprocess.run(["whois", dominio], capture_output=True, text=True, timeout=10)
        if resultado.returncode == 0:
            for linea in resultado.stdout.splitlines():
                if any(k in linea.lower() for k in ['registrar', 'creation date', 'name server', 'domain name', 'org']):
                    print(f"{Fore.GREEN}    ├── {linea}{Style.RESET_ALL}")
                    datos_informe["whois"].append(linea)
        else:
            print(f"{Fore.RED}    └── [-] No se pudo ejecutar whois.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}    └── [-] Error en whois: {e}{Style.RESET_ALL}")

def obtener_registros_dns(dominio):
    print(f"\n{Fore.CYAN}┌── [ 🕵️ MÓDULO PASIVO: REGISTROS DNS ]{Style.RESET_ALL}")
    tipos = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
    for i, tipo in enumerate(tipos, 1):
        barra_progreso(i, len(tipos), prefijo="[DNS Query]")
        try:
            respuestas = dns.resolver.resolve(dominio, tipo)
            for rdata in respuestas:
                txt = f"{tipo}: {rdata.to_text()}"
                print(f"{Fore.GREEN}    ├── {txt}{Style.RESET_ALL}")
                datos_informe["dns"].append(txt)
        except Exception:
            pass

def consultar_crtsh(dominio):
    print(f"\n{Fore.CYAN}┌── [ 🕵️ MÓDULO PASIVO: CRT.SH ]{Style.RESET_ALL}")
    url = f"https://crt.sh/?q={dominio}&output=json"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            datos = res.json()
            msg = f"Certificados históricos: {len(datos)}"
            print(f"{Fore.GREEN}    ├── {msg}{Style.RESET_ALL}")
            datos_informe["crtsh"].append(msg)
            dominios_crt = set()
            for reg in datos:
                for n in reg.get('name_value', '').split('\n'):
                    dominios_crt.add(n.strip())
            for d in sorted(list(dominios_crt))[:5]:
                print(f"{Fore.YELLOW}    ├── Host: {d}{Style.RESET_ALL}")
                datos_informe["crtsh"].append(f"Host: {d}")
    except Exception as e:
        print(f"{Fore.RED}    └── [-] Error en crt.sh: {e}{Style.RESET_ALL}")

def obtener_cabeceras_http(dominio):
    print(f"\n{Fore.MAGENTA}┌── [ ⚡ MÓDULO ACTIVO: CABECERAS HTTP ]{Style.RESET_ALL}")
    try:
        res = requests.get(f"http://{dominio}", timeout=5)
        print(f"{Fore.GREEN}    ├── Estado HTTP: {res.status_code}{Style.RESET_ALL}")
        for h in ['Server', 'X-Powered-By', 'Date', 'Content-Type']:
            if h in res.headers:
                txt = f"{h}: {res.headers[h]}"
                print(f"{Fore.YELLOW}    ├── {txt}{Style.RESET_ALL}")
                datos_informe["activa"].append(txt)
    except Exception as e:
        print(f"{Fore.RED}    └── [-] Error HTTP: {e}{Style.RESET_ALL}")

def obtener_info_certificado(dominio):
    print(f"\n{Fore.MAGENTA}┌── [ ⚡ MÓDULO ACTIVO: CERTIFICADO SSL/TLS ]{Style.RESET_ALL}")
    contexto = ssl.create_default_context()
    try:
        with socket.create_connection((dominio, 443), timeout=5) as sock:
            with contexto.wrap_socket(sock, server_hostname=dominio) as ssock:
                cert = ssock.getpeercert()
                sujeto = dict(x[0] for x in cert.get('subject', []))
                cn = sujeto.get('commonName', 'N/A')
                txt = f"SSL CN: {cn}"
                print(f"{Fore.GREEN}    ├── {txt}{Style.RESET_ALL}")
                datos_informe["activa"].append(txt)
    except Exception as e:
        print(f"{Fore.RED}    └── [-] Error SSL: {e}{Style.RESET_ALL}")

def escaneo_puertos_y_banners(ip, puertos):
    print(f"\n{Fore.MAGENTA}┌── [ ⚡ MÓDULO ACTIVO: ESCANEO DE PUERTOS ]{Style.RESET_ALL}")
    for i, puerto in enumerate(puertos, 1):
        barra_progreso(i, len(puertos), prefijo="[Port Scan]")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        if sock.connect_ex((ip, puerto)) == 0:
            txt = f"Puerto {puerto}/tcp ABIERTO"
            print(f"{Fore.GREEN}    ├── [✔] {txt}{Style.RESET_ALL}")
            datos_informe["puertos"].append(txt)
        sock.close()

def detectar_bases_de_datos(ip):
    print(f"\n{Fore.MAGENTA}┌── [ ⚡ MÓDULO ACTIVO: BASES DE DATOS ]{Style.RESET_ALL}")
    puertos_bd = {3306: "MySQL", 5432: "PostgreSQL", 1433: "MSSQL", 27017: "MongoDB"}
    for puerto, motor in puertos_bd.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        if sock.connect_ex((ip, puerto)) == 0:
            txt = f"{motor} (Puerto {puerto})"
            print(f"{Fore.GREEN}    ├── [✔] Detectado: {txt}{Style.RESET_ALL}")
            datos_informe["bbdd_fuzz"].append(f"BD: {txt}")
        sock.close()

def descubrir_directorios(dominio):
    print(f"\n{Fore.MAGENTA}┌── [ ⚡ MÓDULO ACTIVO: FUZZING WEB ]{Style.RESET_ALL}")
    rutas = ["/usr/share/wordlists/dirb/common.txt", "/usr/share/wordlist/dirb/common.txt"]
    wordlist = next((r for r in rutas if os.path.exists(r)), None)
    if not wordlist:
        print(f"{Fore.RED}    └── [-] No se encontró 'common.txt'.{Style.RESET_ALL}")
        return

    with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
        lineas = [l.strip() for l in f if l.strip() and not l.startswith("#")][:30]

    base_url = f"http://{dominio}"
    total = len(lineas)
    for i, directorio in enumerate(lineas, 1):
        barra_progreso(i, total, prefijo="[Dir Fuzzing]")
        try:
            res = requests.get(f"{base_url}/{directorio}", timeout=2, allow_redirects=False)
            if res.status_code in [200, 301, 302, 403]:
                print(f"{Fore.GREEN}    ├── [✔] Ruta: /{directorio} (HTTP {res.status_code}){Style.RESET_ALL}")
                datos_informe["bbdd_fuzz"].append(f"Ruta: /{directorio} ({res.status_code})")
        except requests.RequestException:
            pass

if __name__ == "__main__":
    banner_hacker()
    objetivo = input(f"{Fore.YELLOW}[*] Introduce el dominio a analizar: {Style.RESET_ALL}").strip()
    objetivo = objetivo.replace("https://", "").replace("http://", "").split("/")[0]

    print(f"\n{Fore.CYAN}Selecciona el modo de enumeración:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}1){Style.RESET_ALL} Solo Enumeración PASIVA")
    print(f"  {Fore.GREEN}2){Style.RESET_ALL} Solo Enumeración ACTIVA")
    print(f"  {Fore.GREEN}3){Style.RESET_ALL} Enumeración COMPLETA (Pasiva + Activa)")
    opcion = input(f"{Fore.YELLOW}Opción [1/2/3]: {Style.RESET_ALL}").strip()

    ip_objetivo = None
    try:
        ip_objetivo = socket.gethostbyname(objetivo)
    except Exception:
        pass

    if opcion in ["1", "3"]:
        consultar_whois(objetivo)
        obtener_registros_dns(objetivo)
        consultar_crtsh(objetivo)

    if opcion in ["2", "3"]:
        if ip_objetivo:
            obtener_cabeceras_http(objetivo)
            obtener_info_certificado(objetivo)
            escaneo_puertos_y_banners(ip_objetivo, [21, 22, 25, 80, 443, 8080])
            detectar_bases_de_datos(ip_objetivo)
            descubrir_directorios(objetivo)
        else:
            print(f"{Fore.RED}[✖] No se pudo resolver la IP.{Style.RESET_ALL}")

    exportar_dashboard_html(objetivo, ip_objetivo, datos_informe)
