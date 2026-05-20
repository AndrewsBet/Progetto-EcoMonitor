# Progetto-EcoMonitor
EcoMonitor
EcoMonitor è un progetto di monitoraggio ambientale realizzato in Python che utilizza l’applicazione mobile Phyphox per raccogliere dati dai sensori dello smartphone.
Il sistema permette di:
raccogliere dati di luminosità e rumore;
inviare i dati via rete locale al computer;
salvare automaticamente le misurazioni in un file CSV;
visualizzare statistiche e grafici tramite una dashboard interattiva.
Funzionamento del progetto
Il progetto è composto da tre parti principali:
1. Server di raccolta dati
File: server_phyphox.py
Il server HTTP:
riceve i dati inviati da Phyphox;
identifica il dispositivo tramite MAC address;
salva le misurazioni nel file dati_phyphox.csv;
gestisce i dati di:
luminosità (lux)
rumore (dB)
2. Launcher principale
File: main.py
Il launcher:
rileva automaticamente l’indirizzo IP locale del computer;
modifica automaticamente il file .phyphox inserendo l’IP corretto;
avvia il server HTTP;
genera un QR Code per collegare facilmente lo smartphone;
apre automaticamente la dashboard.
3. Dashboard grafica
File: dashboard.py
La dashboard mostra:
numero totale delle misurazioni;
media della luminosità;
media del rumore;
grafici temporali;
distribuzione delle misurazioni;
tabella completa dei dati raccolti.
La dashboard è realizzata con:
CustomTkinter
Matplotlib
Tkinter
Struttura del progetto
EcoMonitor/
│
├── main.py
├── server_phyphox.py
├── dashboard.py
├── luce_rumore_tcp.phyphox
├── dati_phyphox.csv
└── README.md
Tecnologie utilizzate
Linguaggi
Python 3
Librerie Python
tkinter
customtkinter
matplotlib
qrcode
pillow
csv
json
http.server
Applicazioni esterne
Phyphox
Installazione
1. Clonare o scaricare il progetto
git clone <repository>
cd EcoMonitor
2. Installare le dipendenze
pip install customtkinter matplotlib qrcode[pil] pillow
Avvio del progetto
Eseguire:
python main.py
Dopo l’avvio:
verrà mostrato un QR Code;
aprire Phyphox sul telefono;
premere +;
scansionare il QR Code;
avviare l’esperimento;
i dati verranno inviati automaticamente al computer.
File CSV
I dati vengono salvati nel file:
dati_phyphox.csv
Formato delle colonne:
mac_address
timestamp_pc
timestamp_telefono
luce_lux
rumore_db
Obiettivo del progetto
L’obiettivo di EcoMonitor è creare un sistema semplice e accessibile per il monitoraggio ambientale utilizzando solamente:
uno smartphone;
una rete locale;
Python.
Il progetto dimostra come integrare:
acquisizione dati;
comunicazione client-server;
salvataggio persistente;
visualizzazione grafica.
Possibili sviluppi futuri
salvataggio su database;
supporto multiutente avanzato;
esportazione PDF dei report;
monitoraggio in tempo reale online;
aggiunta di nuovi sensori;
dashboard web responsive.
Autore
Progetto sviluppato a scopo didattico per il monitoraggio ambientale tramite Phyphox e Python.
 
