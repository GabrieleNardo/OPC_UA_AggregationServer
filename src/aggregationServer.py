"""
File Principale Contenente L'implementazione dell Aggregation Server 
Realizzato da :
Raiti Mario O55000434
Nardo Gabriele Salvatore O55000430
"""
import opcua
import json # per caricare le configurazioni dal file json

with open("./config/json.items") as json_file:
        json_config = json.load(json_file)


print("Codice in Arrivo...")