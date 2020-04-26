import datetime
import json

import requests
from flask import render_template, redirect, request

from app import webapp

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/get_block_chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for i in block["transactions"]:
                i["index"] = block["index"]
                i["hash"] = block["previous_hash"]
                content.append(i)

        global posts
        posts = sorted(content, key=lambda k: k['trantime'],
                       reverse=True)


@webapp.route('/')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='Business Transactions',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@webapp.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    sender = request.form["sender"]
    transact = request.form["transact"]
    receiver = request.form["receiver"]

    transaction_object = {
        "sender":sender,
        "transact":transact,
        "receiver":receiver
    }

    # Submit a transaction
    new_transact_address = "{}/veirfyandaddtran".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_transact_address,
                  json=transaction_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
