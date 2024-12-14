from eth_contracts.scripts.preconditions import get_accounts, convert_to_ETH, convert_to_USD
from brownie import project, network
from web3.datastructures import AttributeDict


class ContractHandler:
    def __init__(self):
        self.PROJECT = project.load("/home/sm/Coding/Python/Solar_bit/eth_contracts")
        self.PROJECT.load_config()
        network.connect("ganache-local")

    def make_contract(self, amount, idx, nodeID):
        account = get_accounts(idx)
        contract = self.PROJECT.Fundraiser.deploy(convert_to_ETH(amount), nodeID, {"from": account})
        network.contract.ContractEvents(contract).subscribe("FundsReleased", self.handleFundRelease)
        network.contract.ContractEvents(contract).subscribe("FundReceived", self.handleFundReceived)
        return contract

    def contribute_to_contract(self, address, amount, idx):
        contract = self.PROJECT.Fundraiser.at(address)
        if contract.checkReleased():
            return False, 0
        else:
            remaining_amount = contract.remainingFunds()
            try:
                if convert_to_USD(remaining_amount)>amount:
                    contract.contribute({"from": get_accounts(idx), "value": convert_to_ETH(amount)})
                    return True, amount
                else:
                    contract.contribute({"from": get_accounts(idx), "value": remaining_amount})
                    return True, convert_to_USD(remaining_amount)
            except Exception as e:
                print(e)

    def handleFundRelease(self, event):
        event_dict = AttributeDict(event['args'])
        print(f"Total funds received of amount {convert_to_USD(event_dict['totalAmount'])}")

    def handleFundReceived(self, event):
        event_dict = AttributeDict(event['args'])
        print(f"Address: {event_dict['contributor']} put forth amount: {convert_to_USD(event_dict['amount'])}")

