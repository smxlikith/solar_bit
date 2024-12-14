import requests
import json
import math
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
from brownie import  accounts, network, config
from web3 import Web3

USDtoETH = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=BTC,USD,EUR"
# RATE = json.loads(requests.get(USDtoETH).content)["USD"]
RATE = 4000
LOCAL = ["development", "ganache-local", "hardhat"]
DECIMALS = 8
START_PRICE = 399600000000

def get_accounts(idx=0):
    if network.show_active() in LOCAL: 
       return accounts[idx]
    else:
        return None
        # return accounts.add(config["wallets"]["from_key"])

# def deploy_mock_v3(account):
#     return MockV3Aggregator.deploy(DECIMALS, START_PRICE, {"from":account})

def gas_strategy():
    gas_strategy = LinearScalingStrategy("60 gwei", "70 gwei", 1.1)
    if network.show_active() in LOCAL:
        gas_price(gas_strategy)

def convert_to_ETH(amount):
    return  Web3.to_wei((amount/RATE), "ether")

def convert_to_USD(wei):
    return float(Web3.from_wei(wei, "ether"))*RATE

