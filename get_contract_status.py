#!/home/sm/Coding/Python/Solar_bit/.venv/bin/python3
from eth_contracts.scripts.deploy import ContractHandler

PROJECT = ContractHandler().PROJECT
address = input("Enter the address ")
contract = PROJECT.Fundraiser.at(address)

while True:
    print("select one: ")
    print("1. maxFundAmount\n2. totalFunds\n3. remainingFunds")
    choice = input("Enter: ")
    if choice == "1":
        print("The maxFundAmount is : ", contract.maxFundAmount())
    elif choice == "2":
        print("The totalFunds is: ", contract.totalFunds())
    else:
        print("The remainingFunds is: ", contract.remainingFunds())
