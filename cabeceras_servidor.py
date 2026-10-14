import threading
import requests
import sys
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from colorama import init, Fore, Style

init(autoreset=True)

def banner_hacker():
    print(Fore.CYAN + Style.BRIGHT + """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║        [+] SECURITY HEADERS AUDITOR & USER-AGENT SNIFFER          ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)

class ManejadorCapturaHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        user_agent = self.headers.get("User-Agent", "No especificado / Desconocido")
        ip_cliente, puerto_cliente = self.client_address
        fecha_hora = datetime.now().strftime("%H:%M:%S")

        print(f"\n{Fore.YELLOW}[!] Petición GET interceptada [{fecha_hora}]{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    ├── Cliente:    {ip_cliente}:{puerto_cliente}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    ├── Ruta:       {self.path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}    └── User-Agent: {user_agent}{Style.RESET_ALL}")

        if hasattr(self.server, "peticiones_capturadas"):
            self.server.peticiones_capturadas.append({
                "hora": fecha_hora,
                "ip": f"{ip_cliente}:{puerto_cliente}",
                "ruta": self.path,
                "user_agent": user_agent
            })

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><body style='background:#0b0f19;color:#fff;'><h2>Servidor activo - Peticion registrada</h2></body></html>")

    def log_message(self, format, *args):
        return

class ServidorHTTPReutilizable(ThreadingHTTPServer):
    allow_reuse_address = True

def barra_progreso(actual, total, prefijo='Progreso', longitud=30):
    if total <= 0:
        total = 1
    porcentaje = min(float(actual) / float(total), 1.0)
    completado = int(round(longitud * porcentaje))
    # Corrección aplicada aquí usando LIGHTBLACK_EX en lugar de DARKGRAY
    barra = Fore.GREEN + '█' * completado + Fore.LIGHTBLACK_EX + '-' * (longitud - completado) + Style.RESET_ALL
    sys.stdout.write(f'\r{Fore.YELLOW}{prefijo} [{barra}] {int(porcentaje * 100)}% ({actual}/{total}){Style.RESET_ALL}')
    sys.stdout.flush()
    if actual >= total:
        print()

def exportar_dashboard_html(sitio, datos_auditoria, peticiones_capturadas):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = f"dashboard_cabeceras_{sitio.replace('.', '_')}.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Cabeceras & User-Agents - {sitio}</title>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --accent-green: #10b981;
            --accent-cyan: #06b6d4;
            --accent-red: #ef4444;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border-color: #1f2937;
        }}
        body {{ background-color: var(--bg-color); color: var(--text-main); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #111827, #1f2937); border: 1px solid var(--border-color); padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
        .header h1 {{ margin: 0 0 10px 0; color: var(--accent-cyan); font-size: 1.8rem; }}
        .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-top: 15px; }}
        .meta-card {{ background: rgba(17, 24, 39, 0.7); border: 1px solid var(--border-color); padding: 12px 18px; border-radius: 8px; }}
        .meta-card span {{ color: var(--text-muted); font-size: 0.85rem; display: block; }}
        .meta-card strong {{ color: var(--text-main); font-size: 1rem; }}
        .section-title {{ color: var(--accent-green); font-size: 1.3rem; margin: 30px 0 15px 0; border-bottom: 2px solid var(--border-color); padding-bottom: 8px; }}
        .card {{ background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .card h3 {{ margin-top: 0; color: #93c5fd; font-size: 1.1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }}
        ul {{ margin: 0; padding-left: 20px; }}
        li {{ margin-bottom: 8px; font-family: 'Consolas', monospace; font-size: 0.9rem; word-break: break-all; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
        .badge-green {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); }}
        .badge-red {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; background: var(--card-bg); border-radius: 8px; overflow: hidden; border: 1px solid var(--border-color); }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }}
        th {{ background: #1f2937; color: var(--accent-cyan); }}
        .footer {{ text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 0.85rem; border-top: 1px solid var(--border-color); padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Dashboard de Seguridad Web & User-Agents</h1>
        <div class="meta-grid">
            <div class="meta-card"><span>Sitio Auditado</span><strong>{sitio}</strong></div>
            <div class="meta-card"><span>Fecha del Informe</span><strong>{timestamp}</strong></div>
            <div class="meta-card"><span>Peticiones Capturadas</span><strong>{len(peticiones_capturadas)} clientes</strong></div>
        </div>
    </div>
    <div class="section-title">🔍 1. Auditoría de Cabeceras de Seguridad</div>
    <div class="card">
        <h3>Estado de Cabeceras HTTP</h3>
        <ul>"""
    
    if datos_auditoria:
        for item in datos_auditoria:
            estado_clase = "badge-green" if item['estado'] == "PRESENTE" else "badge-red"
            html_content += f"<li><span class='badge {estado_clase}'>{item['estado']}</span> <strong>{item['cabecera']}</strong>: {item['valor']}</li>"
    else:
        html_content += "<li>No se auditó ninguna cabecera.</li>"

    html_content += """</ul></div>
    <div class="section-title">⚡ 2. Servidor HTTP (User-Agents Interceptados)</div>"""
    
    if peticiones_capturadas:
        html_content += """<table><thead><tr><th>Hora</th><th>Cliente IP:Puerto</th><th>Ruta</th><th>User-Agent Detectado</th></tr></thead><tbody>"""
        for pet in peticiones_capturadas:
            html_content += f"<tr><td>{pet['hora']}</td><td>{pet['ip']}</td><td>{pet['ruta']}</td><td style='font-family:monospace;color:#10b981;'>{pet['user_agent']}</td></tr>"
        html_content += """</tbody></table>"""
    else:
        html_content += "<p style='color:var(--text-muted);'>No se interceptaron peticiones.</p>"

    html_content += """<div class="footer">Generado automáticamente por el script CLI.</div></body></html>"""

    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n{Fore.GREEN}[✔] Dashboard HTML de cabeceras guardado: {nombre_archivo}{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[✖] Error al exportar HTML: {e}{Style.RESET_ALL}")

def analizar_cabeceras(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"\n{Fore.CYAN}┌── [ ANALIZANDO CABECERAS DE SEGURIDAD EN: {url} ]{Style.RESET_ALL}")
    cabeceras_seguridad = {
        "Strict-Transport-Security": "Fuerza conexiones HTTPS (HSTS).",
        "Content-Security-Policy": "Mitiga ataques XSS (CSP).",
        "X-Frame-Options": "Previene Clickjacking.",
        "X-Content-Type-Options": "Bloquea MIME-sniffing.",
        "Referrer-Policy": "Controla cabecera Referer.",
        "Permissions-Policy": "Restringe APIs del navegador.",
        "X-XSS-Protection": "Filtro XSS."
    }

    datos_auditoria = []
    total = len(cabeceras_seguridad)
    try:
        headers_peticion = {"User-Agent": "Mozilla/5.0 (Security-Auditor-CLI/1.0)"}
        res = requests.get(url, headers=headers_peticion, timeout=8)
        print(f"{Fore.GREEN}    ├── Conexión exitosa (Estado HTTP: {res.status_code}){Style.RESET_ALL}")

        for i, (cabecera, desc) in enumerate(cabeceras_seguridad.items(), 1):
            barra_progreso(i, total, prefijo="[Auditoría]")
            valor = res.headers.get(cabecera)
            if valor:
                print(f"{Fore.GREEN}    ├── [PRESENTE] {cabecera}: {valor}{Style.RESET_ALL}")
                datos_auditoria.append({"cabecera": cabecera, "estado": "PRESENTE", "valor": valor})
            else:
                print(f"{Fore.RED}    ├── [AUSENTE]  {cabecera} ({desc}){Style.RESET_ALL}")
                datos_auditoria.append({"cabecera": cabecera, "estado": "AUSENTE", "valor": desc})
        return datos_auditoria
    except Exception as e:
        print(f"{Fore.RED}    └── [!] Error al conectar: {e}{Style.RESET_ALL}")
        return []

if __name__ == "__main__":
    banner_hacker()
    url_objetivo = input(f"{Fore.YELLOW}[*] Introduce la URL a auditar (ej. wikipedia.org): {Style.RESET_ALL}").strip()
    datos_aud = []
    if url_objetivo:
        datos_aud = analizar_cabeceras(url_objetivo)

    puerto = input(f"\n{Fore.YELLOW}[*] Introduce el puerto para el servidor HTTP [por defecto 8080]: {Style.RESET_ALL}").strip()
    puerto = int(puerto) if puerto.isdigit() else 8080

    servidor = ServidorHTTPReutilizable(("0.0.0.0", puerto), ManejadorCapturaHTTP)
    servidor.peticiones_capturadas = []

    hilo_srv = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo_srv.start()

    print(f"\n{Fore.GREEN}[✔] Servidor HTTP activo en http://localhost:{puerto}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Abre tu navegador o usa 'curl' para enviar peticiones.")
    print(f"{Fore.YELLOW}[*] Presiona Ctrl+C para detener y exportar el Dashboard HTML.{Style.RESET_ALL}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Deteniendo servidor y exportando informe visual...{Style.RESET_ALL}")
        servidor.shutdown()
        servidor.server_close()
        exportar_dashboard_html(url_objetivo if url_objetivo else "local", datos_aud, servidor.peticiones_capturadas)
