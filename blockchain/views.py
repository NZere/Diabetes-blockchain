import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from blockchain.models import Block
from market.models import Cart
from users.views import get_user_first_name


class Blockchain(object):
    def __init__(self):
        self.chain = Block.objects.all()
        self.current_transactions = []
        self.nodes = set()

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def new_block(self, proof, previous_hash=None):
        print("new block")
        block = Block.objects.create(
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(Block.objects.order_by("-id")[0]))
        self.current_transactions = []
        return block

    def new_transaction(self, sender, recipient, amount, time=str(datetime.now())):
        """
        Generate new transaction information, which will be added to the next block to be mined
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'time': time
        })
        return self.last_block.id + 1

    @staticmethod
    def hash(block):
        block_json = {
            'index': block.id,
            'timestamp': block.timestamp,
            'transactions': block.transactions,
            'proof': block.proof,
            'previous_hash': block.previous_hash,
        }
        block_string = json.dumps(block_json, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def hash_dict(block):
        block_json = {
            'index': block["id"],
            'timestamp': block["timestamp"],
            'transactions': block["transactions"],
            'proof': block["proof"],
            'previous_hash': block["previous_hash"],
        }
        block_string = json.dumps(block_json, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return Block.objects.order_by("-id")[0]
        # return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        print("========")
        while self.valid_proof(last_proof, proof) is False:
            print(proof)
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = str(last_proof * proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"

    def valid_chain(self, chain):
        current_index = 2
        last_block = chain[0]  # id=1
        print(last_block)
        while current_index < len(chain):
            try:
                for d in chain:  # d is dict
                    if d["id"] == current_index:
                        block = d  # block is dict
                        if block["previous_hash"] != self.hash_dict(last_block):
                            mes = []
                            ss = "Hashes not equal!! error in block:" + str(current_index) + "\n"
                            ss += "it must be: " + block["previous_hash"] + ", not: " + self.hash_dict(last_block)

                            mes.append(ss)
                            return False, mes
                        # Check that the Proof of Work is correct
                        if not self.valid_proof(last_block["proof"], block["proof"]):
                            mes = []
                            ss = "proofs are incorrect"
                            mes.append(ss)
                            return False, mes
                        last_block = block
                        current_index += 1
            except:
                mes = []
                ss = "error"
                mes.append(ss)
                return False, mes
        mes = []
        return True, mes


node_identifier = str(uuid4()).replace('-', '')
# Instantiate the Blockchain
blockchain = Blockchain()


def mine(request, *args, **kwargs):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
    last_block = blockchain.last_block
    # last_proof = last_block['proof']
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)
    if len(blockchain.current_transactions) == 0 and request.user.is_staff == 0:
        messages.warning(request, "you can not mine")
        return redirect("/")
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        # 'index': block['index'],
        'index': block.id,
        # 'transactions': block['transactions'],
        'transactions': block.transactions,
        'proof': block.proof,
        # 'previous_hash': block['previous_hash']
        'previous_hash': block.previous_hash,
        # 'this_hash': blockchain.hash(blockchain.chain[-1])
        'this_hash': blockchain.hash(blockchain.last_block),
        'user_first_name': user_first_name
    }
    print(response)
    return redirect("/blockchain/block/chain", response)
    # return HttpResponse(json.dumps(response))


@csrf_protect
def new_transaction(request):
    order = Cart.objects.get(user=request.user, is_ordered=False)
    order_items = order.items.all()
    final = 0
    for i in order_items:
        final += i.get_final_price()
    index = 0
    print("final, ", final)
    index = blockchain.new_transaction(request.user.username, User.objects.get(id=1).first_name,
                                       final)
    order_items.update(is_ordered=True)
    for item in order_items:
        print("here")
        item.save()
    print("end")
    order.is_ordered = True
    order.save()
    messages.success(request, 'Transaction will be added to Block %s' % index)
    print("to mine")
    return redirect("blockchain:mine")


def hashes_of_blocks():
    hashes = []
    for i in Block.objects.all():
        hashes.append(blockchain.hash(i))
    print(hashes)
    return hashes


def chains(request):
    block_list = list(Block.objects.values())
    response = {
        'chain': list(block_list),
        'length': len(block_list)
    }
    return JsonResponse(response, safe=False)


def full_chain(request):
    user_first_name = None
    if request.user.is_authenticated:
        user_first_name = get_user_first_name(request.user)
    blockchain_chain = Block.objects.all()
    checking_blocks = []
    current_index = 2

    hashes_blocks = hashes_of_blocks()
    is_red = False
    while current_index <= len(blockchain_chain):

        b1 = Block.objects.get(id=current_index)
        b_prev = Block.objects.get(id=(current_index - 1))

        if blockchain.valid_proof(b_prev.proof, b1.proof) and (
                not is_red and b1.previous_hash == blockchain.hash(Block.objects.get(id=(current_index - 1)))):
            checking_blocks.append(1)
        else:
            is_red = True
            checking_blocks.append(0)

        current_index += 1
    blockchain_chain2 = Block.objects.all().order_by("-id")

    checking_blocks.reverse()
    hashes_blocks.reverse()
    zippedList = zip(blockchain_chain2, hashes_blocks, checking_blocks)
    print(blockchain_chain)
    response = {
        # 'chain': blockchain.chain,
        'neighbours': blockchain.nodes,
        'length': len(blockchain_chain),
        'zip': zippedList,
        # 'hashes': hashes_of_blocks()
        'user_first_name': user_first_name
    }
    # return HttpResponse(json.dumps(response))
    print("here")
    return render(request, 'blockchain.html', response)


def proof_of_work(self, last_proof):
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
        proof += 1
    return proof


@staticmethod
def valid_proof(last_proof, proof):
    guess = str(last_proof * proof).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"


@csrf_exempt
def connect_node(request):  # New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=400)
        for node in nodes:
            blockchain.register_node(node)
        response = {
            'message': 'All the nodes are now connected. The Sudocoin Blockchain now contains the following nodes:',
            'total_nodes': list(blockchain.nodes)}
    return JsonResponse(response)


def replace_chain(request):  # New
    if request.method == 'GET':
        try:
            is_chain_replaced, mes = blockchain.resolve_conflicts()
            print(mes)
            try:
                if is_chain_replaced and len(mes) != 0:
                    for mess in mes:
                        messages.success(request, mess)
                elif len(mes) != 0:
                    for mess in mes:
                        messages.warning(request, mess)
                elif not is_chain_replaced:
                    messages.info(request, "All good. The chain is the largest one.")
            except:
                print("replace chain")

        except:
            print("replace chain error")
    return redirect("blockchain:chain")
