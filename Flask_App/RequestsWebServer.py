import subprocess
import json
import time
from flask import *

app = Flask(__name__)

@app.route('/valid_accounts', methods=['POST'])
def ParseData():
    data = fetch_users(request.data, 0, 99999)
    #data.headers['Access-Control-Allow-Origin'] = '*'
    return data


def fetch_users(document, start, end) -> None:
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
            valid_actions = subprocess.Popen(["cline", "get", "actions", account, str(start), str(end), "-j", "--full"], stdout = subprocess.PIPE)
            #time.sleep(0.2)
            valid_actions = json.loads(valid_actions.communicate()[0].decode())["actions"]
            for act in valid_actions:
                if act["action_trace"]["act"]["name"] in account_actions:
                    valid_accounts.append(account)
                    break
        except Exception as ex:
            #print(ex)
            pass
    message = []
    text = []
    for account in valid_accounts:
        text.append(account)
    message.append("{'valid_accounts' : " + str(text) + "}")
    return message

if __name__ == "__main__":
    app.run(host="0.0.0.0")