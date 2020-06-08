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
    def __init__(self , sample_server_conf , cert_path, AggrObject):
        threading.Thread.__init__(self)
        self._stropper = threading.Event() 
        self.sample_server_conf = sample_server_conf
        self.cert_path = cert_path
        self.AggrObject = AggrObject
     
    def stop(self): 
        self._stropper.set() 
  
    def stopped(self): 
        return self._stropper.isSet() 
    
    def run(self):
            client = Client.Client_opc(self.cert_path , self.sample_server_conf['endpoint'], self.sample_server_conf['security_policy'] , self.sample_server_conf['security_mode'], self.AggrObject)
            client.client_instantiate()
            client.secure_channel_and_session_connection()

            if (self.sample_server_conf['service_req'] == "read"):
                client.readData(self.sample_server_conf['node_id'])
                

            if (self.sample_server_conf['service_req'] == "subscribe"):
                sub, handle = client.subscribe(self.sample_server_conf['node_id'],self.sample_server_conf['sub_info'])

            if (self.sample_server_conf['service_req'] == "write"):
                client.writeData(self.sample_server_conf['node_id'],self.sample_server_conf['write_info']['new_value'])
                
                
            while True: 
                if self.stopped():                  
                    print("Client Stopping...")
                    if (self.sample_server_conf['service_req'] == "subscribe"):
                        client.unsubscribe(sub, handle)
                        client.delete_sub(sub)
                    client.disconnect()
                    return
            
        