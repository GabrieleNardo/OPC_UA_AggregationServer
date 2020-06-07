"""
File contenente l'implementazione del Client 
Realizzato da :
Nardo Gabriele Salvatore O55000430
Raiti Mario O55000434
"""

from opcua import ua , Client
import time 

class SubHandler(object):

    def __init__(self, AggrObject):
        self.AggrObject = AggrObject

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, data.monitored_item.Value.ServerTimestamp, val)
        AggrVar = self.AggrObject.get_variables()
        for i in range(len(AggrVar)):
           AggrVar[i].set_value(data.monitored_item.Value)

    def event_notification(self, event):
        print("Python: New event", event)

class Client_opc():

    def __init__(self, cert_path, server_path, policy, mode, AggrObject):
        self.cert_path = cert_path #certificates path
        self.server_path = server_path
        self.policy = policy
        self.mode = mode
        self.AggrObject = AggrObject

    def client_instantiate(self):
        self.client = Client(self.server_path) #instaniate client
        if ((self.policy != "None") and (self.mode != "None")):
            self.client.set_security_string(self.policy+","+self.mode+","+self.cert_path+"client_certificate.der,"+self.cert_path+"client_private_key.pem") #SecurityPolicy, Mode, Certificate path, Private key path

    '''def get_endp(self):
        self.endp = self.client.get_endpoints()
        print("Endpoint disponibili: \n")
        print(self.endp)
        return self.endp'''

    def secure_channel_and_session_connection(self):
        self.client.secure_channel_timeout = 10000
        self.client.session_timeout = 10000
        try:
            self.client.connect() #create secure channel and session; activate session
            print("Client instantiated; secure channel and session created; session activated ")
        except: 
            self.client.disconnect()
            
    def disconnect(self):
        self.client.disconnect()

    def readData(self,node_ids):
        node = []
        values = []
        #Get nodes
        for node_id in node_ids.split(","):
            node.append(self.client.get_node(node_id))
        #Get values
        for i in range(len(node)):
            values.append(node[i].get_data_value())
        #Set readed values in the local variables
        AggrVar = self.AggrObject.get_variables()
        for i in range(len(AggrVar)):
           AggrVar[i].set_value(values[i])

    
    def writeData(self,node_ids,new_values):
        node = []
        new_vals = []
        #Get nodes
        for node_id in node_ids.split(","):
            node.append(self.client.get_node(node_id))
        #Get values
        for val in new_values.split(","):
            new_vals.append(val)
        #Set new values in local variables
        AggrVar = self.AggrObject.get_variables()
        for i in range(len(AggrVar)):
           AggrVar[i].set_value(new_vals[i])
        #Set new values in the sample server
        for i in range(len(node)):
           node[i].set_value(new_vals[i]) 

    def subscribe(self,node_ids,pub_interval):
        #Create the handler
        handler = SubHandler(self.AggrObject)
        node = [] 
        #Creating the subscription
        sub = self.client.create_subscription(pub_interval, handler)
        #node is the nodelist that we want to get the updated values
        for node_id in node_ids.split(","):
            node.append(self.client.get_node(node_id))
        #subscribe_data_change creates monitored items
        handle = sub.subscribe_data_change(node) #handle = list of monitored items ids
        
        #handler.datachange_notification is called when a value of the monitored nodes has changed
        return sub, handle
    
    def unsubscribe(self, sub, handle):
        for mid in handle:
            sub.unsubscribe(mid) #unsubscribe to data_change/events of the selected monitored items (handle -> list of monitored items ids)

    def delete_sub(self, sub):
        sub.delete()


""" Test Client
if __name__ == "__main__":
    client = Client("opc.tcp://pc-mario:51210/UA/SampleServer")
    #client.set_security_string("Basic128Rsa15,SignAndEncrypt,.\\certificates\\client_certificate.der,.\\certificates\\client_private_key.pem")
    try:
        client.connect()
        while True:
          
    except KeyboardInterrupt:
        print("Client Stopping...")
    finally:
        client.disconnect()
"""