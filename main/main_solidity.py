import secrets
from web3 import Web3
from web3 import HTTPProvider
from web3 import Account


web3 = Web3(HTTPProvider('http://127.0.0.1:8545'))
#it will be an issue after containerization
owner_private_key = '0x' + secrets.token_hex(32)
owner_account = Account.from_key(owner_private_key)
owner_address = owner_account.address
print(owner_address)
def money_to_owner():
    web3.eth.send_transaction({'from': web3.eth.accounts[0],
                               'to': owner_address,
                               'value': web3.to_wei(2, 'ether'),
                               'gasPrice': 1})

def send_transaction(transaction, private_key):
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    return receipt

def read_file(path):
    with open(path, 'r') as file:
        return file.read()


abi = read_file('./solidity/output/contract.abi')
bytecode = read_file('./solidity/output/contract.bin')


def create_contract(customer_address, price):
    print(owner_address)
    contract_creation_transaction = (web3.eth.contract(bytecode=bytecode, abi=abi)
                                     .constructor(customer_address, int(price*1000))
                                     .build_transaction({'from': owner_address,
                                                         'nonce': web3.eth.get_transaction_count(owner_address),
                                                         'gasPrice': 1}))
    result = send_transaction(contract_creation_transaction, owner_private_key)
    return result['contractAddress']


def confirm_delivery(contract_address):
    print(owner_address)
    contract = web3.eth.contract(address=contract_address, abi=abi)
    confirm_delivery_transaction = contract.functions.confirm_delivery().build_transaction(
        {
            'from': owner_address,
            'nonce': web3.eth.get_transaction_count(owner_address),
            'gasPrice': 1
        }
    )
    result = send_transaction(confirm_delivery_transaction, owner_private_key)
    return result['status'] == '0x1'

def add_courier(contract_address, courier_address):
    print(owner_address)
    contract = web3.eth.contract(address=contract_address, abi=abi)
    add_courier_transaction = contract.functions.add_courier(courier_address).build_transaction(
        {
            'from': owner_address,
            'nonce': web3.eth.get_transaction_count(owner_address),
            'gasPrice': 1
        }
    )
    print(owner_address)
    result = send_transaction(add_courier_transaction, owner_private_key)
    return result['status'] == '0x1'