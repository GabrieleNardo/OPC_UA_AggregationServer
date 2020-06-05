"""
File contenente l'implementazione del Client 
Realizzato da :
Nardo Gabriele Salvatore O55000430
Raiti Mario O55000434
"""

from opcua import ua , Client
import time 

class Client_opc():

    def __init__(self, cert_path, server_path, policy, mode):
        self.cert_path = cert_path #certificates path
        self.server_path = server_path
        self.policy = policy
        self.mode = mode

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
        client.secure_channel_timeout = 10000
        client.session_timeout = 10000
        try:
            self.client.connect() #create secure channel and session; activate session
            print("Client instantiated; secure channel and session created; session activated ")
        except: 
            self.client.disconnect()

    def readData(self,node_id):
        node = client.get_node(node_id)
        var = node.get_data_value()
        return var
    
    def writeData(self,node_id,new_value):
        node = client.get_node(node_id)
        node.set_value(new_value)
        return

    def subscribe(self,node_id,pub_int):
        # inserire implementazione della subscription
        return

""" Test Client
if __name__ == "__main__":
    client = Client("opc.tcp://pc-mario:51210/UA/SampleServer")
    #client.set_security_string("Basic128Rsa15,SignAndEncrypt,.\certificates\client_certificate.der,.\certificates\client_private_key.pem")
    try:
        client.connect()
        while True:
          
    except KeyboardInterrupt:
        print("Client Stopping...")
    finally:
        client.disconnect()
"""