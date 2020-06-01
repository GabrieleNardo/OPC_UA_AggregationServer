# OPC-UA Aggregation Server

Tesina finale relativa al corso Industrial Informatics - UniCT , a.a 2019/2020.

Implementazione in python di un Aggregation Server , utilizzando lo standard OPC-UA. Lo specifico Stack utilizzato è [freeopcua](https://github.com/FreeOpcUa/python-opcua) che presenta l'implementazione in python delle classi Client e Server e relativi metodi associati.

La struttura della repository è la seguente :
- **src** : contiene i file sorgenti contenenti l'i,plementazione, 
- **config** : contiene i file di configurazione per la gestioen dell'aggregazione,
- **certificates** : contiene i certificati x509v3 relativi alle entità sviluppate,
- **docs** : contiene la documentazione dettagliata del progetto.

## Dipendenze
Il Tool è stato implementato in python ( si pressupone che siano già stati installati python3 e pip3 in caso contrario [download](https://www.python.org/downloads/)).

Per una corretta esecuzione è necessario installare i seguenti moduli :
- **opcua**
  
L'installazione delle dipendenze deve essere eseguita tramite i seguenti comandi :

```[shell]
pip3 install opcua ( per installazione dettagliata di opcua seguire il link in alto)

```
