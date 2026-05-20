"""
EcoMonitor - Launcher principale
Avvia tutto il progetto con un solo comando:
  python main.py

Dipendenze aggiuntive: pip install qrcode[pil] pillow
"""

import subprocess
import threading
import time
import sys
import os
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import tkinter as tk

# ─── CONFIGURAZIONE ───────────────────────────────────────────────
PORT_SERVER  = 8080
PORT_QR      = 8081
PHYPHOX_FILE = "luce_rumore_tcp.phyphox"
# ──────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def ottieni_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return socket.gethostbyname(socket.gethostname())


def prepara_phyphox(ip: str) -> bytes:
    """Legge il file .phyphox e sostituisce SERVER_IP con l'IP reale."""
    path = os.path.join(BASE_DIR, PHYPHOX_FILE)
    with open(path, "r", encoding="utf-8") as f:
        contenuto = f.read()
    # Sostituisce il placeholder con l'IP reale e la porta corretta
    contenuto = contenuto.replace("SERVER_IP", ip)
    contenuto = contenuto.replace(
        f"http://{ip}:8080/data",
        f"http://{ip}:{PORT_SERVER}/data"
    )
    return contenuto.encode("utf-8")


def crea_handler(ip: str):
    """Crea un handler HTTP che serve il .phyphox con IP già sostituito."""
    phyphox_bytes = prepara_phyphox(ip)
    filename = PHYPHOX_FILE

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Serve il file .phyphox con IP già sostituito
            if self.path == f"/{filename}" or self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Content-Length", str(len(phyphox_bytes)))
                self.end_headers()
                self.wfile.write(phyphox_bytes)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    return Handler


def avvia_mini_server(ip: str, porta: int):
    handler = crea_handler(ip)
    server = HTTPServer(("0.0.0.0", porta), handler)
    print(f"[INFO] Mini server HTTP avviato sulla porta {porta}")
    server.serve_forever()


def mostra_qr(ip: str, porta: int, file: str):
    try:
        import qrcode
        from PIL import ImageTk
    except ImportError:
        print("\n[ERRORE] Librerie mancanti. Esegui:")
        print("  pip install qrcode[pil] pillow\n")
        return

    url = f"http://{ip}:{porta}/{file}"
    print(f"[INFO] URL esperimento Phyphox: {url}")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")

    win = tk.Tk()
    win.title("EcoMonitor - Connetti Phyphox")
    win.configure(bg="#F5F5F0")
    win.resizable(False, False)
    win.update_idletasks()
    w, h = 480, 580
    x = (win.winfo_screenwidth()  - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(win, text="EcoMonitor", bg="#F5F5F0",
        font=("Helvetica", 22, "bold"), fg="#1A1A1A"
    ).pack(pady=(28, 2))
    tk.Label(win, text="Scansiona con Phyphox per caricare l'esperimento",
        bg="#F5F5F0", font=("Helvetica", 12), fg="#888888"
    ).pack(pady=(0, 16))

    tk_img = ImageTk.PhotoImage(img_qr)
    tk.Label(win, image=tk_img, bg="#F5F5F0", relief="flat").pack(pady=(0, 16))

    url_frame = tk.Frame(win, bg="#FEF3E2", padx=12, pady=8)
    url_frame.pack(fill="x", padx=40)
    tk.Label(url_frame, text=url, bg="#FEF3E2",
        font=("Courier", 10), fg="#F5A623", wraplength=380
    ).pack()

    tk.Label(win,
        text="1. Apri Phyphox  →  2. Tocca \"+\"  →  3. Scansiona QR",
        bg="#F5F5F0", font=("Helvetica", 11), fg="#888888"
    ).pack(pady=(14, 0))

    tk.Button(win, text="Chiudi e avvia Dashboard →",
        bg="#F5A623", fg="white", font=("Helvetica", 12, "bold"),
        relief="flat", padx=20, pady=10, cursor="hand2",
        command=win.destroy
    ).pack(pady=(16, 28))

    win.mainloop()


def avvia_progetto():
    print("=" * 52)
    print("  ECOMONITOR - Avvio in corso...")
    print("=" * 52)

    # 1. Ricava IP
    ip = ottieni_ip()
    print(f"[INFO] IP locale rilevato: {ip}")

    # 2. Verifica file .phyphox
    phyphox_path = os.path.join(BASE_DIR, PHYPHOX_FILE)
    if not os.path.exists(phyphox_path):
        print(f"\n[ERRORE] File non trovato: {phyphox_path}")
        print(f"  Assicurati che '{PHYPHOX_FILE}' sia nella stessa cartella di main.py")
        input("Premi INVIO per uscire...")
        sys.exit(1)
    print(f"[INFO] File .phyphox trovato, IP '{ip}' verrà inserito automaticamente")

    # 3. Avvia mini server HTTP con IP già iniettato nel file
    t_http = threading.Thread(
        target=avvia_mini_server,
        args=(ip, PORT_QR),
        daemon=True
    )
    t_http.start()
    time.sleep(0.3)

    # 4. Avvia server dati
    server_process = subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "server_phyphox.py")],
        cwd=BASE_DIR
    )
    print(f"[INFO] Server dati avviato sulla porta {PORT_SERVER}")
    time.sleep(0.5)

    # 5. Mostra QR code
    print("[INFO] Apertura finestra QR code...")
    mostra_qr(ip, PORT_QR, PHYPHOX_FILE)

    # 6. Avvia Dashboard
    print("[INFO] Apertura Dashboard...")
    try:
        subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, "dashboard.py")],
            cwd=BASE_DIR
        )
    except KeyboardInterrupt:
        pass
    finally:
        print("\n[INFO] Chiusura server dati...")
        server_process.terminate()
        print("[INFO] EcoMonitor chiuso. Arrivederci!")


if __name__ == "__main__":
    avvia_progetto()
