import json
import urllib

from web3 import Web3
from web3.types import TxParams
from eth_account.account import Account
from eth_account import messages
from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes

wallet = ''

victim = ''

sender: LocalAccount = Account.from_key(wallet)

victimSender :LocalAccount = Account.from_key(victim)

# Web3 HTTP Provider
w3 = Web3(Web3.HTTPProvider('xxxx'))


def main():

    tx1flashbots: TxParams = {
        "to": HexBytes('x'),
        "value": w3.to_wei(0.018, 'ether'), 
        "gas": 90000,
        "maxFeePerGas": w3.to_wei(80, 'gwei'),
        "maxPriorityFeePerGas": w3.to_wei(70, 'gwei'),
        "nonce": w3.eth.get_transaction_count(sender.address),
        "chainId": 1 
    }

    tx2flashbots: TxParams = {
        "to": HexBytes('x'),
        "value": 0,  
        "data": '', 
        "gas": 120000, 
        "maxFeePerGas": w3.to_wei(100, 'gwei'),
        "maxPriorityFeePerGas": w3.to_wei(70, 'gwei'),
        "nonce": w3.eth.get_transaction_count(victimSender.address),
        "chainId": 1 
    }

    tx3flashbots: TxParams = {
        "to": HexBytes(''),
        "value": 0,  
        "data": '',  
        "gas": 121000, 
        "maxFeePerGas": w3.to_wei(100, 'gwei'),
        "maxPriorityFeePerGas": w3.to_wei(70, 'gwei'),
        "nonce": w3.eth.get_transaction_count(victimSender.address) + 1,
        "chainId": 1 
    }

    # 签名交易
    tx1SignedFlashbots = sender.sign_transaction(tx1flashbots)

    tx2SignedFlashbots = victimSender.sign_transaction(tx2flashbots)

    tx3SignedFlashbots = victimSender.sign_transaction(tx3flashbots)

    for i in range(12):
        flashbotsJson = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendBundle",
            "params": [
                {
                    "txs": [
                        tx1SignedFlashbots.rawTransaction.hex(),
                        tx2SignedFlashbots.rawTransaction.hex(),
                        tx3SignedFlashbots.rawTransaction.hex(),
                    ],
                    "blockNumber": hex(w3.eth.block_number + i + 1),  
                }
            ]
        }

        print("blockNumber: ", w3.eth.block_number + i + 1)


        flashbotsJsonStr = json.dumps(flashbotsJson)
        flashbotsBytes = flashbotsJsonStr.encode('utf-8')

        message = messages.encode_defunct(text=Web3.keccak(flashbotsBytes).hex())
        signatureer: LocalAccount = Account.create()

        signed_message = signatureer.address + ':' + Account.sign_message(message, signatureer._private_key.hex()).signature.hex()


        headers = {'Content-Type': 'application/json', 'X-Flashbots-Signature': signed_message, 'User-Agent': 'Mozilla/5.0 3578.98 Safari/537.36'}


        # annother miner address
        # https://rsync-builder.xyz/
        # https://rpc.titanbuilder.xyz
        flashbotsRequest = urllib.request.Request("https://rpc.beaverbuild.org", data=flashbotsBytes, headers=headers, method='POST')
        flashbotsRes = urllib.request.urlopen(flashbotsRequest).read()
        

        print(flashbotsRes)

if __name__ == "__main__":
    main()
