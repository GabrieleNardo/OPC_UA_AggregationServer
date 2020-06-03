"""
File Principale Contenente L'implementazione dell Aggregation Server 
Realizzato da :
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
from opcua import ua, Client, Server
import json # per caricare le configurazioni dal file json
import time 

if __name__ == "__main__":
    #Path settings
    config_path = ".\config\\"
    certificate_path = ".\certificates\\"

    # import aggregation server configuration info  
    print("-----------------------------------")
    print("Loading Configuration Information")
    print("-----------------------------------")
    config_file = open(config_path + "config.json","r")
    config_json = json.load(config_file)

    aggr_servers = [] #sample servers informaion list
    for key in config_json:
        aggr_servers.append(config_json[key])

    print(aggr_servers)    

    sec_config_file = open(config_path + "openssl_conf.json","r")
    sec_config_json = json.load(sec_config_file)

    # Server Setup endpoint and security policy
    server = Server()
    server.set_endpoint("opc.tcp://127.0.0.1:8000/AggregationServer/")

    server.set_security_policy([ua.SecurityPolicyType.NoSecurity,
                            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                            ua.SecurityPolicyType.Basic256Sha256_Sign])

    # load server certificate and private key. This enables endpoints
    server.load_certificate(certificate_path + "server_certificate.der")
    server.load_private_key(certificate_path + "server_private_key.pem")
    
    # Setup our namespace
    uri = "http://Aggregation.Server.opcua"
    idx = server.register_namespace(uri)
  
    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()

    # populate our namespace with the aggreagated element adn their variables
    aggregator = objects.add_folder(idx, "Aggregator")
 
    # definition of our custom object type AggregatedServer
    types = server.get_node(ua.ObjectIds.BaseObjectType)
    mycustomobj_type = types.add_object_type(idx, "AggregatedServerType")
    var = mycustomobj_type.add_variable(idx, "AggregaterdVariable", 0)
    var.set_writable()
    var.set_modelling_rule(True)    

    aggregatedServers_objects = [] #aggregated servers objects list
    for i in range(len(aggr_servers)):
        aggregatedServers_objects.append(aggregator.add_object(idx,"AggregatedServer_"+str(i+1), mycustomobj_type.nodeid))

    print(aggregatedServers_objects)


    # starting server
    server.start()
    print("Available Endpoint for connection : opc.tcp://127.0.0.1:8000/AggregationServer/")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server Stopping...")
        print("-----------------------------------")
    finally:
        server.stop()