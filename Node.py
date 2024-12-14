from google.protobuf.text_format import PrintMessage

from eth_contracts.scripts.deploy import ContractHandler
from collections import defaultdict
from Meter import Meter
import threading
import heapq
import socket
import json



class Node(Meter):
    def __init__(self, port):
        super().__init__()
        self.node_socket = None
        self.id = None
        self.ip = "0.0.0.0"
        self.port = port
        self.hashTable = {}

        self.contract_lock = threading.Lock()
        self.contracts = defaultdict(int)
        self.Contract_values = []

        self.ELE_CONVERSION_RATE = 0.094 # amount in dollars/kwh
        self.bootstrap_nodes = (self.ip, 8191)
        self.transaction_handler = ContractHandler()
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()
    """ This initialises all the variables and the function required for the proper functioning of node"""

    def listen(self):
        self.node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.node_socket.bind(("0.0.0.0", self.port))
        self.node_socket.listen()
        while True:
            node, address = self.node_socket.accept()
            handle_peer_thread = threading.Thread(target=self.handle_peers, args=(node,))
            handle_peer_thread.start()

    """ Listens for New Incoming Connections and Creates a new thread for each...."""
    def bootstrap(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
                node_socket.connect(self.bootstrap_nodes)
                node_socket.send(json.dumps({"ip": self.port}).encode("ascii"))
                response = json.loads(node_socket.recv(5024).decode("ascii"))
                self.id = response["id"]
                self.ELE_CONVERSION_RATE = response["rate"]
                self.hashTable = response["table"]
                print(f"Connected to bootstrap server {self.bootstrap_nodes}, received hash table.")
        except socket.error:
            print("No working bootstrap servers. Please contact your local authority.")
            exit()
        except json.JSONDecodeError:
            print("Received invalid data from the server.")
            exit()
    """ This sets up the Distributed Hash Table"""

    def gossip(self, energy, _transaction_id):
        if len(self.hashTable):
            if not self.contracts[_transaction_id]:
                data = {"energy": energy, "transaction_id": _transaction_id}
                data = json.dumps(data).encode("ascii")
                self.contracts[_transaction_id] = 1

                for node in self.hashTable:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                            sock.connect(tuple(self.hashTable[node]))
                            sock.send(data)
                    except Exception as e:
                        print(f"Encountered error {e}")
        else:
            print("Hash table is empty; bootstrap may have failed.")
    """ Forwards the Transactions """

    def handle_peers(self, conn):
        try:
            data = json.loads(conn.recv(1024).decode("ascii"))
            print(data)
            transaction_ID = data.get("transaction_id")
            energy = data.get("energy")
            if transaction_ID and energy:
                heapq.heappush(self.Contract_values, (-energy, transaction_ID))
                if self.net > 0:
                    process_contract_thread = threading.Thread(target=self.process_contract)
                    process_contract_thread.start()
            elif "new_node" in data:
                id = list(data["new_node"].keys())[0]
                self.hashTable[id] = data["new_node"][id]

            else:
                print(f"Unknown data received: {data}")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error decoding or processing data from peer: {e}")
        finally:
            conn.close()
    """ Handles Incoming Connections"""

    def process_contract(self):
        with self.contract_lock:
            try:
                while self.net != 0:
                    energy, transaction_id = heapq.heappop(self.Contract_values)
                    if self.net < 0:
                        energy = abs(energy)
                        print(f"Accepted contract: Transaction ID {transaction_id}, Energy {energy}")
                        amount = 0
                        # if the node consumed is greater than the incoming
                        if abs(self.net) >= energy:
                            amount = energy * self.ELE_CONVERSION_RATE
                        else:
                            amount = abs(self.net) * self.ELE_CONVERSION_RATE
                        success, paid = self.transaction_handler.contribute_to_contract(transaction_id, amount, self.port % 8190)
                        if success:
                            self.contracts[transaction_id] = 1
                            self.net -= paid/self.ELE_CONVERSION_RATE
                        else:
                            print(f"Contract already Complete: REJECTED")
                    else:
                        print(f"Insufficient energy for contract {transaction_id}; forwarding request.")
                        self.gossip(energy, transaction_id)
            except IndexError:
                print("All Active Contracts Resolved")
            except Exception as e:
                print("No Contracts Received Yet...,\n",e)
    """ Processes the contracts """

    def make_contract(self, amount, account):
        new_contract = self.transaction_handler.make_contract(amount, account, self.id)
        print(f"Made Contract at the address: {new_contract.address}")
        return new_contract.address
    """ Makes a new Contract """



