from Node import Node
import time

if __name__ == "__main__":
    node = Node(int(input("Enter the Port: ")))
    node.bootstrap()
    while True:
        print(node.hashTable)
        node.net = int(input("NET: "))
        if node.net > 0:
            contract = node.make_contract(node.net*node.ELE_CONVERSION_RATE, node.port%8190)
            node.gossip(abs(node.net), contract)
        elif node.net < 0:
            node.process_contract()