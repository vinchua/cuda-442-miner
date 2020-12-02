import requests
import json
import base64
import time
from subprocess import Popen, PIPE, STDOUT
from timeit import default_timer as timer

COIN_PREFIX_STR = "CPEN 442 Coin2020"
LAST_COIN_URL = "http://cpen442coin.ece.ubc.ca/last_coin";
DIFFICULTY_URL = "http://cpen442coin.ece.ubc.ca/difficulty"
CLAIM_COIN_URL = "http://cpen442coin.ece.ubc.ca/claim_coin"
DEFAULT_DIFFICULTY = 7

class Tracker(object):
    def __init__(self, miner_id):
        self.miner_id = miner_id
        self.last_coin = self.get_last_coin()
        self.difficulty = self.get_difficulty()


    def get_last_coin(self):
        r = requests.post(LAST_COIN_URL)
        response = r.json()
        return response['coin_id']

    def update_last_coin(self):
        self.last_coin = self.get_last_coin()
        return self.last_coin

    def get_difficulty(self):
        r = requests.post(DIFFICULTY_URL)
        response = r.json()
        return response['number_of_leading_zeros']

    def update_difficulty(self):
        self.difficulty = self.get_difficulty()
        return self.difficulty

    def claim_coin(self, list):
        coin_blob = base64.b64encode(list[0].encode("utf-8")).decode("utf-8")
        hash = list[2]

        print(f'Coin_blob: {coin_blob}')
        # print(f'Hash: {hash}')

        data = {}
        data['coin_blob'] = coin_blob
        data['id_of_miner'] = self.miner_id
        data['hash_of_last_coin'] = self.last_coin
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(CLAIM_COIN_URL, data=json.dumps(data), headers=headers)
        response = r.json()
        print(response)


def main():
    # echo -n "cudacloud442" | sha256sum
    obj = Tracker("8a366f7c9c9ef851760f9838ac5b1b27fa9c4341620fad9ff1dfbf4f421fae91")

    # std::string previous_coin = argv[1];
    # std::string suffix = argv[2];
    # difficulty = std::stoi(argv[3]);

    # if (argc == 4){
	# 	user_nonce = std::stoi(argv[4]);
	# }

    while True:
        list = []
        save_flag = False

        current_difficulty = obj.update_difficulty()
        current_coin = obj.update_last_coin()

        timer = time.perf_counter()
        with Popen(["./miner", obj.last_coin, obj.miner_id, str(current_difficulty),"95600000000000"], stdout=PIPE, stdin=PIPE, stderr=STDOUT) as p:
            for line in p.stdout:
                line = line.decode('utf-8')
                print(line, end='')
                if save_flag is True:
                    list.append(line.strip())

                if "-" in line:
                    save_flag = True

                if time.perf_counter() - timer > 10:
                    timer = time.perf_counter()
                    if obj.update_last_coin() != current_coin:
                        print("Coin changed. Restarting.")
                        p.kill()
                        break;
                    if obj.update_difficulty() != current_difficulty:
                        print("Difficulty changed. Restarting.")
                        p.kill()
                        break;
                    
        save_flag = False
        check_difficulty = obj.update_difficulty()
        check_last_coin = obj.update_last_coin()
        print(list)
        if current_difficulty == check_difficulty and current_coin == check_last_coin and list:
            obj.claim_coin(list)


if __name__ == "__main__":
    main()
