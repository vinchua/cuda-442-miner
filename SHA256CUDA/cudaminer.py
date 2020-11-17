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
        print(f'Hash: {hash}')

        data = {}
        data['coin_blob'] = coin_blob
        data['id_of_miner'] = self.miner_id
        data['hash_of_preceding_coin'] = self.last_coin
        r = requests.post(CLAIM_COIN_URL, data=data)
        response = r.json()
        print(response)


def main():
    # echo -n "supersecretcpen442publicid" | sha256sum
    obj = Tracker("534618e186cb7b73677a6b3571fe03c5ef2570d24691e7386ae6ddb62a167c7b")

    while True:
        list = []
        save_flag = False

        current_difficulty = obj.update_difficulty()
        current_coin = obj.update_last_coin()
        if current_difficulty > 9:
            print("Difficulty too high, sleeping for 3 minutes...")
            time.sleep(180 - time.time() % 180)
            continue

        timer = time.perf_counter()
        with Popen(["442cointest.exe", obj.last_coin, str(current_difficulty)], stdout=PIPE, stdin=PIPE, stderr=STDOUT) as p:
            for line in p.stdout:
                line = line.decode('utf-8')
                print(line, end='')
                if save_flag is True:
                    list.append(line.strip())

                if "-" in line:
                    save_flag = True

                if time.perf_counter() - timer > 60:
                    timer = time.perf_counter()
                    if obj.update_difficulty() != current_difficulty:
                        print("Difficulty changed. Restarting.")
                        break;
                    
        save_flag = False
        check_difficulty = obj.update_difficulty()
        check_last_coin = obj.update_last_coin()
        if current_difficulty == check_difficulty and current_coin == check_last_coin:
            obj.claim_coin(list)
        # obj.claim_coin(list)


if __name__ == "__main__":
    main()