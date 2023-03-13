import json
import time

from GameState import GameState
from Helper import Actions

TURN_MAX_TIME = 3

SENSOR_MAPPING = {"gun": "bullets", "vest": "hp"}


class GameEngine:
    def __init__(
        self,
        opp_in_frames,
        action_queue,
        update_beetle_queue,
        eval_req_queue,
        eval_resp_queue,
        vis_queue,
    ):
        self.game_state = GameState()
        self.action_queue = action_queue
        self.update_beetle_queue = update_beetle_queue
        self.eval_req_queue = eval_req_queue
        self.eval_resp_queue = eval_resp_queue
        self.vis_queue = vis_queue
        self.opp_in_frames = opp_in_frames
        self.signals = {}
        self.complete = {}
        self.turn_end_time = 0.0
        self.turn_time_left = 0
        self.reset_turn()

    def update_players(self, update):
        player_1 = self.game_state.p1
        player_2 = self.game_state.p2

        if update["p1"]["bullets"] != player_1.bullets:
            self.update_beetle_queue.put(("p1_gun", update["p1"]["bullets"]))
        if update["p2"]["bullets"] != player_2.bullets:
            self.update_beetle_queue.put(("p2_gun", update["p2"]["bullets"]))

        if update["p1"]["hp"] != player_1.hp:
            self.update_beetle_queue.put(("p1_vest", update["p1"]["hp"]))
        if update["p2"]["hp"] != player_2.hp:
            self.update_beetle_queue.put(("p2_vest", update["p2"]["hp"]))

        player_1.initialize_from_dict(update["p1"])
        player_2.initialize_from_dict(update["p2"])

    def reset_turn(self):
        # print("Resetting")
        self.turn_end_time = time.time() + TURN_MAX_TIME
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
        return self.complete["p1"] or self.complete["p2"]

    def is_turn_over(self):
        print("Turn is over")
        self.turn_time_left = max(self.turn_end_time - time.time(), 0)
        return self.turn_time_left <= 0

    def is_logged_out(self):
        return (
            self.game_state.p1.action == Actions.logout
            or self.game_state.p2.action == Actions.logout
        )

    def run(self):
        self.reset_turn()
        game_start = True

        while game_start:
            if self.is_turn_over():
                self.reset_turn()
                continue

            if not self.action_queue:
                continue

            player, action = self.action_queue.get()
            opp = self.get_opp(player)
            print(player, action)

            # If new connection, action will be 'conn_<sensor>'
            conn_list = action.split("_", 1)
            if conn_list[0] == "conn":
                sensor = conn_list[1]
                data = getattr(self.game_state, player)[SENSOR_MAPPING[sensor]]
                print(data)
                self.update_beetle_queue.put((player + "_" + sensor, data))
                continue

            if action in Actions.all:
                self.signals[player]["action"] = action
            elif action == Actions.hit:
                self.signals[opp]["opp_hit"] = True

            self.check_turn("p1")
            self.check_turn("p2")

            if self.is_complete():
                print("Turn Complete")
                if self.complete["p1"]:
                    action_p1 = self.signals["p1"]["action"]
                    opp_hit_p1 = self.signals["p1"]["opp_hit"]
                else:
                    action_p1 = Actions.no
                    opp_hit_p1 = False
                if self.complete["p2"]:
                    action_p2 = self.signals["p2"]["action"]
                    opp_hit_p2 = self.signals["p2"]["opp_hit"]
                else:
                    action_p2 = Actions.no
                    opp_hit_p2 = False

                with self.opp_in_frames.get_lock():
                    opp_blasted_p1 = self.opp_in_frames[0]
                    opp_blasted_p2 = self.opp_in_frames[1]

                player_1 = self.game_state.p1
                player_2 = self.game_state.p2

                action_p1_is_valid = player_1.action_is_valid(
                    action_p1, opp_hit_p1, opp_blasted_p1
                )
                action_p2_is_valid = player_2.action_is_valid(
                    action_p2, opp_hit_p2, opp_blasted_p2
                )

                player_1.update(action_p1, action_p2, action_p2_is_valid)
                player_2.update(action_p2, action_p1, action_p1_is_valid)

                game_state = self.game_state.get_dict()
                print("[Game State Sent]:\n" + json.dumps(game_state, indent=4))

                self.eval_req_queue.put(game_state)
                updated_game_state = self.eval_resp_queue.get()

                self.update_players(updated_game_state)
                print(
                    "[Game State Updated]:\n"
                    + json.dumps(self.game_state.get_dict(), indent=4)
                )

                self.vis_queue.put(updated_game_state)

                if self.is_logged_out():
                    game_start = False

                self.reset_turn()
