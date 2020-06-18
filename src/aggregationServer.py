"""
Main file that contain the implementation of the Aggregation Server 
Created by:
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
from opcua import ua, Client, Server
import json # per caricare le configurazioni dal file json
import time
from Thread_client import ThreadClient

if __name__ == "__main__":
    #Path settings
    #Path Config json file
    config_path = ".\\config\\"
    #Path to certificates files
    certificate_path = ".\\certificates\\"

    # import aggregation server configuration infos file  
    print("-----------------------------------")
    print("Loading Configuration Information")
    print("-----------------------------------")
    config_file = open(config_path + "config.json","r")
    config_json = json.load(config_file)

    aggr_servers = [] #each element will contain sample servers informaion list
    for i in range(len(config_json["servers"])):
        aggr_servers.append(config_json["servers"][i])
    
    # Server Setup endpoint and security policy settings
    server = Server()
    server.name = "AggregationServer"
    server.set_endpoint("opc.tcp://127.0.0.1:8000/AggregationServer/")

    server.set_security_policy([ua.SecurityPolicyType.NoSecurity,
                            ua.SecurityPolicyType.Basic128Rsa15_Sign,
                            ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
                            ua.SecurityPolicyType.Basic256_Sign,
                            ua.SecurityPolicyType.Basic256_SignAndEncrypt,
                            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                            ua.SecurityPolicyType.Basic256Sha256_Sign])

    # load server certificate and private key. This enables endpoints
    server.load_certificate(certificate_path + "server_certificate.der")
    server.load_private_key(certificate_path + "server_private_key.pem")
    
    # Setup our namespace
    uri = "http://Aggregation.Server.opcua"
    #Getting the index of our nasmespace
    idx = server.register_namespace(uri)
  
    # get Objects node. This is where we should put our custom stuff
    objects = server.get_objects_node()

    # populate our namespace with the aggreagated element and their variables
    aggregator = objects.add_folder(idx, "Aggregated Servers")
 
    # definition of our custom object type -> AggregatedServer
    types = server.get_node(ua.ObjectIds.BaseObjectType)
    mycustomobj_type = types.add_object_type(idx, "AggregatedServerType") 
    mycustomobj_type.set_modelling_rule(True)    

    # each element of the node_ids list contains the node ids of the nodes that we want to monitor on a single sample server
    #This list is useful when populating object tree
    c_handles = [[] for i in range(len(aggr_servers))]
    node_ids = [[] for i in range(len(aggr_servers))]
    for i in range(len(aggr_servers)):
        for j in range(len(aggr_servers[i]["monitoring_info"])):
            node_ids[i].append(aggr_servers[i]["monitoring_info"][j]["nodeTomonitor"])
            if(aggr_servers[i]["monitoring_info"][j]["monitoringMode"] == "monitored_item"):
                c_handles[i].append(aggr_servers[i]["monitoring_info"][j]["client_handle"])

    #Populating the object tree with our custom object type and variables that will contain the values that we want to monitor. 
    #Added also a property for each variable, that will contain the node id of the node in the sample server that we want to obtain values
    var_node_ids = [[] for i in range(len(aggr_servers))]
    polling_dict = [{} for i in range(len(aggr_servers))]
    aggregatedServers_objects = [] #aggregated servers objects list
    for i in range(len(aggr_servers)):
        obj = aggregator.add_object(idx,aggr_servers[i]["serverName"], mycustomobj_type.nodeid)
        obj.add_property(idx, "Remote URL Server", aggr_servers[i]["endpoint"])
        for j in range(len(node_ids[i])):
            var = obj.add_variable(idx,aggr_servers[i]["monitoring_info"][j]["displayName"], 0)
            if(aggr_servers[i]["monitoring_info"][j]["monitoringMode"] == "monitored_item"):
                var_node_ids[i].append(var.nodeid)
            if(aggr_servers[i]["monitoring_info"][j]["monitoringMode"] == "polling"):
                polling_dict[i][str(var.nodeid)] = (node_ids[i][j])
            var.add_property(idx, "Remote NodeId", node_ids[i][j])
            var.set_writable()           
        aggregatedServers_objects.append(obj)


    #Creating dictionary of client_handles and node_ids
    handle_dict = [{} for i in range(len(aggr_servers))]
    for i in range(len(aggr_servers)):
        for j in range(len(c_handles[i])):
                handle_dict[i][str((var_node_ids[i][j]))] = (c_handles[i][j])

    # starting server
    server.start()
    print("Available Endpoint for connection : opc.tcp://127.0.0.1:8000/AggregationServer/")
    print("Press Ctrl + C to stop the server...")
    

    # Creating a Client thread for each Server
    clients_threads = []
    for i in  range(len(aggr_servers)):
        #We pass to the ThreadClient the conf of a sample server, cert path, AggregatedServer object that cointains the variable to monitor in that sample server and translation dictionary
        clients_threads.append(ThreadClient(aggr_servers[i],certificate_path, aggregatedServers_objects[i], handle_dict[i], polling_dict[i]))
    
    for i in range(len(clients_threads)):
        print("-----------------------------------")
        print(f"Thread {i} started..")
        clients_threads[i].start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt: #Ctrl + C
        #Stopping the client threads and joining them before stopping the Aggregation server
        for i in range(len(clients_threads)):
            clients_threads[i].stop()
            clients_threads[i].join()
    finally:
        print("-----------------------------------")
        print("Server Stopping...")
        print("-----------------------------------")
        server.stop()



    #ns=2;i=11212,ns=2;i=11206,ns=2;i=11224 UINT 64, INT 64, DOUBLE (Analog)
    #ns=2;i=11200,ns=2;i=11194  UINT 32, INT 32 (Analog)