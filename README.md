# OPC-UA Aggregation Server

Tesina finale relativa al corso Industrial Informatics - UniCT, a.a 2019/2020.

Implementazione in python di un Aggregation Server, utilizzando lo standard OPC-UA. Lo specifico Stack utilizzato è [freeopcua](https://github.com/FreeOpcUa/python-opcua), che presenta l'implementazione in python delle classi Client, Server e relativi metodi associati. 

L'elaborato è stato sviluppato in ambiente Windows, per tale motivo le scelte implementative sono mirate all'esecuzione su tale piattaforma (gestione dei path). Da ciò ne consegue che potrebbero incorrere errori durante l'esecuzione su altre piattaforme diverse da quella presa in considerazione.

La struttura del repository è la seguente:
- **src**: contiene i file sorgenti contenenti l'implementazione dell'elaborato; 
- **config**: contiene il file di configurazione per la gestione dell'aggregazione (formato e campi del _config file_ verranno discussi dettagliatamente nell'apposita sezione);
- **certificates**: contiene i certificati x509v3 e le private keys relativi alle entità sviluppate al fin di poter implementare i meccanismi di sicurezza richiesti da _OPC-UA_;
- **docs**: contiene la documentazione dettagliata del progetto.

## Dipendenze
L'elaborato è stato implementato in python (si pressuppone che siano già stati installati python3 e pip3; in caso contrario [download](https://www.python.org/downloads/)).

Per una corretta esecuzione è necessario importare i seguenti moduli:
- **opcua**
- **json**
- **threading**
  
L'installazione delle dipendenze deve essere eseguita tramite i seguenti comandi:

```[shell]
pip3 install opcua (per installazione dettagliata e relative dipendenze richieste da opcua seguire il link realtivo allo stack)
```
Inoltre è richiesta l'installazione di opnessl per la generazione dei certificati di sicurezza

## File di Configurazione
Nella directory config è presente il file __config.json__ che contiene le informazioni relative ai server che si vogliono aggregare e ai rispettivi dati alla quale si vuole accedere.

**config.json:** questo file contiene un elemento sample server per ogni server che si vuole aggregare. Per ogni elemento sono previsti dei campi da configurare opportunamente per settare le informazioni relative al server e ai dati da tracciare, e per far si che l'applicativo esegua correttamente. Di seguito vengono descritti tali campi e per ognuno di essi sarà presentato in basso un esempio con dei valori ammissibili:

- **endpoint**: deve contenere l'url del server che si vuole aggregare;
-  **security_policy**: deve contenere una stringa che rappresenti l'algoritmo utilizzato per le operazioni di sicurezza, ove previste, in accordo al campo security mode. I valori ammissibili sono None se scegliamo come mode None, Basic256 se scegliamo come mode Sign o Basic256Sha256/Basic128Rsa15 se scegliamo come mode SignAndEncrypt;
-  **security_mode** : deve contenere una stringa contente la modalità di sicurezza richiesta; i valori ammissibili sono: None, Sign e SignAndEncrypt; 
-  **node_ids**: deve contenere il node id della variabile di cui si vogliono ottenere i valori sotto forma di stringa formattata nel seguente modo: ‘ns=valore;i=valore’; è possibile passare una lista di node id separati da una virgola, se vogliamo tener traccia di più nodi;
-  **service_req**: definisce il tipo di servizio per otternere i dati, i valori ammissibili sono tre: _read_, _write_, _subscribe_;

Se viene richiesto come servizio la _write_ bisogna settare il campo **new_value** presente in **write_info** che conterrà il nuovo valore o i nuovi valori da scrivere sui nodi del sample server e sulla copia locale nell’aggregation server.

Se viene richiesto come servizio la _subscribe_, bisogna creare uno o più elementi all'interno del campo __sub_infos__: ognuno degli elementi deve avere la struttura indicata nell'esempio in basso; in sintesi, tutti gli elementi devono avere come nome **‘sub_infoi’ (con i un intero che parte da 1 e viene incrementato di un’unità per ogni nuovo elemento sub_info)**. Tali elementi andranno ad indicare le configurazioni delle n sottoscrizioni con parametri distinti che si vogliono creare. Il numero massimo di sub_info che è possibile inserire è pari al numero dei nodeid che si vogliono monitorare.

**NOTA BENE: tutti i sub_info inseriti devono essere utilizzati e quindi assegnati**

L'assegnazione della sub_infoi allo specifico nodeid avviene settando opportunamente il campo __sub_info_ids__. Tale campo deve contenere una stringa che rappresenta una lista di interi corrispondenti all'identificativo del sub_infoi. Ad esempio, avendo a disposizione sub_info1 e sub_info2, i valori ammissibili da sub_info_ids saranno proprio 1 e 2. L'ordine con cui vengono passati tali numeri deve fare riferimento all'ordine con cui vanno passati i nodeid nel campo node_ids.

**Esempio:"node_ids":"ns=2;i=11212,ns=2;i=11206,ns=2;i=11224"sub_info_ids="1,2,2" --> così al primo nodeid verrà assegnata la configurazione sub_info1, al secondo nodeid verrà assegnata sub_info2 ed al terzo, ancora sub_info2**

Ogni sub_infoi contiene i seguenti campi:
- **requested_publish_interval**: definisce il publish interval della subscription in millisecondi;
- **requested_lifetime_count**: intero che indica quante volte il publishing interval può trascorrere senza che sia monitorata alcuna attività da parte del client. Passato questo lasso di tempo, il server cancella la Subscription e libera le risorse. **NOTA BENE: questo parametro dev’essere grande almeno tre volte il keep alive count;**
- **requested_max_keepalive_timer**: intero che indica quante volte il publishing interval deve trascorrere senza che sia disponibile alcuna Notifications da inviare al Client, perché il server mandi un keep-alive messagge al client in grado di comunicargli che quella particolare Subscription è ancora attiva;
- **max_notif_per_publish**: intero che indica il numero massimo di notifiche per ogni publish;
- **publishing_enabled**: booleano che abilità la pubblicazione dei messaggi prodotti dai monitored item;
- **priority**: intero che indica la priorità associata alla sottoscrizione;

In caso di sottoscrizione bisogna inoltre creare uno o più elementi all'interno del campo **monitored_item_infos**, i quali elementi devono avere la struttura indicata nell'esempio in basso in sintesi, tutti gli elementi devono avere come nome **monitored_item_infosi (con i un intero che parte da 1 e viene incrementato di un’unità per ogni nuovo elemento monitored_item_info)**. Tali elementi andranno ad indicare le configurazioni degli n monitored item con parametri distinti che si vogliono creare ed associare alle variabili da monitorare. Il numero massimo di monitored_item_infos che è possibile inserire è pari al numero dei nodeid che si vogliono monitorare.

**NOTA BENE: tutti i monitored_item_infos inseriti devono essere utilizzati e quindi assegnati**

L'assegnazione dei __monitored_item_infos’i’__ allo specifico nodeid avviene settando opportunamente il campo **monitored_item_info_ids**. Il riempimento di questo campo segue le stesse regole descritte precedentemente per sub_info_ids. I campi di __monitored_item_infos’i’__ sono:
- **sampling_interval**: intero che indica l'intervallo di tempo con la quale vengono prodotte le notifiche dai monitored item e poste nella coda dei messaggi;
- **queue_size**: intero che indica la dimensione della coda dei monitored items;
- **discard_oldest**: booleano che definisce la politica di gestione dei messaggi quando la coda del monitored item è piena;
- **deadbandval**: valore da inserie in accordo al tipo di deadband voluta: se si sceglie la deadband percentuale bisogna inserire un numero compreso tra 0 e 100; se si sceglie invece la deadband assoluta bisogna mettere il valore che andrà a costituire la soglia;
- **deadbandtype**: permette di settare il tipo di dead band che verrà presa in considerazione dal datachange filter, come valore ammissibile ha **1** se vogliamo una dead band assoluta, **2** se vogliamo una deadband percentuale e **0** se vogliamo aggiornare continuamente la variabile ad ogni cambiamento di valore. Scegliere una dead band percentuale solo se si vuole monitorare un node analog.

A segurie un esempio di configurazione : 

```[json]
{
   "sample_server1": {
        "endpoint":"opc.tcp://DESKTOP-V6N8M9J:51210/UA/SampleServer",
        "security_policy":"None",
        "security_mode":"None",
        "node_ids":"ns=2;i=11212,ns=2;i=11206,ns=2;i=11224",
        "service_req":"subscribe",
        "write_info":{      
            "new_value":"2,5"
        },
        "sub_infos": {
            "sub_info1":{
                "requested_publish_interval": 2000,
                "requested_lifetime_count": 30000,
                "requested_max_keepalive_timer": 5000,
                "max_notif_per_publish": 2147483647,
                "publishing_enabled": true,
                "priority": 0
            },
            "sub_info2":{
                "requested_publish_interval": 3000,
                "requested_lifetime_count": 30000,
                "requested_max_keepalive_timer": 5000,
                "max_notif_per_publish": 2147483647,
                "publishing_enabled": true,
                "priority": 0
            }
        },
        "sub_info_ids":"2,1,2",
        "monitored_item_infos":{
            "monitored_item_infos1":{
                "sampling_interval": 2000,
                "queue_size": 1,
                "discard_oldest": true,
                "deadbandval": 40,
                "deadbandtype": 2
            },
            "monitored_item_infos2":{
                "sampling_interval": 3000,
                "priority": 0,
                "queue_size": 1,
                "discard_oldest": true,
                "deadbandval": 60,
                "deadbandtype": 1
            }
        },
        "monitored_item_info_ids": "1,1,2"
    },

    "sample_server2" : {
        "endpoint":"opc.tcp://DESKTOP-V6N8M9J:51210/UA/SampleServer",
        "security_policy":"None",
        "security_mode":"None",
        "node_ids":"ns=2;i=11200,ns=2;i=11194",
        "service_req":"subscribe",
        "write_info":{      
            "new_value":"2,5"
        },
        "sub_infos": {
            "sub_info1":{
                "requested_publish_interval": 4000,
                "requested_lifetime_count": 30000,
                "requested_max_keepalive_timer": 5000,
                "max_notif_per_publish": 2147483647,
                "publishing_enabled": true,
                "priority": 0
            },
            "sub_info2":{
                "requested_publish_interval": 1000,
                "requested_lifetime_count": 30000,
                "requested_max_keepalive_timer": 5000,
                "max_notif_per_publish": 2147483647,
                "publishing_enabled": true,
                "priority": 0
            }
        },
        "sub_info_ids":"1,2",
        "monitored_item_infos":{
            "monitored_item_infos1":{
                "sampling_interval": 4000,
                "queue_size": 1,
                "discard_oldest": true,
                "deadbandval": 90,
                "deadbandtype": 1
            },
            "monitored_item_infos2":{
                "sampling_interval": 1000,
                "priority": 0,
                "queue_size": 1,
                "discard_oldest": true,
                "deadbandval": 20,
                "deadbandtype": 2
            }
        },
        "monitored_item_info_ids": "2,1"
    }
}   
```
## Creazione Certificati
Per il corretto funzionamento dell’elaborato e per utilizzare i meccanismi di sicurezza offerti da OPC-UA è necessario creare i certificati di sicurezza x509v3 da posizionare all’interno della directory _certificates_ del progetto. Per la creazione dei certificati è necessario aver installato openssl sulla propria macchina.

Bisogna posizionarsi all’interno del path di installazione di Openssl nella directory bin. Una volta situati in questo path “C:\Program Files\OpenSSL-Win64\bin”, bisogna creare un file di configurazione per openssl con la seguente struttura:

```[shell]
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
C = US
ST = VA
L = SomeCity
O = MyCompany
OU = MyDivision
CN = AggregationServer / AggregationClient
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = “inserire qui hostname della propria macchina”
```

Importante settare opportunamente i campi CN e DNS.1. Il campo CN indica il common name dell’applicazione, invece DNS.1 indica l’identità della macchina su cui sta girando l’applicazione. Per il campo CN in alto sono presenti i valori da inserire: il primo va usato per la creazione del certificato del server, invece il secondo va usato per la creazione del certificato del client. Se non si conosce l’hostname della propria macchina basta digitare il comando hostname sul terminale.

Per questo esempio il file di configurazione creato verrà chiamato my_config.conf.

Partendo quindi dalla directory C:\Program Files\OpenSSL-Win64\bin, lanciare il file exe di openssl e inserire i seguenti comandi:

- **[Server Certificates]**
```[shell]
req -x509 -nodes -days 355 -newkey rsa:2048 -keyout server_private_key.pem -out server_certificate.pem -config my_config.conf

x509 -outform der -in server_certificate.pem -out server_certificate.der

```

- **[Client Certificates]**
```[shell]
req -x509 -nodes -days 355 -newkey rsa:2048 -keyout client_private_key.pem -out client_certificate.pem -config my_config.conf

x509 -outform der -in client_certificate.pem -out client_certificate.der
```
## Avvio
Per testare/utilizzare il software è necessario seguire i seguenti step:

- Compilare opportunamente il file di configurazione _config.json_ presente nella directory config della repository;
- Avviare il/i server che si vogliono aggregare;
- Avviare l'aggregation server posizionandosi all'interno della directory principale del progetto e lanciare il seguente comando da terminale:

```[shell]
python .\src\aggregationServer.py

```

- Collegarsi all’aggregation server attraverso un client

## Altre Info
Una descrizione dettagliata dell'implementazione è presente nel file _Relazione.pdf_ situato nella directory **docs**