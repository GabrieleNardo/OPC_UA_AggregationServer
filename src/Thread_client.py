"""
File contenente l'implementazione del Thread che verrà invocato per la creazione 
dei client associati agli n server da aggreagre
Realizzato da :
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
import Client
import threading 

class ThreadClient(threading.Thread):

    """ il parametro sample_server_conf sarà un elemento tra quelli letti 
        dal file di configurazione 
    """
    def __init__(self , sample_server_conf , cert_path):
        threading.Thread.__init__(self)
        self._stop = threading.Event() 
        self.sample_server_conf = sample_server_conf
        self.cert_path = cert_path
     
    def stop(self): 
        self._stop.set() 
  
    def stopped(self): 
        return self._stop.isSet() 
    
    def run(self):
            client = Client.Client_opc(self.cert_path , self.sample_server_conf['endpoint'], self.sample_server_conf['security_policy'] , self.sample_server_conf['security_mode'])
            client.client_instantiate()
            client.secure_channel_and_session_connection()

            if (self.sample_server_conf['service_req'] == "read"):
                readed_value = client.readData(self.sample_server_conf['node_id'])
                print(readed_value)
                # implementare aggiornamento dei valore del server

            if (self.sample_server_conf['service_req'] == "subscribe"):
                client.subscribe(self.sample_server_conf['node_id'],self.sample_server_conf['publish_interval'])
                # implementare aggiornamento dei valore del server
                
            while True: 
                if self.stopped(): 
                    print("Client Stopping...")
                    client.disconnect()
                    return
            
        