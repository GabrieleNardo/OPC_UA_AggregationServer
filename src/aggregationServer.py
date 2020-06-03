"""
File Principale Contenente L'implementazione dell Aggregation Server 
Realizzato da :
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
from opcua import ua, Server, Client
import json # per caricare le configurazioni dal file json
import time 

if __name__ == "__main__":
    #Path settings
    config_path = "..\\config\\"
    certificate_path = "..\\certificates\\"

    # Import delle informazioni relative ai server da aggregare e alla sicurezza 
    print("-----------------------------------")
    print("Loading Configuration Information")
    print("-----------------------------------")
    config_file = open(config_path + "config.json","r")
    config_json = json.load(config_file)
    aggregated_server_1 = config_json['sample_server1']
    aggragated_server_2 = config_json['sample_server2']

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

    aggregatedServer_1 = aggregator.add_object(idx,"AggregatedServer_1")
    aggraegated_var_1 = aggregatedServer_1.add_variable(idx, "AggregatedVariable", 0)
    aggraegated_var_1.set_writable()

    aggregatedServer_2 = aggregator.add_object(idx,"AggregatedServer_2")
    aggraegated_var_2 = aggregatedServer_2.add_variable(idx, "AggregatedVariable", 0)
    aggraegated_var_2.set_writable()

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