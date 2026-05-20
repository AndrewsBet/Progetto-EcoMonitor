"""
Server HTTP per Phyphox - Luce e Rumore
Riceve dati via HTTP POST dal telefono e li salva in CSV.
Il MAC del dispositivo viene ricavato automaticamente tramite ARP (Windows).
"""

import csv
import os
import json
import subprocess
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# ─── CONFIGURAZIONE ───────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8080
CSV_FILE = "dati_phyphox.csv"
# ──────────────────────────────────────────────────────────────────

HEADER_CSV = ["mac_address", "timestamp_pc", "timestamp_telefono", "luce_lux", "rumore_db"]


def ottieni_mac(ip: str) -> str:
    """Ricava il MAC address tramite la tabella ARP di Windows."""
    try:
        subprocess.run(["ping", "-n", "1", "-w", "500", ip], capture_output=True)
        result = subprocess.run(["arp", "-a", ip], capture_output=True, text=True)
        match = re.search(r"([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}", result.stdout)
        if match:
            return match.group(0).replace("-", ":").upper()
        return "sconosciuto"
    except Exception as e:
        print(f"[WARN] Impossibile ricavare il MAC per {ip}: {e}")
        return "sconosciuto"


def inizializza_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER_CSV)
        print(f"[INFO] File CSV creato: {CSV_FILE}")
    else:
        print(f"[INFO] File CSV esistente: {CSV_FILE} — i dati verranno aggiunti in fondo.")


def salva_su_csv(riga: dict):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER_CSV)
        writer.writerow(riga)


class PhyphoxHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/data":
            self.send_response(404)
            self.end_headers()
            return

        # Leggi il body JSON
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            dato = json.loads(body)
            ip_client = self.client_address[0]
            mac = ottieni_mac(ip_client)
            ts_pc = datetime.now().isoformat(timespec="milliseconds")

            # 1. Recuperiamo le liste (se non esistono nel JSON, usiamo liste vuote [])
            t_list      = dato.get("t", [])
            luce_list   = dato.get("luce", [])
            rumore_list = dato.get("rumore", [])

            # 2. CONTROLLO DI SICUREZZA: Estraiamo l'ultimo elemento [-1] SOLO se le liste NON sono vuote
            t_val      = t_list[-1] if t_list else None
            luce_val   = luce_list[-1] if luce_list else None
            rumore_val = rumore_list[-1] if rumore_list else None

            # 3. Salviamo nel CSV solo se i dati di luce e rumore sono effettivamente presenti
            if luce_val is not None and rumore_val is not None:
                riga = {
                    "mac_address":        mac,
                    "timestamp_pc":       ts_pc,
                    "timestamp_telefono": t_val,
                    "luce_lux":           luce_val,
                    "rumore_db":          rumore_val,
                }

                salva_su_csv(riga)
                print(
                    f"  [{ts_pc}] ({mac}) "
                    f"Luce: {luce_val} lux | "
                    f"Rumore: {rumore_val} dB"
                )
            else:
                # Se Phyphox manda un pacchetto vuoto (es. all'avvio), lo ignora senza bloccarsi
                print(f"  [{ts_pc}] ({mac}) Ricevuto pacchetto di controllo vuoto (ignorato)")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        except (json.JSONDecodeError, Exception) as e:
            print(f"[WARN] Errore elaborazione dati: {e}")
            self.send_response(400)
            self.end_headers()

            salva_su_csv(riga)
            print(
                f"  [{ts_pc}] ({mac}) "
                f"Luce: {luce_val} lux | "
                f"Rumore: {rumore_val} dB"
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        except (json.JSONDecodeError, Exception) as e:
            print(f"[WARN] Errore elaborazione dati: {e}")
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silenzia i log HTTP di default


def avvia_server():
    inizializza_csv()

    import socket
    hostname = socket.gethostname()
    try:
        ip_locale = socket.gethostbyname(hostname)
    except Exception:
        ip_locale = "???"

    print("=" * 55)
    print("  SERVER PHYPHOX AVVIATO")
    print(f"  In ascolto su  {ip_locale}:{PORT}")
    print(f"  Endpoint:       http://{ip_locale}:{PORT}/data")
    print(f"  Salvataggio su  {CSV_FILE}")
    print("  Premi Ctrl+C per fermare")
    print("=" * 55)
    print(f"\n  *** Inserisci nel file .phyphox: ***")
    print(f"  address=\"http://{ip_locale}:{PORT}/data\"")
    print()

    server = HTTPServer((HOST, PORT), PhyphoxHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server fermato dall'utente.")
    finally:
        server.server_close()


if __name__ == "__main__":
    avvia_server()
