from GameState import GameState


class GameEngine_Stub:
    def __init__(self, opp_in_frames, action_queue, eval_queue, vis_queue):
        self.game_state = GameState()
        self.action_queue = action_queue
        self.eval_queue = eval_queue
        self.vis_queue = vis_queue
        self.opp_in_frames = opp_in_frames

    def run(self):
        while True:
            self.action_queue.get()

            game_state = self.game_state.get_dict()
            self.eval_queue.put(game_state)
            self.vis_queue.put(game_state)
