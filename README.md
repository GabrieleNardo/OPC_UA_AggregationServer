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

**config.json :** questo file contiene un elemento sample server per ogni server che si vuole aggregare, per ogni elemento sono previsti 6 capi da configurare opportunamente per settare le informazioni relative al servere e ai dati da tracciare. Di seguito vengono descritti tali campi :
- **server_url**
- **endpoint**
- **security_level**
- **node_id**
- **variable_type**
- **service_req**
- 
```[json]
{
   "sample_server" : {
        "server_url":"",
        "endpoint":"",
        "security_level":"",
        "node_id":"",
        "variable_type":"",
        "service_req":""
    },
}
```
## Avvio
Per avviare l'aggregation server bisogna posizionarsi all'interno della directory principale del progetto e lanciare il seguente comando da terminale :

```[shell]
python .\src\aggregationServer.py

```