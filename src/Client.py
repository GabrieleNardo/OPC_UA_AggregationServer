"""
File that contains Client implementation 
Created by:
Nardo Gabriele Salvatore O55000430
Raiti Mario O55000434
"""

from opcua import ua , Client
from collections.abc import Iterable

#This class is used to handle the datachange notifications
#OPC UA Python Stack specify to use  explicitly "datachange_notification" method to handle the notifications
class SubHandler(object):

    #We pass Aggr Object to updated our variables whan a datachange_notification is called
    def __init__(self, AggrObject, handle_dict):
        self.AggrObject = AggrObject
        self.handle_dict = handle_dict

    def datachange_notification(self, node, val, data):
        print("Subscription Service: New data change event:", data.monitored_item.ClientHandle, val, node)
        #Set the recived value in the local variables 
        AggrVar = self.AggrObject.get_variables()
        for var in AggrVar: 
            for key in self.handle_dict:
                 if(self.handle_dict[key] == data.monitored_item.ClientHandle and str(var.nodeid) == key):
                    var.set_value(data.monitored_item.Value)

class Client_opc():

    def __init__(self, cert_path, server_path, policy, mode, AggrObject, handle_dict):
        self.cert_path = cert_path #certificates path
        self.server_path = server_path
        self.policy = policy
        self.mode = mode
        self.AggrObject = AggrObject
        self.handle_dict = handle_dict


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
    def readData(self,node_id, polling_dict):
        #Get node
        node = self.client.get_node(node_id) #Client.py stack function
        #Get values
        value = node.get_data_value() #Node.py stack function
        print(f"Polling Service readed value : {value} ")
        #Set readed values in the local variables
        AggrVar = self.AggrObject.get_variables()
        for var in AggrVar: 
            for key in polling_dict:
                remote_node = self.client.get_node(polling_dict[key])
                if(remote_node == node and str(var.nodeid) == key):
                    var.set_value(value)
                    

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
    def create_monitored_item(self, subscription, nodes , sampling_interval, client_handle, filter=None, queuesize = 0, discard_oldest = True, attr=ua.AttributeIds.Value):
        is_list = True
        if isinstance(nodes, Iterable):
            nodes = list(nodes)
        else:
            nodes = [nodes]
            is_list = False
        mirs = []
        for node in nodes:
            mir = self.make_monitored_item_request(subscription, node, attr, sampling_interval, client_handle, filter, queuesize, discard_oldest) #making monitored item request
            mirs.append(mir)

        mids = subscription.create_monitored_items(mirs)
        if is_list:
            return mids
        if type(mids[0]) == ua.StatusCode:
            mids[0].check()
        return mids[0] #return a list of handles (monitored item ids)


    '''This method is our stack method revisitation to set our parameter values'''
    #This method sets our params obtained from the conf file and make the monitored item request
    def make_monitored_item_request(self, subscription, node, attr, sampling_interval, client_handle, filter, queuesize, discard_oldest):
        rv = ua.ReadValueId()
        rv.NodeId = node.nodeid
        rv.AttributeId = attr
        mparams = ua.MonitoringParameters()
        with subscription._lock:
            subscription._client_handle = client_handle
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
    def subscribe(self, monitored_nodes, sub_infos):
            #Create the handlers
            handler = []
            for i in range(len(sub_infos)):
                handler.append(SubHandler(self.AggrObject, self.handle_dict))
            #Creating a subscription for ech 'sub_infos' element in the config file (different types of subscriptions -> different parameters)
            sub = []
            sub_index_list = []
            for i in range(len(monitored_nodes)):
                sub_index_list.append(monitored_nodes[i]["subIndex"])
            for i in range(len(sub_infos)):
                if(i in sub_index_list):
                    #Set sub parameters
                    params = ua.CreateSubscriptionParameters()
                    params.RequestedPublishingInterval = sub_infos[i]['requested_publish_interval']
                    params.RequestedLifetimeCount = sub_infos[i]['requested_lifetime_count']
                    params.RequestedMaxKeepAliveCount = sub_infos[i]['requested_max_keepalive_timer']
                    params.MaxNotificationsPerPublish = sub_infos[i]['max_notif_per_publish']
                    params.PublishingEnabled = sub_infos[i]['publishing_enabled']
                    params.Priority = sub_infos[i]['priority']
                    #Create the subscription
                    sub.append(self.client.create_subscription(params, handler[i]))
            #handle will contains mon_item_ids 
            handle = []
            Aggr_key = []
            for key in self.handle_dict:
                Aggr_key.append(key)
            for i in range(len(monitored_nodes)):                     
                filter = self.set_datachange_filter(monitored_nodes[i]['deadbandval'], monitored_nodes[i]['deadbandtype']) #Set filter from config parameters setted in the config file
                handle.append(self.create_monitored_item(sub[monitored_nodes[i]['subIndex']], self.client.get_node(monitored_nodes[i]['nodeTomonitor']),  monitored_nodes[i]['sampling_interval'] ,self.handle_dict[Aggr_key[i]], filter, monitored_nodes[i]['queue_size'], monitored_nodes[i]['discard_oldest'])) #handle = list of monitored items ids
            #handler.datachange_notification is called when a value of the monitored nodes has changed
            return sub, handle
    

    #This method take as input the subscription list and handle list of monitored items that we want to delete
    def delete_monit_items(self, sub, handle):
       for i in range(len(sub)):
            for mid in handle:
                try:
                    #stack function called on the subscription
                    sub[i].unsubscribe(mid) #unsubscribe to data_change/events of the selected monitored items (handle -> list of monitored items ids)
                except ua.uaerrors._auto.BadMonitoredItemIdInvalid: 
                    #This except is added because we call the unsubscribe stack method (delete monitored_item) for every subscription, but the monitored item is present only in one of them                        #So, in the other subscriptions, the BadMonitoredItemInvalid is raised, but we want to ignore this error
                    pass
    


    #This method takes as input the subscriptions list and delete them
    def delete_sub(self, sub):
        try:
            for i in range(len(sub)):
                sub[i].delete() #Stack method call on the subscription(this method delete every monitored item in the subscription and delete the subscription)
        except Exception:
            print("An Error was occured in client.delete function!")