"""
File contenente l'implementazione del Client 
Realizzato da :
Nardo Gabriele Salvatore O55000430
Raiti Mario O55000434
"""

from opcua import ua , Client
from collections import Iterable
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
        self.client.name = "AggregationClient"
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



    def set_datachange_filter(self, deadband_val, deadbandtype=1):
        deadband_filter = ua.DataChangeFilter()
        deadband_filter.Trigger = ua.DataChangeTrigger(1)  # send notification when status or value change
        deadband_filter.DeadbandType = deadbandtype
        deadband_filter.DeadbandValue = deadband_val
        return deadband_filter



    def create_monitored_item(self, subscription, sub_nodes , sampling_interval, filter=None, queuesize = 0, discard_oldest = True, attr=ua.AttributeIds.Value):
        is_list = True
        if isinstance(sub_nodes, Iterable):
            nodes = list(sub_nodes)
        else:
            nodes = [nodes]
            is_list = False
        mirs = []
        for node in nodes:
            mir = self.make_monitored_item_request(subscription, node, attr, sampling_interval, filter, queuesize, discard_oldest)
            mirs.append(mir)

        mids = subscription.create_monitored_items(mirs)
        if is_list:
            return mids
        if type(mids[0]) == ua.StatusCode:
            mids[0].check()
        return mids[0]



    def make_monitored_item_request(self, subscription, node, attr, sampling_interval, filter, queuesize, discard_oldest):
        rv = ua.ReadValueId()
        rv.NodeId = node.nodeid
        rv.AttributeId = attr
        mparams = ua.MonitoringParameters()
        with subscription._lock:
            subscription._client_handle += 1
            mparams.ClientHandle = subscription._client_handle
        mparams.SamplingInterval = sampling_interval
        mparams.QueueSize = queuesize
        mparams.DiscardOldest = discard_oldest
        if filter:
            mparams.Filter = filter
        mir = ua.MonitoredItemCreateRequest()
        mir.ItemToMonitor = rv
        mir.MonitoringMode = ua.MonitoringMode.Reporting
        mir.RequestedParameters = mparams
        return mir



    def subscribe(self,node_ids, sub_infos, sub_info_ids, monitored_item_infos, monitored_item_info_ids):
            #Create the handlers
            handler = []
            for i in range(len(sub_infos)):
                handler.append(SubHandler(self.AggrObject))
            #Creating the subscriptions
            sub = []
            for i in range(len(sub_infos)):
                #Set sub parameters
                params = ua.CreateSubscriptionParameters()
                params.RequestedPublishingInterval = sub_infos['sub_info'+str(i+1)]['requested_publish_interval']
                params.RequestedLifetimeCount = sub_infos['sub_info'+str(i+1)]['requested_lifetime_count']
                params.RequestedMaxKeepAliveCount = sub_infos['sub_info'+str(i+1)]['requested_max_keepalive_timer']
                params.MaxNotificationsPerPublish = sub_infos['sub_info'+str(i+1)]['max_notif_per_publish']
                params.PublishingEnabled = sub_infos['sub_info'+str(i+1)]['publishing_enabled']
                params.Priority = sub_infos['sub_info'+str(i+1)]['priority']
                #Create the subscription
                sub.append(self.client.create_subscription(params, handler[i]))
            #node is the nodelist that we want to get the updated values
            node = [] 
            for node_id in node_ids.split(","):
                node.append(self.client.get_node(node_id))
            #deadband_monitor creates monitored items
            handle = []           
            sub_info_ids = sub_info_ids.split(",")
            monitored_item_info_ids = monitored_item_info_ids.split(",")
            split_nodes = [[[] for j in range(len(monitored_item_infos))] for i in range(len(sub_infos))]
            for i in range(len(sub_infos)):         #iterate on sub_infos
                for j in range(len(monitored_item_infos)):
                    filter = self.set_datachange_filter(monitored_item_infos['monitored_item_infos'+str(j+1)]['deadbandval'], monitored_item_infos['monitored_item_infos'+str(j+1)]['deadbandtype'])
                    for k in range(len(node)):
                        if ((int(sub_info_ids[k]) == (i+1)) and (int(monitored_item_info_ids[k]) == (j+1))):
                            split_nodes[i][j].append(node[k])
                    if (len(split_nodes[i][j]) > 0):  
                        handle.append(self.create_monitored_item(sub[i], split_nodes[i][j],  monitored_item_infos['monitored_item_infos'+str(j+1)]['sampling_interval'] , filter, monitored_item_infos['monitored_item_infos'+str(j+1)]['queue_size'], monitored_item_infos['monitored_item_infos'+str(j+1)]['discard_oldest'])) #handle = list of monitored items ids
            #handler.datachange_notification is called when a value of the monitored nodes has changed
            return sub, handle
    


    def unsubscribe(self, sub, handle):
       for i in range(len(sub)):
            for j in range(len(handle)):
                for mid in handle[j]:
                    try:
                        sub[i].unsubscribe(mid) #unsubscribe to data_change/events of the selected monitored items (handle -> list of monitored items ids)
                    except ua.uaerrors._auto.BadMonitoredItemIdInvalid: 
                        pass




    def delete_sub(self, sub):
        try:
            for i in range(len(sub)):
                sub[i].delete()
        except Exception:
            print("An Error was occured in client.delete function!")