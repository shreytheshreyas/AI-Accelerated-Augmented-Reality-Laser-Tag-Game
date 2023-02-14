import json
import multiprocessing as mp
import time

from GameEngine import GameEngine

init_json = '{ "p1": { "hp": 100, "action": "none", "bullets": 6, "grenades": 2, "shield_time": 0, "shield_health": 0, "num_deaths": 0, "num_shield": 3 }, "p2": { "hp": 100, "action": "none", "bullets": 6, "grenades": 2, "shield_time": 0, "shield_health": 0, "num_deaths": 0, "num_shield": 3 } } '

opp_in_frames = mp.Array("i", [0] * 2)
action_queue = mp.Queue()
eval_req_queue = mp.Queue()
eval_resp_queue = mp.Queue()
vis_queue = mp.Queue()

engine = GameEngine(
    opp_in_frames, action_queue, eval_req_queue, eval_resp_queue, vis_queue
)


def get_queue(queue):
    while True:
        output = queue.get()
        output = json.dumps(output, indent=2)
        print(output)


def put_actions(action_queue):
    turns = [
        [
            "p1_hit",
            "p2_shoot",
        ],
        [
            "p1_hit",
            "p2_shoot",
            "p1_reload",
        ],
        [
            "p1_hit",
            "p2_shoot",
            "p1_reload",
        ],
        [
            "p1_shoot",
            "p2_hit",
            "p2_grenade",
        ],
        [
            "p1_reload",
            "p2_grenade",
        ],
        [
            "p1_reload",
            "p2_grenade",
        ],
        [
            "p1_hit",
            "p2_shoot",
            "p1_reload",
        ],
        [
            "p1_shoot",
            "p2_hit",
            "p2_grenade",
        ],
    ]

    for turn in turns:
        for x in turn:
            time.sleep(0.5)
            player, action = x.split("_")
            if x == "p2_grenade":
                opp_in_frames[1] = 1
            else:
                opp_in_frames[1] = 0
            action_queue.put((player, action))
            eval_resp_queue.put(init_json)

        time.sleep(3)


engine_process = mp.Process(target=engine.run)
vis_queue_process = mp.Process(target=get_queue, args=(vis_queue,))
# eval_queue_process = mp.Process(target=get_queue, args=(eval_req_queue,))
# eval_queue_process = mp.Process(target=get_queue, args=(eval_req_queue,))
action_process = mp.Process(target=put_actions, args=(action_queue,))

try:
    engine_process.start()
    vis_queue_process.start()
    # eval_queue_process.start()
    action_process.start()
    engine_process.join()
    vis_queue_process.join()
    # eval_queue_process.join()
    action_process.join()
except KeyboardInterrupt:
    print("\nShutting Down")
    engine_process.terminate()
    vis_queue_process.terminate()
    # eval_queue_process.terminate()
    action_process.terminate()
