# OPC-UA Aggregation Server

Tesina finale relativa al corso Industrial Informatics - UniCT , a.a 2019/2020.

Implementazione in python di un Aggregation Server , utilizzando lo standard OPC-UA. Lo specifico Stack utilizzato è [freeopcua](https://github.com/FreeOpcUa/python-opcua) che presenta l'implementazione in python delle classi Client e Server e relativi metodi associati. 

L'elaborato è stato sviluppato in ambiente Windows , per tale motivo le scelte implementative sono mirate all'esecuzione su tale piattaforma ( gestione dei path ), da ciò ne consegue che potrebbero incorrere errori durante l'esecuzione su altre piattaforme diverse da quella presa in considerazione.

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
pip3 install opcua ( per installazione dettagliata e relative dipendenze richieste da opcua seguire il link realtivo allo stack )
```
Inoltre è richiesta l'installazione di opnessl per la generazione dei certificati di sicurezza

## File di Configurazione
Nella directory config sono presenti i file __config.json__ e __openssl_conf.json__ , il primo contiene le informazioni relative ai server ch si vogliono aggregare, e ai rispettivi dati a cui si vuole accedere; nel secondo file invece sono contenute le informazioni necessarie per la generazione dinamica di certificati x509v3.

**openssl_config.json :** in questo file sono presenti due campi da settare opportunamente per la corretta esecuzione del programma. 
- **ssl_installation_path** in questo campo va inserito il proprio path di installazione di openssl. 
- **ssl_confing_file_name** va inserito il nome del file di configurazione di openssl. In basso un esempio

```[json]
{
    "ssl_installation_path":"C:\Program Files\OpenSSL-Win64\bin\openssl.cfg",
    "ssl_confing_file_name":"openssl.cfg"
}
```

**config.json :** questo file contiene un elemento sample server per ogni server che si vuole aggregare, per ogni elemento sono previsti 6 capi da configurare opportunamente per settare le informazioni relative al servere e ai dati da tracciare. Di seguito vengono descritti tali campi, per ognuno di essi sarà presentato in basso un esempio di valore e la possibilità dei valori ammissibili :

- **endpoint** : deve contenere l'url del server che si vuole aggregare,
-  **security_policy** : deve contenere una stringa che rappresenti l'algoritmo utilizzato per le operazioni di sicurezza ove previste , in accordo al campo security mode,
-  **security_mode** : deve contenere una stringa contente la modalità di sicurezza richiesta , i valori ammissibili sono None , Sign e SignAndEncrypt, 
-  **node_id** : deve contenere il node id della variabile di cui si vogliono ottenere i valori soto forma di stringa formattata nel seguente modo ns=valore;i=valore,
-  **variable_type** : deve contenere il tipo della variabile da leggere,
-  **service_req** : definisce il tipo di servizio per otternere i dati , i valori ammissibili  sono due , _polling_ per abilitare un accesso ai dati utilizzando i servizi read/write e _subscribe_ per abilitare l'accesso ai dati in modalità pub/sub
- **publish_interval** : da settare solo se si sceglie come valore di service_req _subscribe_ , inserire un intero senza segno , tener conto che è il valore inidicherà millisecondi.

```[json]
{
   "sample_server1" : {
        "endpoint":"opc.tcp://pc-mario:51210/UA/SampleServer",
        "security_policy":"None",
        "security_mode":"None",
        "node_id":"ns=2;i=10852",
        "variable_type":"DataValue",
        "service_req":"polling",
        "publish_interval": ""
    },
}
```
## Avvio
Per avviare l'aggregation server bisogna posizionarsi all'interno della directory principale del progetto e lanciare il seguente comando da terminale :

```[shell]
python .\src\aggregationServer.py

```