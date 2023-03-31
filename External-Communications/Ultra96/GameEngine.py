import json
import time

from GameState import GameState
from Helper import Actions

TWO_PLAYER = True

TURN_MAX_TIME = 5

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
        eval_req_console_queue,
        eval_resp_console_queue,
        logs_queue,
    ):
        self.game_state = GameState()
        self.action_queue = action_queue
        self.update_beetle_queue = update_beetle_queue
        self.eval_req_queue = eval_req_queue
        self.eval_resp_queue = eval_resp_queue
        self.vis_queue = vis_queue
        self.opp_in_frames = opp_in_frames
        self.eval_req_console_queue = eval_req_console_queue
        self.eval_resp_console_queue = eval_resp_console_queue
        self.logs_queue = logs_queue
        self.signals = {}
        self.complete = {}
        self.turn_end_time = 0.0
        self.turn_time_left = 0
        self.reset_turn()

    def update_players(self, update):
        player_1 = self.game_state.p1
        player_2 = self.game_state.p2

        self.update_beetle_queue.put(("p1_gun", update["p1"]["bullets"]))
        self.update_beetle_queue.put(("p2_gun", update["p2"]["bullets"]))

        self.update_beetle_queue.put(("p1_vest", update["p1"]["hp"]))
        self.update_beetle_queue.put(("p2_vest", update["p2"]["hp"]))

        player_1.initialize_from_dict(update["p1"])
        player_2.initialize_from_dict(update["p2"])

    def reset_timer(self):
        self.turn_end_time = time.time() + TURN_MAX_TIME
        self.turn_time_left = TURN_MAX_TIME

    def reset_turn(self):
        self.reset_timer()
        self.complete = {"p1": False, "p2": False}

        self.signals = {
            "p1": {
                "action": Actions.no,
                "opp_hit": False,
                "opp_blasted": False,
            },
            "p2": {
                "action": Actions.no,
                "opp_hit": False,
                "opp_blasted": False,
            },
        }

    def check_turn(self, player, opp):
        if (
            (
                self.signals[player]["action"] == Actions.shoot
                and self.signals[player]["opp_hit"]
            )
            or self.signals[player]["action"] == Actions.grenade
            or self.signals[player]["action"] == Actions.reload
            or self.signals[player]["action"] == Actions.shield
        ):
            self.complete[player] = True

    def get_opp(self, player):
        return "p1" if player == "p2" else "p2"

    def is_complete(self):
        if TWO_PLAYER:
            if self.complete["p1"] and self.complete["p2"]:
                self.logs_queue.put("Both complete")
                return True
            # self.logs_queue.put("Not both complete")
            return False

        return self.complete["p1"] or self.complete["p2"]

    def is_turn_over(self):
        self.turn_time_left = self.turn_end_time - time.time()
        # self.logs_queue.put(f"Checking is turn over, time left = {self.turn_time_left}")
        # if self.turn_time_left <= 0:
        # self.logs_queue.put("turn is over")

        return self.turn_time_left <= 0

    def is_logged_out(self):
        return (
            self.game_state.p1.action == Actions.logout
            or self.game_state.p2.action == Actions.logout
        )

    def _run(self):
        game_state = self.game_state.get_dict()
        self.eval_req_console_queue.put(game_state)
        self.eval_resp_console_queue.put(game_state)
        self.reset_turn()
        game_start = True

        while game_start:
            if not self.action_queue.empty():
                # self.logs_queue.put("Getting from action queue")
                player, action = self.action_queue.get()
                opp = self.get_opp(player)
                self.logs_queue.put(player, action)

                # If new connection, action will be 'conn_<sensor>'
                conn_list = action.split("_", 1)
                if conn_list[0] == "conn":
                    self.logs_queue.put("New conn in gameengine")
                    sensor = conn_list[1]
                    data = getattr(
                        getattr(self.game_state, player), SENSOR_MAPPING[sensor]
                    )
                    self.logs_queue.put(SENSOR_MAPPING[sensor], "=", data)
                    self.update_beetle_queue.put((player + "_" + sensor, str(data)))
                    continue

                if action in Actions.all:
                    if self.signals[player]["action"] == Actions.no:
                        self.signals[player]["action"] = action
                        if self.signals[opp]["action"] == Actions.no:
                            self.reset_timer()
                elif action == Actions.hit:
                    if not self.signals[opp]["opp_hit"]:
                        self.signals[opp]["opp_hit"] = True
                        if self.signals[opp]["action"] == Actions.no:
                            self.reset_timer()

                self.check_turn("p1", "p2")
                self.check_turn("p2", "p1")

            if self.is_complete() or self.is_turn_over():
                action_p1 = self.signals["p1"]["action"]
                action_p2 = self.signals["p2"]["action"]

                if action_p1 == Actions.no and action_p2 == Actions.no:
                    self.reset_turn()
                    continue

                opp_hit_p1 = self.signals["p1"]["opp_hit"]
                opp_hit_p2 = self.signals["p2"]["opp_hit"]

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

                # self.logs_queue.put("[Game State Sent]:\n" + json.dumps(game_state, indent=4))
                self.eval_req_queue.put(game_state)
                self.eval_req_console_queue.put(game_state)
                updated_game_state = self.eval_resp_queue.get()
                self.eval_resp_console_queue.put(updated_game_state)

                self.update_players(updated_game_state)

                # Empty queue
                while not self.action_queue.empty():
                    self.action_queue.get()
                # self.logs_queue.put(
                #     "[Game State Updated]:\n"
                #     + json.dumps(self.game_state.get_dict(), indent=4)
                # )

                self.vis_queue.put(updated_game_state)

                if self.is_logged_out():
                    game_start = False

                self.reset_turn()

    def run(self):
        try:
            self.logs_queue.put("Game Engine Started")
            self._run()
        except KeyboardInterrupt:
            self.logs_queue.put("Game Engine Ended")
