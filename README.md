# OPC-UA Aggregation Server

Tesina finale relativa al corso Industrial Informatics - UniCT, a.a 2019/2020.

Implementazione in python di un Aggregation Server, utilizzando lo standard OPC-UA. Lo specifico Stack utilizzato è [freeopcua](https://github.com/FreeOpcUa/python-opcua), che presenta l'implementazione in python delle classi Client, Server e relativi metodi associati. 

L'elaborato è stato sviluppato in ambiente Windows, per tale motivo le scelte implementative sono mirate all'esecuzione su tale piattaforma (gestione dei path). Da ciò ne consegue che potrebbero incorrere errori durante l'esecuzione su altre piattaforme diverse da quella presa in considerazione.

La struttura del repository è la seguente:
- **src**: contiene i file sorgenti contenenti l'implementazione dell'elaborato; 
- **config**: contiene i file di configurazione per la gestione dell'aggregazione (formato e campi del _config file_ verranno discussi dettagliatamente nell'apposita sezione);
- **certificates**: contiene i certificati x509v3 e le private keys relativi alle entità sviluppate al fin di poter implementare i meccanismi di sicurezza richiesti da _OPC-UA_;
- **docs**: contiene la documentazione dettagliata del progetto.

## Dipendenze
L'elaborato è stato implementato in python (si pressuppone che siano già stati installati python3 e pip3; in caso contrario [download](https://www.python.org/downloads/)).

Per una corretta esecuzione è necessario importare i seguenti moduli:
- **opcua**
- **json**
  
L'installazione delle dipendenze deve essere eseguita tramite i seguenti comandi:

```[shell]
pip3 install opcua (per installazione dettagliata e relative dipendenze richieste da opcua seguire il link realtivo allo stack)
```
Inoltre è richiesta l'installazione di opnessl per la generazione dei certificati di sicurezza

## File di Configurazione
Nella directory config sono presenti i file __config.json__ e __openssl_conf.json__: il primo contiene le informazioni relative ai server che si vogliono aggregare e ai rispettivi dati alla quale si vuole accedere; nel secondo file invece sono contenute le informazioni necessarie per la generazione dinamica di certificati x509v3.

**openssl_config.json:** in questo file sono presenti due campi da settare opportunamente per la corretta esecuzione del programma: 
- **ssl_installation_path** in questo campo va inserito il proprio path di installazione di openssl; 
- **ssl_confing_file_name** va inserito il nome del file di configurazione di openssl. 
In basso un esempio:

```[json]
{
    "ssl_installation_path":"C:\Program Files\OpenSSL-Win64\bin\openssl.cfg",
    "ssl_confing_file_name":"openssl.cfg"
}
```

**config.json:** questo file contiene un elemento sample server per ogni server che si vuole aggregare. Per ogni elemento sono previsti sei campi da configurare opportunamente per settare le informazioni relative al servere e ai dati da tracciare. Di seguito vengono descritti tali campi e per ognuno di essi sarà presentato in basso un esempio di valore ammissibile:

- **endpoint**: deve contenere l'url del server che si vuole aggregare;
-  **security_policy**: deve contenere una stringa che rappresenti l'algoritmo utilizzato per le operazioni di sicurezza ove previste, in accordo al campo security mode;
-  **security_mode** : deve contenere una stringa contente la modalità di sicurezza richiesta; i valori ammissibili sono: None, Sign e SignAndEncrypt; 
-  **node_id**: deve contenere il node id della variabile di cui si vogliono ottenere i valori sotto forma di stringa formattata nel seguente modo: ‘ns=valore;i=valore’ nel caso si richiedano servizi di _read_ o _write_ è possibile passare una lista di node id separati da una virgola;
-  **variable_type**: deve contenere il tipo della variabile da leggere;
-  **service_req**: definisce il tipo di servizio per otternere i dati, i valori ammissibili sono tre: _read_, _write_, _subscribe_;

Se viene richiesto come servizio la _write_ bisogna settare il campo **new_value** presente in **write_info** che sarà il nuovo valore che verrà attribuito al nodo del sample server e della copia locale nel aggregation server.

Se viene richiesto come servizio la _subscribe_ bisognare settare i sottocampi di **sub_info** che corrispondo alle caratteristiche della subscription e dei relativi monitored item ad essa associati.
- **publish_interval** : definisce il publish interval della subscription in millisecondi;
- **queue_size** : intero che indica la dimensione della coda dei monitored items;
- **deadbandval** : valore da inserie in accordo al tipo di deadband voluta, se si sceglie la deadband percentuale bisogna inserire un numero compreso tra 0 e 100, se si sceglie invece la deadband assoluta bisogna mettere il valore che andrà a costituire la soglia;
- **deadbandtype** : permette di settare il tipo di deadband che verrà presa in considerazione dal datachange filter, come valore ammisibile ha **1** se vogliamo una deadband assoluta e **2** se vogliamo una deadband percentuale. Scegliere una deadband percentuale solo se si vuole monitorare un node analog

A segurie un esempio di configurazione : 

```[json]
{
   "sample_server1" : {
        "endpoint":"opc.tcp://desktop-v6n8m9j:51210/UA/SampleServer",
        "security_policy":"None",
        "security_mode":"None",
        "node_id":"ns=2;i=11212",
        "variable_type":"DataValue",
        "service_req":"subscribe",
        "write_info":{      
            "new_value":""
        },
        "sub_info": {
            "publish_interval": 500,
            "queue_size": 1,
            "deadbandval": 40,
            "deadbandtype": 1
        }
    }
}
```
## Avvio
Per avviare l'aggregation server bisogna posizionarsi all'interno della directory principale del progetto e lanciare il seguente comando da terminale :

```[shell]
python .\src\aggregationServer.py

```