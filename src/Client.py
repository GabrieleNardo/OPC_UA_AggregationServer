"""
File that contains Client implementation 
Created by:
Nardo Gabriele Salvatore O55000430
Raiti Mario O55000434
"""

from opcua import ua , Client
from collections import Iterable
import time 



#This class is used to handle the datachange notifications
#OPC UA Python Stack specify to use  explicitly "datachange_notification" method and "event_notification" method to handle the notifications
class SubHandler(object):

    #We pass Aggr Object to updated our variables whan a datachange_notification is called
    def __init__(self, AggrObject):
        self.AggrObject = AggrObject

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        #Getting node id string to compare with properties of aggregated variables
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


    #istantiating Client calling "Client" constructor into stack opcua, set name and calling set_security_string method in the stack
    def client_instantiate(self):
        self.client = Client(self.server_path) #instaniate client
        self.client.name = "AggregationClient"
        if ((self.policy != "None") and (self.mode != "None")):
            #this method take a string as input that contains policy, mode, client certificate path and private key path. The endpoint that satisfies this characteristichs is choosed
            self.client.set_security_string(self.policy+","+self.mode+","+self.cert_path+"client_certificate.der,"+self.cert_path+"client_private_key.pem") #SecurityPolicy, Mode, Certificate path, Private key path


    #This method call the "connect" method in the stack. This method creates secure channel, create the session and activate it
    def secure_channel_and_session_activation(self):
        #params requested from the client. Server can set another value based on its requirements
        self.client.secure_channel_timeout = 10000
        self.client.session_timeout = 10000
        try:
            self.client.connect() #create secure channel and session; activate session
            print("Client instantiated; secure channel and session created; session activated ")
        except: 
            #if exception occures, disconnect the client
            self.client.disconnect()


    #This method disconnect the client from the server, closing session and secure channel
    def disconnect(self):
        self.client.disconnect()


    #This method is called when we want only to read Data
    def readData(self,node_ids):
        node = []
        values = []
        #Get nodes
        for node_id in node_ids.split(","):
            node.append(self.client.get_node(node_id)) #Client.py stack function
        #Get values
        for i in range(len(node)):
            values.append(node[i].get_data_value()) #Node.py stack function
        #Set readed values in the local variables
        AggrVar = self.AggrObject.get_variables()
        for i in range(len(AggrVar)):
           AggrVar[i].set_value(values[i])

    '''
    #This method is called when we want only to write Data
    def writeData(self,node_ids,new_values):
        node = []
        new_vals = []
        #Get nodes
        for node_id in node_ids.split(","):
            node.append(self.client.get_node(node_id)) #Client.py stack function
        #Get values from configuration file
        for val in new_values.split(","):
            new_vals.append(val)
        #Set new values in local variables
        AggrVar = self.AggrObject.get_variables()
        for i in range(len(AggrVar)):
           AggrVar[i].set_value(new_vals[i])
        #Set new values in the sample server
        for i in range(len(node)):
           node[i].set_value(new_vals[i]) #Node.py stack function
    '''

    '''This method is our stack method revisitation to set our parameter values'''
    #This method is used in the "subscribe" method to create the filter for making the monitored item request
    def set_datachange_filter(self, deadband_val, deadbandtype=1):
        deadband_filter = ua.DataChangeFilter()
        deadband_filter.Trigger = ua.DataChangeTrigger(1)  # send notification when status or value change
        deadband_filter.DeadbandType = deadbandtype #type = 0 -> notification every change; type = 1 -> absolute deadband_val is considered; type = 2 -> percent deadband_val is considered
        deadband_filter.DeadbandValue = deadband_val
        return deadband_filter


    '''This method is our stack method revisitation to set our parameter values'''
    #This method is called in the "subscribe" method for creating the monitored items for the nodes passed. 
    def create_monitored_item(self, subscription, sub_nodes , sampling_interval, filter=None, queuesize = 0, discard_oldest = True, attr=ua.AttributeIds.Value):
        is_list = True
        if isinstance(sub_nodes, Iterable):
            nodes = list(sub_nodes)
        else:
            nodes = [nodes]
            is_list = False
        mirs = []
        for node in nodes:
            mir = self.make_monitored_item_request(subscription, node, attr, sampling_interval, filter, queuesize, discard_oldest) #making monitored item request
            mirs.append(mir)

        mids = subscription.create_monitored_items(mirs)
        if is_list:
            return mids
        if type(mids[0]) == ua.StatusCode:
            mids[0].check()
        return mids[0] #return a list of handles (monitored item ids)


    '''This method is our stack method revisitation to set our parameter values'''
    #This method sets our params obtained from the conf file and make the monitored item request
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
        mir = ua.MonitoredItemCreateRequest() #stack request
        mir.ItemToMonitor = rv
        mir.MonitoringMode = ua.MonitoringMode.Reporting
        mir.RequestedParameters = mparams
        return mir


    #This method is called when we want only to subscribe to Data. It takes as input sub infos and mon_item infos from conf file
    def subscribe(self,node_ids, sub_infos, sub_info_ids, monitored_item_infos, monitored_item_info_ids):
            #Create the handlers
            handler = []
            for i in range(len(sub_infos)):
                handler.append(SubHandler(self.AggrObject))
            #Creating a subscription for ech 'sub_infos' element in the config file (different types of subscriptions -> different parameters)
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
            #handle will contains mon_item_ids
            handle = []
            #sub_info_ids is used to associate each node to each type of subscription configuration (positional way)          
            sub_info_ids = sub_info_ids.split(",")
            #monitored_item_info_ids is used to associate each node to each type of monitored_item configuration (positional way)
            monitored_item_info_ids = monitored_item_info_ids.split(",")
            #split_nodes will contains all nodes splitted for subscriptions configuration and monitored item configuration for each subscription conf
            split_nodes = [[[] for j in range(len(monitored_item_infos))] for i in range(len(sub_infos))]
            for i in range(len(sub_infos)):         #iterate on sub_infos
                for j in range(len(monitored_item_infos)): 
                    filter = self.set_datachange_filter(monitored_item_infos['monitored_item_infos'+str(j+1)]['deadbandval'], monitored_item_infos['monitored_item_infos'+str(j+1)]['deadbandtype']) #Set filter from config parameters setted in the config file
                    for k in range(len(node)):
                        if ((int(sub_info_ids[k]) == (i+1)) and (int(monitored_item_info_ids[k]) == (j+1))):
                            split_nodes[i][j].append(node[k])
                    if (len(split_nodes[i][j]) > 0):  #for each subscription config and monitored item config, if len of split_nodes is > 0 (noedes are appended), create monitored items for that nodes
                        handle.append(self.create_monitored_item(sub[i], split_nodes[i][j],  monitored_item_infos['monitored_item_infos'+str(j+1)]['sampling_interval'] , filter, monitored_item_infos['monitored_item_infos'+str(j+1)]['queue_size'], monitored_item_infos['monitored_item_infos'+str(j+1)]['discard_oldest'])) #handle = list of monitored items ids
            #handler.datachange_notification is called when a value of the monitored nodes has changed
            return sub, handle
    

    #This method take as input the subscription list and handle list of monitored items that we want to delete
    def delete_monit_items(self, sub, handle):
       for i in range(len(sub)):
            for j in range(len(handle)):
                for mid in handle[j]:
                    try:
                        #stack function called on the subscription
                        sub[i].unsubscribe(mid) #unsubscribe to data_change/events of the selected monitored items (handle -> list of monitored items ids)
                    except ua.uaerrors._auto.BadMonitoredItemIdInvalid: 
                        #This except is added because we call the unsubscribe stack method (delete monitored_item) for every subscription, but the monitored item is present only in one of them
                        #So, in the other subscriptions, the BadMonitoredItemInvalid is raised, but we want to ignore this error
                        pass



    #This method takes as input the subscriptions list and delete them
    def delete_sub(self, sub):
        try:
            for i in range(len(sub)):
                sub[i].delete() #Stack method call on the subscription(this method delete every monitored item in the subscription and delete the subscription)
        except Exception:
            print("An Error was occured in client.delete function!")