import numpy as np
import pynq
from Helper import Actions


class HWAccel:
    def __init__(self) -> None:
        self.overlay = pynq.Overlay("mlp_design.bit")

        self.dma = self.overlay.axi_dma_0

        self.in_buffer = pynq.allocate(shape=(60,), dtype=np.double)
        self.out_buffer = pynq.allocate(shape=(4,), dtype=np.double)

    def get_action(self, msg):
        for i, value in enumerate(msg.split(",")):
            self.in_buffer[i] = value

        self.dma.sendchannel.transfer(self.in_buffer)
        self.dma.recvchannel.transfer(self.out_buffer)
        action = Actions.glove[self.out_buffer.argmax()]

        return action
