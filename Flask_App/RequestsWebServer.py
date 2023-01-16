import subprocess
import json
import time
from flask import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/valid_accounts', methods=['POST'])
@cross_origin()
def ParseContracts():
    data = make_response(fetch_contract_users(request.data, 0, 99999))
    data.headers.add("Access-Control-Allow-Origin", "*")
    data.headers.add("Access-Control-Allow-Headers", "*")
    data.headers.add("Access-Control-Allow-Methods", "POST")
    return data

@app.route('/master_accounts', methods=['POST'])
@cross_origin()
def ParseProducers():
    data = make_response(fetch_producers(request.data))
    data.headers.add("Access-Control-Allow-Origin", "*")
    data.headers.add("Access-Control-Allow-Headers", "*")
    data.headers.add("Access-Control-Allow-Methods", "POST")
    return data

@app.route('/tokens', methods=['POST'])
@cross_origin()
def ParseTokens():
    data = make_response(fetch_tokens(request.data))
    data.headers.add("Access-Control-Allow-Origin", "*")
    data.headers.add("Access-Control-Allow-Headers", "*")
    data.headers.add("Access-Control-Allow-Methods", "POST")
    return data


def fetch_contract_users(document, start, end) -> None:
    accounts = json.loads(document)
    #print(accounts)
    valid_accounts = []
    for account in accounts:
        try:
            account_actions = []
            valid_contract = subprocess.Popen(["cline", "get", "abi", account], stdout = subprocess.PIPE)
            #time.sleep(0.2)
            valid_contract = json.loads(valid_contract.communicate()[0].decode())
            for action in valid_contract["actions"]:
                account_actions.append(action["name"])
            valid_actions = subprocess.Popen(["cline", "get", "actions", account, str(start), str(end), "--json", "--full"], stdout = subprocess.PIPE)
            #time.sleep(0.2)
            valid_actions = json.loads(valid_actions.communicate()[0].decode())["actions"]
            for act in valid_actions:
                if act["action_trace"]["act"]["name"] in account_actions:
                    valid_accounts.append(account)
                    break
        except Exception as ex:
            #print(ex)
            pass
    return str(valid_accounts)

def fetch_producers(document) -> None:
    accounts = json.loads(document)
    #print(accounts)
    valid_accounts = []
    for account in accounts:
        try:
            producer_info = subprocess.Popen(["cline", "get", "account", account, "--json"], stdout=subprocess.PIPE)
            producer = json.loads(producer_info.communicate()[0].decode())
            if len(producer["voter_info"]["producers"]) > 0:
                valid_accounts.append(account)
        except Exception as ex:
            #print(ex)
            pass
    return str(valid_accounts)

def fetch_tokens(document) -> None:
    accounts = json.loads(document)
    #print(accounts)
    tokens_info = subprocess.Popen(["cline", "get", "currency", "balance", "inery.token", "inery", "--json"], stdout=subprocess.PIPE)
    tokens = json.loads(tokens_info.communicate()[0].decode())
    valid_accounts = []
    for token in tokens:
        try:
            token_name = str(token).split(" ")[1]
            owner_info = subprocess.Popen(["cline", "get", "currency", "stats", "inery.token", token_name], stdout=subprocess.PIPE)
            owner_name = json.loads(owner_info.communicate()[0].decode())[token_name]["issuer"]
            if owner_name in accounts:
                valid_accounts.append(owner_name)
        except Exception as ex:
            #print(ex)
            pass
    return str(valid_accounts)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="443", ssl_context=("<cert.pem>", "<key.pem>"))
