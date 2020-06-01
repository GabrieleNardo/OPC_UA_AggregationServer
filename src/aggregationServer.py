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
    config_path = "..\\config\\config.json"
    certificate_path = "..\\certificates\\"
    # Server Setup
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

    # starting server
    server.start()
    
    # Import delle informazioni relative ai server da aggregare 
    print("-----------------------------------")
    print("Reading Configuration Information")
    print("-----------------------------------")
    config_file = open(config_path,"r")
    config_json = json.load(config_file)
    aggregated_server_1 = config_json['sample_server1']
    aggragated_server_2 = config_json['sample_server2']

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server Stopping...")
        print("-----------------------------------")
    finally:
        server.stop()