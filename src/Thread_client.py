"""
File that contain Client Thread implementation, used to instantiate n client associated to the n servers to aggregate
Created by:
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
import Client
import threading
import time
from Thread_polling import PollingService

class ThreadClient(threading.Thread):

    #for each client, sample server conf, contain all the info of a single sample server (e.g. config.json -> sample_server1)
    def __init__(self , sample_server_conf , cert_path, AggrObject, handle_dict, polling_dict):
        threading.Thread.__init__(self)      
        self._stopper = threading.Event()  #used ih thread stopping
        self.sample_server_conf = sample_server_conf
        self.cert_path = cert_path
        self.AggrObject = AggrObject
        self.handle_dict = handle_dict
        self.polling_dict = polling_dict
     
    def stop(self): 
        self._stopper.set() #set stopper when the client thread is stopped
  
    def stopped(self): 
        return self._stopper.isSet() #check if the thread is stopped
    
    def run(self):
            #instantiate the Client. We pass cert path, the endpoint uri, security policy and security mode from sample server conf infos
            client = Client.Client_opc(self.cert_path , self.sample_server_conf['endpoint'], self.sample_server_conf['security_policy'] , self.sample_server_conf['security_mode'], self.AggrObject, self.handle_dict)
            client.client_instantiate()

            #creating secure channel, creating session, activate session
            client.secure_channel_and_session_activation()


            #Check the operation that we have to do from the configuration file
            #Polling operation -> we pass node ids,
            #Subscribe operation -> we pass node_ids, subscriptions infos and monitored items configuration infos
            monitored_nodes = []
            polling_nodes = []
            for i in range(len(self.sample_server_conf["monitoring_info"])):  
                if((self.sample_server_conf["monitoring_info"][i]["monitoringMode"]) == "monitored_item"):
                    monitored_nodes.append(self.sample_server_conf["monitoring_info"][i])
                if((self.sample_server_conf["monitoring_info"][i]["monitoringMode"]) == "polling"):
                    polling_nodes.append(self.sample_server_conf["monitoring_info"][i])
            
            if(len(monitored_nodes) > 0):
                sub, handle = client.subscribe(monitored_nodes,self.sample_server_conf["sub_infos"])
                
 
            if(len(polling_nodes) > 0):
                polling_threads = []
                for i in range(len(polling_nodes)):
                    polling_threads.append(PollingService(polling_nodes[i]["nodeTomonitor"],polling_nodes[i]["refreshing_interval"],client, self.polling_dict))
                    polling_threads[i].start()
            
            
            while True: 
                if self.stopped():  #Check if thread is stopped                
                    #if the request is subscribe, then we want to delete monitored items and delete subscribtions
                    if (len(monitored_nodes) > 0):
                        client.delete_sub(sub)
                    if(len(polling_nodes) > 0):
	                    for i in range(len(polling_nodes)):
		                    polling_threads[i].stop()
		                    polling_threads[i].join()
                    print("-----------------------------------")
                    print("Client Stopping...")
                    print("-----------------------------------")
                    client.disconnect() #close session, secure channel and disconnect
                    return
            
        