import random


class HWAccel_Stub:
    def get_action(self, msg):
        _ = msg
        actions = ["grenade", "shield", "reload"]
        return actions[random.randint(0, 2)]
