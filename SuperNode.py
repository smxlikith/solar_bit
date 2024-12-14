import threading
import json
import os
import socket

class SuperNode:
    def __init__(self):
        self.id = "serverid"
        self.hashTable = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 8191))
        self.STATE = "KA"
        self.DIST = "BNG"
        self.LOCL = "YES"
        self.curr_div = "A"
        self.curr_id = 0
        self.ELE_CONVERSION_RATE = 0.094 # amount in dollars/kwh
        self.cleanup()
        self.start()

    def handle_clients(self, connection, address):
        try:
            data = {"id": self.hash(), "rate": self.ELE_CONVERSION_RATE}
            ip = int(json.loads(connection.recv(1024).decode("ascii"))["ip"])
            self.hashTable[data["id"]] = (address[0], ip)

            data["table"] = self.DHT(data["id"])
            connection.send(json.dumps(data).encode("ascii"))

            print(self.hashTable)
        except json.JSONDecodeError:
            print("Error decoding JSON from client.")
        finally:
            connection.close()

    def hash(self):
        if int(self.curr_id)==1000:
            self.curr_div = chr(ord(self.curr_div)+1)
            self.curr_id = 0
        self.curr_id += 1
        return self.STATE+self.DIST+self.LOCL+self.curr_div+str(self.curr_id).zfill(3)

    def DHT(self, key):
        dht = {}
        data = {"new_node": {key:self.hashTable[key]}}
        keys = list(self.hashTable.keys())
        start, end = (0 if len(keys)-5<=0 else len(keys)-5, len(keys)-1)
        for i in range(start, end):
            node = self.hashTable[keys[i]]
            dht[keys[i]] = node
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_sock:
                    node_sock.connect(node)
                    node_sock.send(json.dumps(data).encode("ascii"))

            except json.JSONDecodeError:
                print("Error decoding JSON from client.")

            except Exception as e:
                print("This is while dht....")
                print(f"Error handling client: {e} {node}")

            finally:
                node_sock.close()

        return dht

    def start(self):
        self.server.listen()
        while True:
            connection, address = self.server.accept()
            clients_thread = threading.Thread(target=self.handle_clients, args=(connection, address))
            clients_thread.start()

    def cleanup(self):
        path = "/home/sm/Coding/Python/Solar_bit/eth_contracts/build/deployments/1337/"
        for file in os.listdir(path):
            os.remove(path+file)
        data = {
            "1337": {
            }
        }
        with open("/home/sm/Coding/Python/Solar_bit/eth_contracts/build/deployments/map.json", "w") as f:
            f.write(json.dumps(data, indent=2))
        f.close()

node = SuperNode()