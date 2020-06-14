"""
File that contain Client Thread implementation, used to instantiate n client associated to the n servers to aggregate
Created by:
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
import Client
import threading 

class ThreadClient(threading.Thread):

    #for each client, sample server conf, contain all the info of a single sample server (e.g. config.json -> sample_server1)
    def __init__(self , sample_server_conf , cert_path, AggrObject):
        threading.Thread.__init__(self)      
        self._stopper = threading.Event()  #used ih thread stopping
        self.sample_server_conf = sample_server_conf
        self.cert_path = cert_path
        self.AggrObject = AggrObject
     
    def stop(self): 
        self._stopper.set() #set stopper when the client thread is stopped
  
    def stopped(self): 
        return self._stopper.isSet() #check if the thread is stopped
    
    def run(self):
            #instantiate the Client. We pass cert path, the endpoint uri, security policy and security mode from sample server conf infos
            client = Client.Client_opc(self.cert_path , self.sample_server_conf['endpoint'], self.sample_server_conf['security_policy'] , self.sample_server_conf['security_mode'], self.AggrObject)
            client.client_instantiate()

            #creating secure channel, creating session, activate session
            client.secure_channel_and_session_activation()

            #Check the operation that we have to do from the configuration file
            #Read operation -> we pass node ids
            if (self.sample_server_conf['service_req'] == "read"):
                client.readData(self.sample_server_conf['node_ids'])
                
            #Subscribe operation -> we pass node_ids, subscriptions infos and monitored items configuration infos
            if (self.sample_server_conf['service_req'] == "subscribe"):
                sub, handle = client.subscribe(self.sample_server_conf['node_ids'],self.sample_server_conf['sub_infos'], self.sample_server_conf['sub_info_ids'], self.sample_server_conf['monitored_item_infos'], self.sample_server_conf['monitored_item_info_ids'])

            #Write operation -> we pass node_ids and new values to write
            if (self.sample_server_conf['service_req'] == "write"):
                client.writeData(self.sample_server_conf['node_ids'],self.sample_server_conf['write_info']['new_value'])
                
                
            while True: 
                if self.stopped():  #Check if thread is stopped                
                    print("Client Stopping...")
                    #if the request is subscribe, then we want to delete monitored items and delete subscribtions
                    if (self.sample_server_conf['service_req'] == "subscribe"):
                        client.delete_monit_items(sub, handle)
                        client.delete_sub(sub)
                    client.disconnect() #close session, secure channel and disconnect
                    return
            
        