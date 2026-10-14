import threading
import requests
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox


class ManejadorCapturaHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        user_agent = self.headers.get("User-Agent", "No especificado / Desconocido")
        ip_cliente, puerto_cliente = self.client_address
        fecha_hora = datetime.now().strftime("%H:%M:%S")

        if hasattr(self.server, "app_gui"):
            app = self.server.app_gui
            app.escribir_log(f"\n[!] Petición GET interceptada [{fecha_hora}]", "alerta")
            app.escribir_log(f"    |_ Cliente:    {ip_cliente}:{puerto_cliente}", "detalle")
            app.escribir_log(f"    |_ Ruta:       {self.path}", "detalle")
            app.escribir_log(f"    |_ User-Agent: {user_agent}", "exito")

            # Guardar en estructura para el Dashboard HTML
            app.peticiones_capturadas.append({
                "hora": fecha_hora,
                "ip": f"{ip_cliente}:{puerto_cliente}",
                "ruta": self.path,
                "user_agent": user_agent
            })

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head><meta charset="UTF-8"><title>Servidor HTTP Activo</title></head>
        <body style="font-family: sans-serif; background-color: #0b0f19; color: #f3f4f6; padding: 40px;">
            <h2 style="color: #06b6d4;">✔ Petición interceptada correctamente</h2>
            <p><strong>Ruta solicitada:</strong> {self.path}</p>
            <p><strong>User-Agent registrado:</strong> <code style="color: #10b981;">{user_agent}</code></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        return


class ServidorHTTPReutilizable(ThreadingHTTPServer):
    allow_reuse_address = True


class AplicacionCabecerasServidorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auditor de Cabeceras y Servidor HTTP - Dashboard HTML")
        self.root.geometry("960x820")
        self.root.minsize(860, 720)

        self.servidor = None
        self.servidor_activo = False
        self.datos_auditoria = []
        self.peticiones_capturadas = []

        # --- SECCIÓN 1: Auditoría de Cabeceras de Seguridad ---
        frame_auditoria = ttk.LabelFrame(root, text=" 1. Auditoría de Cabeceras de Seguridad ", padding=10)
        frame_auditoria.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_auditoria, text="URL / Sitio Web:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_url = ttk.Entry(frame_auditoria, width=50)
        self.entry_url.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.entry_url.insert(0, "https://www.wikipedia.org")

        self.btn_analizar = ttk.Button(
            frame_auditoria, text="🔍 Analizar Cabeceras", command=self.iniciar_analisis_cabeceras
        )
        self.btn_analizar.grid(row=0, column=2, padx=10, pady=5)

        # --- SECCIÓN 2: Servidor HTTP y Captura de User-Agent ---
        frame_servidor = ttk.LabelFrame(root, text=" 2. Servidor HTTP Local (Captura de User-Agent) ", padding=10)
        frame_servidor.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_servidor, text="Puerto de escucha:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_puerto = ttk.Entry(frame_servidor, width=10)
        self.entry_puerto.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.entry_puerto.insert(0, "8080")

        self.btn_iniciar_srv = ttk.Button(
            frame_servidor, text="▶ Iniciar Servidor", command=self.iniciar_servidor
        )
        self.btn_iniciar_srv.grid(row=0, column=2, padx=5, pady=5)

        self.btn_detener_srv = ttk.Button(
            frame_servidor, text="⏹ Detener Servidor", command=self.detener_servidor, state="disabled"
        )
        self.btn_detener_srv.grid(row=0, column=3, padx=5, pady=5)

        self.btn_probar_srv = ttk.Button(
            frame_servidor, text="🧪 Petición de Prueba", command=self.enviar_peticion_prueba, state="disabled"
        )
        self.btn_probar_srv.grid(row=0, column=4, padx=10, pady=5)

        self.lbl_estado_srv = ttk.Label(frame_servidor, text="Servidor: Detenido", foreground="red")
        self.lbl_estado_srv.grid(row=1, column=0, columnspan=5, sticky="w", padx=5, pady=(5, 0))

        # --- Barra de Progreso ---
        frame_progreso = ttk.LabelFrame(root, text=" Progreso de Análisis ", padding=8)
        frame_progreso.pack(fill="x", padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(frame_progreso, orient="horizontal", mode="determinate", length=100)
        self.progress_bar.pack(fill="x", padx=5, pady=2)

        # --- Barra de Utilidades ---
        frame_util = ttk.Frame(root, padding=2)
        frame_util.pack(fill="x", padx=10)

        btn_html = ttk.Button(frame_util, text="🌐 Exportar Dashboard HTML (Visual)", command=self.guardar_html_dashboard)
        btn_html.pack(side="right", padx=5)

        btn_limpiar = ttk.Button(frame_util, text="🗑 Limpiar Consola", command=self.limpiar_consola)
        btn_limpiar.pack(side="right", padx=5)

        # --- SECCIÓN 3: Consola de Resultados y Logs ---
        frame_consola = ttk.LabelFrame(root, text=" Consola de Resultados y Peticiones Capturadas ", padding=5)
        frame_consola.pack(fill="both", expand=True, padx=10, pady=5)

        self.consola = scrolledtext.ScrolledText(
            frame_consola, wrap=tk.WORD, bg="#050505", fg="#00ff66", font=("Consolas", 10)
        )
        self.consola.pack(fill="both", expand=True)

        self.consola.tag_config("titulo", foreground="#00ffff", font=("Consolas", 10, "bold"))
        self.consola.tag_config("exito", foreground="#4ec9b0")
        self.consola.tag_config("error", foreground="#ff3333")
        self.consola.tag_config("detalle", foreground="#ce9178")
        self.consola.tag_config("alerta", foreground="#dcdcaa", font=("Consolas", 10, "bold"))

        self.root.protocol("WM_DELETE_WINDOW", self.al_cerrar_ventana)

    def escribir_log(self, texto, etiqueta=None):
        self.consola.insert(tk.END, texto + "\n", etiqueta)
        self.consola.see(tk.END)

    def limpiar_consola(self):
        self.consola.delete(1.0, tk.END)
        self.progress_bar['value'] = 0
        self.datos_auditoria = []
        self.peticiones_capturadas = []

    def guardar_html_dashboard(self):
        if not self.datos_auditoria and not self.peticiones_capturadas:
            messagebox.showwarning("Sin datos", "Realiza una auditoría o recibe peticiones antes de exportar el dashboard.")
            return

        sitio = self.entry_url.get().strip().replace("https://", "").replace("http://", "").split("/")[0] or "auditoria"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nombre_sugerido = f"dashboard_cabeceras_{sitio.replace('.', '_')}.html"

        ruta = filedialog.asksaveasfilename(
            initialfile=nombre_sugerido, defaultextension=".html", filetypes=[("Archivos HTML", "*.html"), ("Todos", "*.*")]
        )

        if not ruta:
            return

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
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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
            margin-bottom: 8px;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            word-break: break-all;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .badge-green {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); }}
        .badge-red {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.9rem;
        }}
        th {{
            background: #1f2937;
            color: var(--accent-cyan);
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
        <h1>🛡️ Dashboard de Seguridad Web & User-Agents</h1>
        <div class="meta-grid">
            <div class="meta-card">
                <span>Sitio Auditado</span>
                <strong>{sitio}</strong>
            </div>
            <div class="meta-card">
                <span>Fecha del Informe</span>
                <strong>{timestamp}</strong>
            </div>
            <div class="meta-card">
                <span>Peticiones Capturadas</span>
                <strong>{len(self.peticiones_capturadas)} clientes</strong>
            </div>
        </div>
    </div>

    <div class="section-title">🔍 1. Auditoría de Cabeceras de Seguridad</div>
    <div class="card-grid">
        <div class="card" style="grid-column: 1 / -1;">
            <h3>Estado de Cabeceras HTTP</h3>
            <ul>
"""
        if self.datos_auditoria:
            for item in self.datos_auditoria:
                estado_clase = "badge-green" if item['estado'] == "PRESENTE" else "badge-red"
                html_content += f"<li><span class='badge {estado_clase}'>{item['estado']}</span> <strong>{item['cabecera']}</strong>: {item['valor']}</li>"
        else:
            html_content += "<li>No se ha realizado ninguna auditoría de cabeceras en esta sesión.</li>"

        html_content += """
            </ul>
        </div>
    </div>

    <div class="section-title">⚡ 2. Servidor HTTP (User-Agents Interceptados)</div>
"""
        if self.peticiones_capturadas:
            html_content += """
    <table>
        <thead>
            <tr>
                <th>Hora</th>
                <th>Cliente IP:Puerto</th>
                <th>Ruta</th>
                <th>User-Agent Detectado</th>
            </tr>
        </thead>
        <tbody>
"""
            for pet in self.peticiones_capturadas:
                html_content += f"""
            <tr>
                <td>{pet['hora']}</td>
                <td>{pet['ip']}</td>
                <td>{pet['ruta']}</td>
                <td style="font-family: monospace; color: #10b981;">{pet['user_agent']}</td>
            </tr>
"""
            html_content += """
        </tbody>
    </table>
"""
        else:
            html_content += "<p style='color: var(--text-muted);'>No se han interceptado peticiones de clientes en el servidor local todavía.</p>"

        html_content += """
    <div class="footer">
        Generado automáticamente mediante Herramienta de Auditoría Python.
    </div>
</body>
</html>"""

        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(html_content)
            messagebox.showinfo("Éxito", f"Dashboard HTML visual generado correctamente en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo HTML:\n{e}")

    # --- LÓGICA DE AUDITORÍA DE CABECERAS ---
    def iniciar_analisis_cabeceras(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Campo vacío", "Introduce una URL o dominio.")
            return

        self.btn_analizar.config(state="disabled")
        self.progress_bar['value'] = 0
        self.datos_auditoria = []
        hilo = threading.Thread(target=self.ejecutar_analisis_cabeceras, args=(url,), daemon=True)
        hilo.start()

    def ejecutar_analisis_cabeceras(self, url):
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        self.escribir_log("==================================================", "titulo")
        self.escribir_log(f" ANALIZANDO CABECERAS DE SEGURIDAD EN: {url}", "titulo")
        self.escribir_log("==================================================", "titulo")

        cabeceras_seguridad = {
            "Strict-Transport-Security": "Fuerza conexiones HTTPS (HSTS).",
            "Content-Security-Policy": "Mitiga ataques XSS (CSP).",
            "X-Frame-Options": "Previene Clickjacking.",
            "X-Content-Type-Options": "Bloquea MIME-sniffing.",
            "Referrer-Policy": "Controla cabecera Referer.",
            "Permissions-Policy": "Restringe APIs del navegador.",
            "X-XSS-Protection": "Filtro XSS."
        }

        total = len(cabeceras_seguridad)
        try:
            headers_peticion = {"User-Agent": "Mozilla/5.0 (Security-Auditor-GUI/1.0)"}
            res = requests.get(url, headers=headers_peticion, timeout=8)

            self.escribir_log(f"[+] Conexión exitosa (Estado HTTP: {res.status_code})", "exito")
            self.escribir_log(f"[+] URL final: {res.url}\n", "detalle")

            presentes = 0
            for i, (cabecera, desc) in enumerate(cabeceras_seguridad.items(), 1):
                self.progress_bar['value'] = (i / total) * 100
                valor = res.headers.get(cabecera)
                if valor:
                    presentes += 1
                    self.escribir_log(f"[+] PRESENTE | {cabecera}", "exito")
                    self.escribir_log(f"    |_ Valor: {valor}", "detalle")
                    self.datos_auditoria.append({"cabecera": cabecera, "estado": "PRESENTE", "valor": valor})
                else:
                    self.escribir_log(f"[-] AUSENTE  | {cabecera}", "error")
                    self.escribir_log(f"    |_ Info:  {desc}")
                    self.datos_auditoria.append({"cabecera": cabecera, "estado": "AUSENTE", "valor": desc})

            self.progress_bar['value'] = 100
            self.escribir_log(f"\n[*] Resumen: {presentes}/{total} cabeceras presentes.", "titulo")
        except requests.RequestException as e:
            self.escribir_log(f"[!] Error al conectar con el sitio: {e}", "error")
        finally:
            self.btn_analizar.config(state="normal")

    # --- LÓGICA DEL SERVIDOR HTTP ---
    def iniciar_servidor(self):
        puerto_str = self.entry_puerto.get().strip()
        if not puerto_str.isdigit() or not (1 <= int(puerto_str) <= 65535):
            messagebox.showerror("Puerto inválido", "Introduce un número de puerto válido (1 - 65535).")
            return

        puerto = int(puerto_str)

        try:
            self.servidor = ServidorHTTPReutilizable(("0.0.0.0", puerto), ManejadorCapturaHTTP)
            self.servidor.app_gui = self
            self.servidor_activo = True

            hilo_srv = threading.Thread(target=self.servidor.serve_forever, daemon=True)
            hilo_srv.start()

            self.btn_iniciar_srv.config(state="disabled")
            self.entry_puerto.config(state="disabled")
            self.btn_detener_srv.config(state="normal")
            self.btn_probar_srv.config(state="normal")
            self.lbl_estado_srv.config(
                text=f"Servidor: ACTIVO escuchando en http://localhost:{puerto}", foreground="green"
            )

            self.escribir_log("\n==================================================", "titulo")
            self.escribir_log(f" SERVIDOR HTTP INICIADO EN PUERTO {puerto}", "titulo")
            self.escribir_log("==================================================", "titulo")
            self.escribir_log(f"[*] Abre http://localhost:{puerto} en tu navegador o pulsa 'Petición de Prueba'.")

        except PermissionError:
            messagebox.showerror("Permiso denegado", f"El puerto {puerto} requiere privilegios de root (ej. usa 8080).")
        except OSError as e:
            messagebox.showerror("Error al iniciar", f"No se pudo iniciar el servidor en el puerto {puerto}:\n{e}")

    def detener_servidor(self):
        if self.servidor and self.servidor_activo:
            threading.Thread(target=self._apagar_servidor_interno, daemon=True).start()

    def _apagar_servidor_interno(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.servidor_activo = False

        self.btn_iniciar_srv.config(state="normal")
        self.entry_puerto.config(state="normal")
        self.btn_detener_srv.config(state="disabled")
        self.btn_probar_srv.config(state="disabled")
        self.lbl_estado_srv.config(text="Servidor: Detenido", foreground="red")
        self.escribir_log("\n[*] Servidor HTTP detenido correctamente.", "error")

    def enviar_peticion_prueba(self):
        if not self.servidor_activo:
            return
        puerto = self.entry_puerto.get().strip()
        url_local = f"http://localhost:{puerto}/prueba-gui"

        def _peticion():
            try:
                headers = {"User-Agent": "Cliente-Prueba-KaliLinux/1.0 (Simulador GUI)"}
                requests.get(url_local, headers=headers, timeout=3)
            except requests.RequestException as e:
                self.escribir_log(f"[-] Error en petición de prueba: {e}", "error")

        threading.Thread(target=_peticion, daemon=True).start()

    def al_cerrar_ventana(self):
        if self.servidor and self.servidor_activo:
            self.servidor.shutdown()
            self.servidor.server_close()
        self.root.destroy()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionCabecerasServidorGUI(ventana)
    ventana.mainloop()
