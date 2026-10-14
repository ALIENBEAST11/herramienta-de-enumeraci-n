import socket
import ssl
import os
import subprocess
import threading
from datetime import datetime
import requests
import dns.resolver
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox


class AplicacionEnumeracionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Herramienta de Enumeración - Pasiva & Activa (Dashboard HTML)")
        self.root.geometry("940x780")
        self.root.minsize(840, 680)

        self.ejecutando = False
        self.datos_informe = {}  # Diccionario para almacenar resultados estructurados

        # --- Marco Superior: Configuración del Objetivo ---
        frame_config = ttk.LabelFrame(root, text=" Configuración del Objetivo ", padding=10)
        frame_config.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_config, text="Dominio / Host:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_dominio = ttk.Entry(frame_config, width=35)
        self.entry_dominio.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.entry_dominio.insert(0, "scanme.nmap.org")

        ttk.Label(frame_config, text="Wordlist Dirb:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_wordlist = ttk.Entry(frame_config, width=55)
        self.entry_wordlist.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.entry_wordlist.insert(0, self.localizar_wordlist_defecto())

        btn_explorar = ttk.Button(frame_config, text="Explorar...", command=self.seleccionar_wordlist)
        btn_explorar.grid(row=1, column=2, padx=5, pady=5)

        # --- Contenedor de Fases (Pasiva y Activa) ---
        frame_fases = ttk.Frame(root)
        frame_fases.pack(fill="x", padx=10, pady=5)

        # Panel Izquierdo: Recopilación Pasiva
        frame_pasiva = ttk.LabelFrame(frame_fases, text=" 🕵️ Recopilación Pasiva (OSINT / DNS) ", padding=10)
        frame_pasiva.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.var_whois = tk.BooleanVar(value=True)
        self.var_dns = tk.BooleanVar(value=True)
        self.var_crtsh = tk.BooleanVar(value=True)

        ttk.Checkbutton(frame_pasiva, text="Consulta WHOIS", variable=self.var_whois).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame_pasiva, text="Registros DNS (A, MX, TXT...)", variable=self.var_dns).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame_pasiva, text="crt.sh (Certificados)", variable=self.var_crtsh).grid(row=2, column=0, sticky="w", padx=5, pady=2)

        btn_solo_pasiva = ttk.Button(frame_pasiva, text="✔ Marcar Solo Pasiva", command=self.seleccionar_solo_pasiva)
        btn_solo_pasiva.grid(row=3, column=0, sticky="w", padx=5, pady=(8, 0))

        # Panel Derecho: Recopilación Activa
        frame_activa = ttk.LabelFrame(frame_fases, text=" ⚡ Recopilación Activa (Interacción Directa) ", padding=10)
        frame_activa.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.var_http = tk.BooleanVar(value=True)
        self.var_ssl = tk.BooleanVar(value=True)
        self.var_puertos = tk.BooleanVar(value=True)
        self.var_bbdd = tk.BooleanVar(value=True)
        self.var_subdominios = tk.BooleanVar(value=True)
        self.var_directorios = tk.BooleanVar(value=True)

        ttk.Checkbutton(frame_activa, text="Cabeceras HTTP", variable=self.var_http).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame_activa, text="Certificado SSL (443)", variable=self.var_ssl).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame_activa, text="Puertos y Banners", variable=self.var_puertos).grid(row=0, column=2, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame_activa, text="Bases de Datos", variable=self.var_bbdd).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame_activa, text="Subdominios", variable=self.var_subdominios).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(frame_activa, text="Fuzzing Web", variable=self.var_directorios).grid(row=1, column=2, sticky="w", padx=5, pady=2)

        frame_btns_activa = ttk.Frame(frame_activa)
        frame_btns_activa.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Button(frame_btns_activa, text="✔ Marcar Solo Activa", command=self.seleccionar_solo_activa).pack(side="left", padx=2)
        ttk.Button(frame_btns_activa, text="★ Marcar Todo", command=self.seleccionar_todo).pack(side="left", padx=2)

        # --- Barra de Progreso ---
        frame_progreso = ttk.LabelFrame(root, text=" Progreso del Escaneo ", padding=8)
        frame_progreso.pack(fill="x", padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(frame_progreso, orient="horizontal", mode="determinate", length=100)
        self.progress_bar.pack(fill="x", padx=5, pady=2)

        # --- Botones de Control ---
        frame_botones = ttk.Frame(root, padding=5)
        frame_botones.pack(fill="x", padx=10)

        self.btn_iniciar = ttk.Button(frame_botones, text="▶ Iniciar", command=self.iniciar_hilo_analisis)
        self.btn_iniciar.pack(side="left", padx=3)
        self.btn_detener = ttk.Button(frame_botones, text="⏹ Detener", command=self.detener_analisis, state="disabled")
        self.btn_detener.pack(side="left", padx=3)

        btn_html = ttk.Button(frame_botones, text="🌐 Exportar Dashboard HTML (Visual)", command=self.guardar_html_dashboard)
        btn_html.pack(side="right", padx=3)
        btn_guardar = ttk.Button(frame_botones, text="💾 Guardar TXT", command=self.guardar_resultados_txt)
        btn_guardar.pack(side="right", padx=3)
        btn_limpiar = ttk.Button(frame_botones, text="🗑 Limpiar", command=self.limpiar_consola)
        btn_limpiar.pack(side="right", padx=3)

        self.lbl_estado = ttk.Label(frame_botones, text="Estado: Listo", foreground="green")
        self.lbl_estado.pack(side="left", padx=15)

        # --- Consola ---
        frame_consola = ttk.LabelFrame(root, text=" Consola de Resultados ", padding=5)
        frame_consola.pack(fill="both", expand=True, padx=10, pady=5)

        self.consola = scrolledtext.ScrolledText(
            frame_consola, wrap=tk.WORD, bg="#050505", fg="#00ff66", font=("Consolas", 10)
        )
        self.consola.pack(fill="both", expand=True)

        self.consola.tag_config("fase", foreground="#00ffff", font=("Consolas", 10, "bold"))
        self.consola.tag_config("exito", foreground="#4ec9b0")
        self.consola.tag_config("error", foreground="#ff3333")
        self.consola.tag_config("detalle", foreground="#ce9178")

    def seleccionar_solo_pasiva(self):
        self.var_whois.set(True)
        self.var_dns.set(True)
        self.var_crtsh.set(True)
        for v in [self.var_http, self.var_ssl, self.var_puertos, self.var_bbdd, self.var_subdominios, self.var_directorios]:
            v.set(False)

    def seleccionar_solo_activa(self):
        self.var_whois.set(False)
        self.var_dns.set(False)
        self.var_crtsh.set(False)
        for v in [self.var_http, self.var_ssl, self.var_puertos, self.var_bbdd, self.var_subdominios, self.var_directorios]:
            v.set(True)

    def seleccionar_todo(self):
        for v in [self.var_whois, self.var_dns, self.var_crtsh, self.var_http, self.var_ssl, self.var_puertos, self.var_bbdd, self.var_subdominios, self.var_directorios]:
            v.set(True)

    def localizar_wordlist_defecto(self):
        for r in ["/usr/share/wordlists/dirb/common.txt", "/usr/share/wordlist/dirb/common.txt"]:
            if os.path.exists(r):
                return r
        return "/usr/share/wordlists/dirb/common.txt"

    def seleccionar_wordlist(self):
        archivo = filedialog.askopenfilename(initialdir="/usr/share", filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if archivo:
            self.entry_wordlist.delete(0, tk.END)
            self.entry_wordlist.insert(0, archivo)

    def escribir_log(self, texto, etiqueta=None):
        self.consola.insert(tk.END, texto + "\n", etiqueta)
        self.consola.see(tk.END)

    def limpiar_consola(self):
        self.consola.delete(1.0, tk.END)
        self.progress_bar['value'] = 0
        self.datos_informe = {}

    def detener_analisis(self):
        if self.ejecutando:
            self.ejecutando = False
            self.lbl_estado.config(text="Estado: Deteniendo...", foreground="orange")
            self.escribir_log("\n[!] Solicitud de parada recibida...", "error")

    def guardar_resultados_txt(self):
        contenido = self.consola.get(1.0, tk.END).strip()
        if not contenido:
            messagebox.showwarning("Consola vacía", "No hay resultados para guardar.")
            return
        dominio = self.entry_dominio.get().strip().replace("https://", "").replace("http://", "").split("/")[0] or "objetivo"
        ruta = filedialog.asksaveasfilename(
            initialfile=f"reporte_{dominio}.txt", defaultextension=".txt", filetypes=[("Text files", "*.txt")]
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido + "\n")
                messagebox.showinfo("Éxito", f"Guardado en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def guardar_html_dashboard(self):
        if not self.datos_informe:
            messagebox.showwarning("Sin datos", "Ejecuta primero un escaneo para generar el dashboard visual.")
            return

        dominio = self.datos_informe.get("dominio", "objetivo")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nombre_sugerido = f"dashboard_hacker_{dominio.replace('.', '_')}.html"

        ruta = filedialog.asksaveasfilename(
            initialfile=nombre_sugerido, defaultextension=".html", filetypes=[("Archivos HTML", "*.html"), ("Todos", "*.*")]
        )

        if not ruta:
            return

        # Generar HTML visual e interactivo moderno
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
            --accent-red: #ef4444;
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
            display: flex;
            align-items: center;
            gap: 10px;
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
            display: flex;
            align-items: center;
            gap: 8px;
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
        .badge-red {{
            background: rgba(239, 68, 68, 0.15);
            color: var(--accent-red);
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
                <strong>{self.datos_informe.get('ip', 'No resuelta')}</strong>
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
            <ul>
"""
        # Añadir DNS
        dns_data = self.datos_informe.get('dns', [])
        if dns_data:
            for item in dns_data:
                html_content += f"<li>{item}</li>"
        else:
            html_content += "<li>No se recopilaron registros DNS.</li>"

        html_content += """
            </ul>
        </div>
        <div class="card">
            <h3>Información WHOIS</h3>
            <ul>
"""
        whois_data = self.datos_informe.get('whois', [])
        if whois_data:
            for item in whois_data:
                html_content += f"<li>{item}</li>"
        else:
            html_content += "<li>Sin datos WHOIS disponibles.</li>"

        html_content += """
            </ul>
        </div>
        <div class="card">
            <h3>Transparencia de Certificados (crt.sh)</h3>
            <ul>
"""
        crt_data = self.datos_informe.get('crtsh', [])
        if crt_data:
            for item in crt_data:
                html_content += f"<li>{item}</li>"
        else:
            html_content += "<li>Sin registros en crt.sh o módulo desactivado.</li>"

        html_content += """
            </ul>
        </div>
    </div>

    <div class="section-title">⚡ Fase Activa (Servicios y Red)</div>
    <div class="card-grid">
        <div class="card">
            <h3>Cabeceras HTTP & SSL</h3>
            <ul>
"""
        activa_data = self.datos_informe.get('activa', [])
        if activa_data:
            for item in activa_data:
                html_content += f"<li>{item}</li>"
        else:
            html_content += "<li>Módulo activo no ejecutado.</li>"

        html_content += """
            </ul>
        </div>
        <div class="card">
            <h3>Puertos Abiertos & Banners</h3>
            <ul>
"""
        puertos_data = self.datos_informe.get('puertos', [])
        if puertos_data:
            for item in puertos_data:
                html_content += f"<li><span class='badge'>{item}</span></li>"
        else:
            html_content += "<li>No se detectaron puertos abiertos.</li>"

        html_content += """
            </ul>
        </div>
        <div class="card">
            <h3>Bases de Datos & Fuzzing Web</h3>
            <ul>
"""
        bbdd_fuzz = self.datos_informe.get('bbdd_fuzz', [])
        if bbdd_fuzz:
            for item in bbdd_fuzz:
                html_content += f"<li>{item}</li>"
        else:
            html_content += "<li>Sin hallazgos en bases de datos o directorios.</li>"

        html_content += """
            </ul>
        </div>
    </div>

    <div class="footer">
        Generado automáticamente por la herramienta de auditoría táctica en Python.
    </div>
</body>
</html>"""

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(html_content)
            messagebox.showinfo("Éxito", f"Dashboard HTML visual generado correctamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo HTML:\n{e}")

    def iniciar_hilo_analisis(self):
        dominio = self.entry_dominio.get().strip()
        if not dominio:
            messagebox.showwarning("Campo vacío", "Introduce un dominio.")
            return
        dominio = dominio.replace("https://", "").replace("http://", "").split("/")[0]

        self.ejecutando = True
        self.btn_iniciar.config(state="disabled")
        self.btn_detener.config(state="normal")
        self.progress_bar['value'] = 0
        self.lbl_estado.config(text="Estado: Escaneando...", foreground="blue")
        self.datos_informe = {"dominio": dominio, "dns": [], "whois": [], "crtsh": [], "activa": [], "puertos": [], "bbdd_fuzz": []}

        threading.Thread(target=self.ejecutar_proceso, args=(dominio,), daemon=True).start()

    def ejecutar_proceso(self, dominio):
        pasos_totales = 8
        actual = 0

        def actualizar_progreso():
            nonlocal actual
            actual += 1
            self.progress_bar['value'] = (actual / pasos_totales) * 100

        # 0. WHOIS
        if self.var_whois.get() and self.ejecutando:
            self.escribir_log(f"\n[*] --- [PASIVA] CONSULTA WHOIS ({dominio}) ---", "fase")
            try:
                resultado = subprocess.run(["whois", dominio], capture_output=True, text=True, timeout=10)
                if resultado.returncode == 0:
                    for linea in resultado.stdout.splitlines():
                        if any(k in linea.lower() for k in ['registrar', 'creation date', 'name server', 'domain name', 'org']):
                            self.escribir_log(f"  [+] {linea}", "exito")
                            self.datos_informe["whois"].append(linea)
            except Exception as e:
                self.escribir_log(f"  [-] Error whois: {e}", "error")
        actualizar_progreso()

        # 1. DNS
        if self.var_dns.get() and self.ejecutando:
            self.escribir_log(f"\n[*] --- [PASIVA] REGISTROS DNS ({dominio}) ---", "fase")
            for t in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']:
                try:
                    for r in dns.resolver.resolve(dominio, t):
                        txt = f"{t}: {r.to_text()}"
                        self.escribir_log(f"  [+] {txt}", "exito")
                        self.datos_informe["dns"].append(txt)
                except Exception:
                    pass
        actualizar_progreso()

        # 2. crt.sh
        if self.var_crtsh.get() and self.ejecutando:
            self.escribir_log(f"\n[*] --- [PASIVA] CRT.SH ---", "fase")
            try:
                res = requests.get(f"https://crt.sh/?q={dominio}&output=json", timeout=10)
                if res.status_code == 200:
                    datos = res.json()
                    msg = f"Certificados históricos hallados: {len(datos)}"
                    self.escribir_log(f"  [+] {msg}", "exito")
                    self.datos_informe["crtsh"].append(msg)
            except Exception:
                pass
        actualizar_progreso()

        ip = None
        try:
            ip = socket.gethostbyname(dominio)
            self.datos_informe["ip"] = ip
        except Exception:
            pass

        # 3. HTTP Headers
        if self.var_http.get() and ip and self.ejecutando:
            self.escribir_log(f"\n[*] --- [ACTIVA] CABECERAS HTTP ---", "fase")
            try:
                res = requests.get(f"http://{dominio}", timeout=4)
                for h in ['Server', 'X-Powered-By', 'Content-Type']:
                    if h in res.headers:
                        txt = f"{h}: {res.headers[h]}"
                        self.escribir_log(f"  [+] {txt}", "detalle")
                        self.datos_informe["activa"].append(txt)
            except Exception:
                pass
        actualizar_progreso()

        # 4. SSL
        if self.var_ssl.get() and self.ejecutando:
            self.escribir_log(f"\n[*] --- [ACTIVA] CERTIFICADO SSL/TLS ---", "fase")
            try:
                contexto = ssl.create_default_context()
                with socket.create_connection((dominio, 443), timeout=3) as sock:
                    with contexto.wrap_socket(sock, server_hostname=dominio) as ssock:
                        cert = ssock.getpeercert()
                        cn = cert.get('subject', ((('commonName', 'N/A'),),))[0][0][1]
                        txt = f"SSL CN: {cn}"
                        self.escribir_log(f"  [+] {txt}", "exito")
                        self.datos_informe["activa"].append(txt)
            except Exception:
                pass
        actualizar_progreso()

        # 5. Puertos
        if self.var_puertos.get() and ip and self.ejecutando:
            self.escribir_log(f"\n[*] --- [ACTIVA] PUERTOS Y BANNERS ({ip}) ---", "fase")
            for p in [21, 22, 80, 443, 8080]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.5)
                if sock.connect_ex((ip, p)) == 0:
                    txt = f"Puerto {p}/tcp ABIERTO"
                    self.escribir_log(f"  [+] {txt}", "exito")
                    self.datos_informe["puertos"].append(txt)
                sock.close()
        actualizar_progreso()

        # 6. Bases de datos
        if self.var_bbdd.get() and ip and self.ejecutando:
            self.escribir_log(f"\n[*] --- [ACTIVA] BASES DE DATOS ---", "fase")
            for p, m in [(3306, "MySQL"), (5432, "PostgreSQL"), (27017, "MongoDB")]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex((ip, p)) == 0:
                    txt = f"{m} detectado en puerto {p}"
                    self.escribir_log(f"  [+] {txt}", "exito")
                    self.datos_informe["bbdd_fuzz"].append(txt)
                sock.close()
        actualizar_progreso()

        # 7. Fuzzing web
        if self.var_directorios.get() and self.ejecutando:
            self.escribir_log(f"\n[*] --- [ACTIVA] FUZZING WEB ---", "fase")
            wordlist = self.entry_wordlist.get().strip()
            if os.path.exists(wordlist):
                with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
                    lineas = [l.strip() for l in f if l.strip() and not l.startswith("#")][:30]
                for d in lineas:
                    try:
                        r = requests.get(f"http://{dominio}/{d}", timeout=2)
                        if r.status_code in [200, 301, 302, 403]:
                            txt = f"Ruta descubierta: /{d} (HTTP {r.status_code})"
                            self.escribir_log(f"  [+] {txt}", "exito")
                            self.datos_informe["bbdd_fuzz"].append(txt)
                    except Exception:
                        pass
        actualizar_progreso()

        self.progress_bar['value'] = 100
        self.lbl_estado.config(text="Estado: Finalizado", foreground="green")
        self.btn_iniciar.config(state="normal")
        self.btn_detener.config(state="disabled")
        self.ejecutando = False


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionEnumeracionGUI(ventana)
    ventana.mainloop()
