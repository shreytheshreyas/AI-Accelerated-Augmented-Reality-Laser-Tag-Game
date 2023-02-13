import json
import time

from GameState import GameState
from Helper import Actions

TURN_MAX_TIME = 10


class GameEngine:
    def __init__(
        self, opp_in_frames, action_queue, eval_req_queue, eval_resp_queue, vis_queue
    ):
        self.game_state = GameState()
        self.action_queue = action_queue
        self.eval_req_queue = eval_req_queue
        self.eval_resp_queue = eval_resp_queue
        self.vis_queue = vis_queue
        self.opp_in_frames = opp_in_frames
        self.signals = {}
        self.complete = {}
        self.turn_start_time = 0.0
        self.turn_time_left = 0
        self.reset_turn()

    def update_players(self, update):
        self.game_state.player_1.initialize_from_dict(update["p1"])
        self.game_state.player_2.initialize_from_dict(update["p2"])

    def reset_turn(self):
        print("Resetting")
        self.turn_start_time = time.time()
        self.turn_time_left = TURN_MAX_TIME
        self.complete = {"p1": False, "p2": False}

        self.signals = {
            "p1": {
                "action": None,
                "opp_hit": False,
                "opp_blasted": False,
            },
            "p2": {
                "action": None,
                "opp_hit": False,
                "opp_blasted": False,
            },
        }

    def check_turn(self, player):
        if (
            self.signals[player]["action"] == Actions.shoot
            and self.signals[player]["opp_hit"]
        ):
            self.complete[player] = True

        elif (
            self.signals[player]["action"] == Actions.grenade
            or self.signals[player]["action"] == Actions.reload
            or self.signals[player]["action"] == Actions.shield
        ):
            self.complete[player] = True

    def get_opp(self, player):
        return "p1" if player == "p2" else "p2"

    def is_complete(self):
        return self.complete["p1"] and self.complete["p2"]

    def is_turn_over(self):
        self.turn_time_left = max(time.time() - self.turn_start_time, 0)
        print(self.turn_time_left)
        return self.turn_time_left <= 0

    def run(self):
        self.reset_turn()

        while True:
            if self.is_turn_over():
                self.reset_turn()
                continue

            player, action = self.action_queue.get()
            print(player, action)
            opp = self.get_opp(player)

            if action in Actions.all:
                self.signals[player]["action"] = action
            elif action == Actions.hit:
                self.signals[opp]["opp_hit"] = True

            print(self.signals)
            self.check_turn("p1")
            self.check_turn("p2")

            if self.is_complete():
                print("Turn Complete")
                action_p1 = self.signals["p1"]["action"]
                opp_hit_p1 = self.signals["p1"]["opp_hit"]
                action_p2 = self.signals["p2"]["action"]
                opp_hit_p2 = self.signals["p2"]["opp_hit"]

                with self.opp_in_frames.get_lock():
                    opp_blasted_p1 = self.opp_in_frames[0]
                    opp_blasted_p2 = self.opp_in_frames[1]

                player_1 = self.game_state.player_1
                player_2 = self.game_state.player_2

                action_p1_is_valid = player_1.action_is_valid(
                    action_p1, opp_hit_p1, opp_blasted_p1
                )
                action_p2_is_valid = player_2.action_is_valid(
                    action_p2, opp_hit_p2, opp_blasted_p2
                )

                player_1.update(action_p1, action_p2, action_p2_is_valid)
                player_2.update(action_p2, action_p1, action_p1_is_valid)

                game_state = self.game_state.get_dict()
                self.eval_req_queue.put(game_state)
                self.vis_queue.put(game_state)

                update_json = self.eval_resp_queue.get()
                update = json.loads(update_json)
                self.update_players(update)

                self.reset_turn()
