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
        print("Python: New data change event", node, val)
        #Getting node_id string to compare with properties of aggregated variables
        node_str = "ns="+str(node.nodeid.NamespaceIndex)+";i="+str(node.nodeid.Identifier)
        AggrVar = self.AggrObject.get_variables()
        for i in range(len(AggrVar)):
            value = AggrVar[i].get_properties()
            if(value[0].get_data_value().Value.Value == node_str):
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

    def subscribe(self,node_ids, sub_infos, sub_info_ids):
        #Create the handlers
        #try:
            handler = []
            for i in range(len(sub_infos)):
                handler.append(SubHandler(self.AggrObject))
            node = [] 
            sub = []
            #Creating the subscription
            for i in range(len(sub_infos)):
                params = ua.CreateSubscriptionParameters()
                params.RequestedPublishingInterval = sub_infos['sub_info'+str(i+1)]['requested_publish_interval']
                params.RequestedLifetimeCount = sub_infos['sub_info'+str(i+1)]['requested_lifetime_count']
                params.RequestedMaxKeepAliveCount = sub_infos['sub_info'+str(i+1)]['requested_max_keepalive_timer']
                params.MaxNotificationsPerPublish = sub_infos['sub_info'+str(i+1)]['max_notif_per_publish']
                params.PublishingEnabled = sub_infos['sub_info'+str(i+1)]['publishing_enabled']
                params.Priority = sub_infos['sub_info'+str(i+1)]['priority']
                sub.append(self.client.create_subscription(params, handler[i]))
            #node is the nodelist that we want to get the updated values
            for node_id in node_ids.split(","):
                node.append(self.client.get_node(node_id))
            #deadband_monitor creates monitored items
            handle = []
            sub_info_ids = sub_info_ids.split(",")
            for i in range(len(sub_infos)):         #iterate on sub_infos
                sub_node = []                       #sub_node will contain the nodes that we want to subscribe with the same sub parameters                      
                for j in range(len(node)):          #iterate on the number on nodes             
                    if(int(sub_info_ids[j]) == (i+1)):   #if ids are the same, append that node for that subscription
                        sub_node.append(node[j])
                handle.append(sub[i].deadband_monitor(sub_node, sub_infos['sub_info'+str(i+1)]['deadbandval'], sub_infos['sub_info'+str(i+1)]['deadbandtype'], sub_infos['sub_info'+str(i+1)]['queue_size'])) #handle = list of monitored items ids
        #except Exception:
        #handler.datachange_notification is called when a value of the monitored nodes has changed
            return sub, handle
    
    def unsubscribe(self, sub, handle):
        try:
            for i in range(len(handle)):
                for mid in handle[i]:
                    sub[i].unsubscribe(mid) #unsubscribe to data_change/events of the selected monitored items (handle -> list of monitored items ids)
        except Exception:
            print("An Error was occured in client.unsubscribe function!")

    def delete_sub(self, sub):
        try:
            for i in range(len(sub)):
                sub[i].delete()
        except Exception:
            print("An Error was occured in client.delete function!")