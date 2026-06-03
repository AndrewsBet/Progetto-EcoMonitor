Requisiti e Installazione
1. Prerequisiti
Assicurati di avere installato Python 3.8 o superiore sul tuo computer e l'applicazione Phyphox sul tuo smartphone (disponibile gratuitamente su Android e iOS). I dispositivi (PC e Smartphone) devono essere connessi alla stessa rete Wi-Fi.

2. Installazione delle dipendenze
Clona o estrai il progetto sul tuo computer, apri il terminale all'interno della cartella del progetto ed esegui il seguente comando per installare le librerie necessarie:
  pip install -r requirements.txt

Le dipendenze incluse nel file requirements.txt sono:
customtkinter (Interfaccia grafica moderna)
matplotlib (Generazione dei grafici statistici)
tkintermapview (Integrazione di mappe interattive OpenStreetMap)
qrcode[pil] & pillow (Generazione e renderizzazione del codice QR)

Come Usare il Sistema
1. Avvia il progetto sul PC:
   Esegui il file di lancio principale dal terminale:
   python main.py
2. Connetti lo Smartphone:
   A schermo comparirà una finestra con un codice QR. Apri l'app Phyphox sullo smartphone, seleziona l'opzione per aggiungere un esperimento tramite codice QR e inquadra lo schermo.

3. Avvia la Raccolta Dati:
   Una volta caricato l'esperimento "Luce e Rumore" su Phyphox, premi il pulsante Play (Avvia) in alto nell'app. Lo smartphone inizierà a trasmettere i dati dei sensori al PC.

4. Esplora la Dashboard:
   In contemporanea si aprirà la EcoMonitor Dashboard sul PC. Potrai navigare tra le varie schede laterali per osservare i grafici aggiornarsi in tempo reale e vedere i punti mappati geograficamente sulla mappa.

5. Chiusura sicura:
   Chiudendo la dashboard sul PC, il sistema interromperà automaticamente il server in background e avvierà la routine di sanificazione del file CSV per preservare l'integrità dei dati.

Personalizzazione del Tema
La dashboard supporta il cambio di tema dinamico. All'interno della scheda Settings, è possibile attivare o disattivare la modalità scura per adattare l'interfaccia visiva alle proprie preferenze o alle condizioni di luce del laboratorio.
