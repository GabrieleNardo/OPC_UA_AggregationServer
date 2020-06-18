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

**config.json:** questo file contiene un array sample, tale array avrà un elemento per ogni server che si vuole aggregare. Per ogni elemento sono previsti dei campi da configurare opportunamente per settare le informazioni relative al server e ai dati da tracciare, e per far si che l'applicativo esegua correttamente. Di seguito vengono descritti tali campi e per ognuno di essi sarà presentato in basso un esempio con dei valori ammissibili:

- **serverName** : stringa che indica il nome server da aggragare che verrà visualizzato collegandosi all'aggreagtion server;
- **endpoint**: deve contenere l'url del server che si vuole aggregare;
-  **security_policy**: deve contenere una stringa che rappresenti l'algoritmo utilizzato per le operazioni di sicurezza, ove previste, in accordo al campo security mode. I valori ammissibili sono None se scegliamo come mode None, Basic256 se scegliamo come mode Sign o Basic256Sha256/Basic128Rsa15 se scegliamo come mode SignAndEncrypt;
-  **security_mode** : deve contenere una stringa contente la modalità di sicurezza richiesta; i valori ammissibili sono: None, Sign e SignAndEncrypt; 

Il campo **sub_infos** è anch'esso un array, ogni suo elemento indicherà le caratteristiche di una singola subscription, ogni elemento presenta i seguenti campi :

- **requested_publish_interval**: definisce il publish interval della subscription in millisecondi;
- **requested_lifetime_count**: intero che indica quante volte il publishing interval può trascorrere senza che sia monitorata alcuna attività da parte del client. Passato questo lasso di tempo, il server cancella la Subscription e libera le risorse. **NOTA BENE: questo parametro dev’essere grande almeno tre volte il keep alive count;**
- **requested_max_keepalive_timer**: intero che indica quante volte il publishing interval deve trascorrere senza che sia disponibile alcuna Notifications da inviare al Client, perché il server mandi un keep-alive messagge al client in grado di comunicargli che quella particolare Subscription è ancora attiva;
- **max_notif_per_publish**: intero che indica il numero massimo di notifiche per ogni publish;
- **publishing_enabled**: booleano che abilità la pubblicazione dei messaggi prodotti dai monitored item;
- **priority**: intero che indica la priorità associata alla sottoscrizione;

Il campo **monitoring_info** è un array, ogni su elemento andrà ad indicare un oggetto che si vuole monitorare. Sono possibili due tipi di elementi in base al tipo di monitoring richiesto la disciriminazione avviene tramite il campo **monitoringMode**, che può assumere due valori : __monitored_item__ in questo caso l'elemento costituirà il monitored item che verrà creatonel meccanismo di sottoscrizione, __polling__ se si vuole monitorare il nodo con letture ad intervalli regolari.

Nel caso in venga settato **monitoringMode** con __monitored_item__ seguiranno i seguenti campi :

- **discplayName** : stringa che indica il nome della variabile da monitorare che verrà visualizzato collegandosi all'aggreagtion server;
- **client_handle** : intero che verrà utilizzato per associare il monitored item alla variabile nell'aggregation server e permetterne l'aggiornamento. Tale valore deve essere diverso per ogni monitored item e preferibilmente progressivo;
- **subIndex** : indice dell'array sub_info corrispondente alla sottoscrizione a cui si vuole associare il monitored item;
- **nodeTomonotor** : stringa contenente il nodeid del nodo da monitorare;
- **sampling_interval**: intero che indica l'intervallo di tempo in millisecondi con la quale vengono prodotte le notifiche dai monitored item e poste nella coda dei messaggi;
- **queue_size**: intero che indica la dimensione della coda dei monitored items;
- **discard_oldest**: booleano che definisce la politica di gestione dei messaggi quando la coda del monitored item è piena;
- **deadbandval**: valore da inserie in accordo al tipo di deadband voluta: se si sceglie la deadband percentuale bisogna inserire un numero compreso tra 0 e 100; se si sceglie invece la deadband assoluta bisogna mettere il valore che andrà a costituire la soglia;
- **deadbandtype**: permette di settare il tipo di dead band che verrà presa in considerazione dal datachange filter, come valore ammissibile ha **1** se vogliamo una dead band assoluta, **2** se vogliamo una deadband percentuale e **0** se vogliamo aggiornare continuamente la variabile ad ogni cambiamento di valore. Scegliere una dead band percentuale solo se si vuole monitorare un node analog.

Nel caso in venga settato **monitoringMode** con __polling__ seguiranno i seguenti campi :

- **nodeTomonotor** : stringa contenente il nodeid del nodo da monitorare,
- **refreshing_interval** : intero che rappresenta l'intervallo tempo in secondi che indica la periodicità della lettura e aggiornamento dei vlaori

A segurie un esempio di configurazione : 

```[json]
{
   "servers" : [{
        "serverName" : "Sample Server 1",
        "endpoint":"opc.tcp://pc-mario:51210/UA/SampleServer",
        "security_policy":"Basic128Rsa15",
        "security_mode":"SignAndEncrypt",
        "sub_infos": [
            {
                "requested_publish_interval": 2000,
                "requested_lifetime_count": 30000,
                "requested_max_keepalive_timer": 5000,
                "max_notif_per_publish": 2147483647,
                "publishing_enabled": true,
                "priority": 0
            },
            {
                "requested_publish_interval": 3000,
                "requested_lifetime_count": 30000,
                "requested_max_keepalive_timer": 5000,
                "max_notif_per_publish": 2147483647,
                "publishing_enabled": true,
                "priority": 0
            }
        ],
        "monitoring_info":[
            {
                "displayName": "Int64Value",
                "nodeTomonitor": "ns=2;i=11206",
                "monitoringMode": "polling", 
                "refreshing_interval": 2
            },
            {
                "displayName" : "Uint64Value",
                "client_handle" : 1
                "subIndex": 0,
                "nodeTomonitor": "ns=2;i=11212",
                "monitoringMode": "monitored_item", 
                "sampling_interval": 2000,
                "queue_size": 1,
                "discard_oldest": true,
                "deadbandval": 40,
                "deadbandtype": 2
            }
        ]
    }
    ]
}   
```
## Creazione Certificati
Per il corretto funzionamento dell’elaborato e per utilizzare i meccanismi di sicurezza offerti da OPC-UA è necessario creare i certificati di sicurezza x509v3 da posizionare all’interno della directory certificates del progetto. Per la creazione dei certificati è necessario aver installato openssl sulla propria macchina.

Bisogna posizionarsi all’interno del path di installazione di Openssl nella directory bin. Una volta situati in questo path “C:\Program Files\OpenSSL-Win64\bin”, bisogna creare un file di configurazione per openssl con la seguente struttura:

```[shell]
[ req ]
default_bits = 2048
default_md = sha256
distinguished_name = subject
req_extensions = req_ext
x509_extensions = req_ext
string_mask = utf8only
prompt = no
[ req_ext ]
basicConstraints = CA:FALSE
nsCertType = client, server
keyUsage = nonRepudiation, digitalSignature, keyEncipherment, dataEncipherment, keyCertSign
extendedKeyUsage= serverAuth, clientAuth
nsComment = "OpenSSL Generated Certificat"
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
subjectAltName = DNS: DESKTOP-V6N8M9J, IP: 127.0.0.1
[ subject ]
countryName = IT
stateOrProvinceName = CT
localityName = CT
organizationName = MyOrg
```

Importante inserire all’interno del campo DNS di subjectAltName il proprio hostname. Se non si conosce l’hostname della propria macchina basta digitare il comando hostname sul terminale.


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