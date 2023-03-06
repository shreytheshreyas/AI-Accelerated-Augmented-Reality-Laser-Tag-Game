import random


class HWAccel_Stub:
    def get_action(self, msg):
        index = int(msg)
        actions = ["grenade", "shield", "reload"]
        return actions[index]
