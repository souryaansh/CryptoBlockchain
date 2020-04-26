from hashlib import sha256
import json
import time
from pprint import pprint
import random

g=2
p=11
def zeroKnowlege(x):
    y = (g**x)%p
    r = random.randint(0,p-1)
    h=(g**r)%p
    b = verifyZK(h,g,r,p)
    bobshouldsend=h*(y**b)%p
    s=(r+(b*x))%(p-1)
    if(bobshouldsend==verifyZK2(g,s,p)):
        return True
    return False
def verifyZK(h,g,r,p):return random.randint(0,1)
def verifyZK2(g,s,p):return (g**s)%p

class Block:
    def __init__(self,index,transactions,timestamp,previous_hash):
        self.index = index
        self.transactions=transactions
        self.timestamps = timestamp
        self.previous_hash = previous_hash
    # one way hash
    # very difficult to obtain key from value
    def hash_it(self):
        str_of_block = json.dumps(self.__dict__,sort_keys=True)
        return sha256(str_of_block.encode()).hexdigest()


class Chain_of_blocks:
    def __init__(self):
        self.blockchain = []
        self.create_zero_block() 
        self.new_transactions=[]

    def create_zero_block(self):
        zero_block = Block(0,[],time.time(),"0")
        zero_block.hash=zero_block.hash_it()
        self.blockchain.append(zero_block)

    def last_block(self):
        return self.blockchain[-1]

    def proof_of_work(self,block):
        block.fpw = 0
        hashed_block = block.hash_it()
        while not hashed_block[:4]=="0000" :
            block.fpw +=1
            hashed_block = block.hash_it()
        return hashed_block
    
    def createBlock(self, block, pOw):
        if(self.last_block().hash != block.previous_hash):
            return False
        
        if not self.ifValid(block,pOw):
            return False
        block.hash = pOw
        self.blockchain.append(block)

    def ifValid(self,block,hashof):
        return hashof[:4]=="0000" and hashof==block.hash_it()
    
    def verifyTransaction(self,transaction):
        if(zeroKnowlege(len(transaction["sender"]))):
            self.new_transactions.append(transaction)
            return True
        else:
            return False

    def mineBlock(self):
        if not self.new_transactions:
            return False
        print("henlo")
        prev_block = self.last_block()
        new_block = Block(index = prev_block.index+1,transactions = self.new_transactions,timestamp = time.time(),previous_hash=prev_block.hash)
        pOw = self.proof_of_work(new_block)
        self.createBlock(new_block,pOw)
        self.new_transactions=[]
        return new_block.index
    
    def viewUser(self,user):
        tore=[]
        for i in self.blockchain:
            for j in i.transactions:
                if(j["sender"]==user or j["receiver"]==user):
                    tore.append(j)
        return tore

    def isValidChain(self, chain):
        """
        A helper method to check if the entire blockchain is valid.            
        """
        result = True
        previous_hash = "0"

        # Iterate through every block
        for i in self.blockchain:
            block_hash = i.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(i, "hash")

            if not self.ifValid(i, i.hash) or \
                    previous_hash != i.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

blockchain = Chain_of_blocks()
def is_uninanimous():
    global blockchain
    longest_chain = None
    curr_len = len(blockchain.blockchain)

    for node in peers:
        response = requests.get('{}/get_block_chain'.format(node))
        their_length = response.json()['length']
        their_chain = response.json()['chain']
        if their_length > curr_len and blockchain.isValidChain(their_chain):
              # Longer valid chain found!
            current_len = their_length
            longest_chain = their_chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


# blockchain.verifyTransaction({"sender":"Souryaansh", "receiver":"Hitesh","transact":1000, "trantime":time.time()})
# blockchain.verifyTransaction({"sender":"Hitesh", "receiver":"Souryaansh","transact":2000, "trantime":time.time()})
# blockchain.verifyTransaction({"sender":"Abhishek", "receiver":"Hitesh","transact":1000, "trantime":time.time()})
# blockchain.verifyTransaction({"sender":"Abhishek", "receiver":"Souryaansh","transact":2000, "trantime":time.time()})
# result = blockchain.mineBlock()
# blockchain.viewUser("Souryaansh")
# print(result)
# for i in blockchain.blockchain:
#     pprint(i.__dict__)

#GUI

from flask import Flask, request
import requests

webapp=Flask(__name__)

@webapp.route('/veirfyandaddtran', methods=['POST'])
def verifyandadd():
    currTran=request.get_json()
    deets=["sender","receiver","transact"]
    for i in deets:
        if not currTran.get(i):
            return "Transaction not valid", 404
    
    currTran["trantime"] = time.time()
    print("in vad")
    if(blockchain.verifyTransaction(dict(currTran))):
        return "Success", 201
    
    return "Transaction not valid", 404

@webapp.route('/viewuser', methods=['POST'])

def viewUsertran():
    username = request.form["user"]
    print(username)
    if not username:
        return "Transaction not valid", 404

    tore_data=blockchain.viewUser(str(username))
    if(not len(tore_data)):
        return "User's Transactions haven't been mined."
    # tore =""
    # to_tore=[]
    # for i in tore_data:
    #     tore=""
    #     tore+="\nSender: "
    #     tore+=i["sender"]
    #     tore+=" Receiver: "
    #     tore+=i["receiver"]
    #     tore+=" Amount: "
    #     tore+=str(i["transact"])
    #     tore+="\n"
    #     to_tore.append(tore)
    return str(tore_data)

@webapp.route('/mineBlock', methods=['GET'])
def mineBlock():
    res=blockchain.mineBlock()
    if not res:
        return "No transactions to mine !"
    else:
        len_chain=len(blockchain.blockchain)
        is_uninanimous()
        if len_chain == len(blockchain.blockchain):
            announce_new_block(blockchain.last_block)
    return "Mined Block #{}.".format(blockchain.last_block().index)

@webapp.route('/get_block_chain', methods=['GET'])
def get_block_chain():
    chain= []
    for i in blockchain.blockchain:
        chain.append(i.__dict__)
    return json.dumps({"length": len(chain),
                       "chain": chain,
                       "peers": list(peers)})

peers = set()

@webapp.route('/register_new_node', methods=['POST'])
def add_peers():
    address_of_node = request.get_json()["node_address"]
    if not address_of_node:
        return "Invalid data", 400
    peers.add(address_of_node)

    # Return the blockchain to the newly registered node so that it can sync
    return get_block_chain()


@webapp.route('/add_this_to_exis', methods=['POST'])
def add_this_to_exis():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    response = requests.post(node_address + "/register_new_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers

        drop_chain = response.json()['chain']
        blockchain = create_chain_from_dump(drop_chain)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(drop_chain):
    generated_blockchain = Chain_of_blocks()
    # generated_blockchain.create_genesis_block()
    for i, j in enumerate(drop_chain):
        if i == 0:
            continue 
        block = Block(j["index"],
                      j["transactions"],
                      j["timestamp"],
                      j["previous_hash"],
                      j["nonce"])
        proof = j['hash']
        added = generated_blockchain.cre(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain

@webapp.route('/add_new_block', methods=['POST'])
def verify_and_add_block():
    j = request.get_json()
    block = Block(j["index"],
                  j["transactions"],
                  j["timestamp"],
                  j["previous_hash"])

    proof = j['hash']
    added = blockchain.createBlock(block, proof)

    if not added:
        return "block was thrown away", 400

    return "block is added", 201


def announce_new_block(block):
    for peer in peers:
        url = "{}add_new_block".format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))

 
