# OPC-UA Aggregation Server

Tesina finale relativa al corso Industrial Informatics - UniCT , a.a 2019/2020.

Implementazione in python di un Aggregation Server , utilizzando lo standard OPC-UA. Lo specifico Stack utilizzato è [freeopcua](https://github.com/FreeOpcUa/python-opcua) che presenta l'implementazione in python delle classi Client e Server e relativi metodi associati. 

L'elaborato è stato sviluppato in ambiente Windows , per tale motivo le scelte implementative sono mirate all'esecuzione su tale piattaforma ( gestione dei path ), da ciò ne consegue che potrebbero incorrere errori durante l'esecuzione su altre piattaforme diverse da quella presa in cosiderazione.

La struttura della repository è la seguente :
- **src** : contiene i file sorgenti contenenti l'implementazione dell'elaborato, 
- **config** : contiene i file di configurazione per la gestione dell'aggragazione ( formato e campi del _config file_ verranno discussi dettagliatamente nell'apposita sezione ),
- **certificates** : contiene i certificati x509v3 relativi alle entità sviluppate al fin di poter implementare i meccanismi di sicurezza richiesti da _OPC-UA_,
- **docs** : contiene la documentazione dettagliata del progetto.

## Dipendenze
L'elaborato è stato implementato in python ( si pressuppone che siano già stati installati python3 e pip3 in caso contrario [download](https://www.python.org/downloads/)).

Per una corretta esecuzione è necessario importare i seguenti moduli :
- **opcua**
- **json**
  
L'installazione delle dipendenze deve essere eseguita tramite i seguenti comandi :

```[shell]
pip3 install opcua ( per installazione dettagliata e realtive dipendenze ruchieste da opcua seguire il link in alto)

```
