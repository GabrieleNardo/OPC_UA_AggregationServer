"""
File Principale Contenente L'implementazione dell Aggregation Server 
Realizzato da :
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
import opcua
import json # per caricare le configurazioni dal file json

# Import delle informazioni relative ai server da aggregare 
print("Reading Configuration Information")
print("-------------------------------")
config_path = "..\\config\\config.json"
config_file = open(config_path,"r")
config_json = json.load(config_file)
print(config_json)


print("Codice in Arrivo...")