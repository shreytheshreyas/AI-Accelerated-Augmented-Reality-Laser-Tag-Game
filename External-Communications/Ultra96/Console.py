import time

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel


class ConsoleInterface:
    LOG_HEIGHT = 27
    CONN_HEIGHT = 6
    GAMESTATE_HEIGHT = 18
    NUM_ACTIONS = 3
    COMPONENT_NAMES = ["Gun", "Vest", "Glove"]

    def __init__(
        self, connected, opp_in_frames, action_queue, gs_queue, eval_gs_queue, log_queue
    ):
        self.console = Console()
        self.connected = connected
        self.opp_in_frames = opp_in_frames
        self.gs_queue = gs_queue
        self.eval_gs_queue = eval_gs_queue
        self.action_queue = action_queue
        self.logs_queue = log_queue
        self.actions = {"p1": [], "p2": []}

        self.info_panel = Panel(
            "",
            title="Players Info",
            border_style="green",
            height=self.GAMESTATE_HEIGHT + 2,
        )

        self.logs_panel = Panel(
            "",
            title="Logs",
            border_style="blue",
            height=self.LOG_HEIGHT + 2,
        )

        self.game_state_panel = Panel(
            "",
            title="Game State",
            border_style="magenta",
            height=self.GAMESTATE_HEIGHT + 2,
        )

        self.eval_game_state_panel = Panel(
            "",
            title="Evaluation Game State",
            border_style="yellow",
            height=self.GAMESTATE_HEIGHT + 2,
        )

        self.layout = Layout()
        self.layout.split(
            Layout(name="main"),
            Layout(name="logs"),
            splitter="column",
        )

        self.layout["main"].split(
            self.info_panel,
            self.game_state_panel,
            self.eval_game_state_panel,
            splitter="row",
        )
        self.layout["main"].minimum_size = self.GAMESTATE_HEIGHT + 2
        self.layout["logs"].split(self.logs_panel)
        self.layout["logs"].ratio = 2

        self.game_state = {}
        self.eval_game_state = {}

    def pretty_print_dict(self, d, indent=0):
        output = ""
        for key, value in d.items():
            output += f"{' ' * indent}{key}: "
            if isinstance(value, dict):
                output += "\n" + self.pretty_print_dict(value, indent + 2)
            else:
                output += f"{value}\n"
        return output

    def get_game_state_strs(self, game_state, eval_game_state):
        gs_list = self.pretty_print_dict(game_state, 0).split("\n")
        eval_gs_list = self.pretty_print_dict(eval_game_state, 0).split("\n")

        gs_str = ""
        eval_gs_str = ""
        for gs_line, eval_gs_line in zip(gs_list, eval_gs_list):
            if gs_line == eval_gs_line:
                if gs_line == "p1: ":
                    gs_line = "[blue bold underline]Player 1:[/]"
                    eval_gs_line = "[blue bold underline]Player 1:[/]"
                elif gs_line == "p2: ":
                    gs_line = "[blue bold underline]Player 2:[/]"
                    eval_gs_line = "[blue bold underline]Player 2:[/]"

                gs_str += gs_line + "\n"
                eval_gs_str += eval_gs_line + "\n"
            else:
                gs_str += f"[red]{gs_line}[/]\n"
                eval_gs_str += f"[red]{eval_gs_line}[/]\n"

        return gs_str, eval_gs_str

    def get_info_str(self):
        info_str = ""
        with self.connected.get_lock():
            info_str += "[blue bold underline]Player 1:[/]\n"
            for index, component in enumerate(self.COMPONENT_NAMES):
                info_str += f"{component}: {'[bold green]Connected' if self.connected[index] else '[bold red]Disconnected'}[/]\n"

        with self.opp_in_frames.get_lock():
            info_str += f"Opp In Frame: {'[bold green]True' if self.opp_in_frames[0] else '[bold red]False'}[/]\n"

        info_str += "[underline]Last Actions:[/]\n"
        for index, action in enumerate(self.actions["p1"][::-1]):
            info_str += f"  {action}\n"
        for _ in range(self.NUM_ACTIONS - len(self.actions["p1"])):
            info_str += "\n"

        with self.connected.get_lock():
            info_str += "[blue bold underline]Player 2:[/]\n"
            for index, component in enumerate(self.COMPONENT_NAMES):
                info_str += f"{component}: {'[bold green]Connected' if self.connected[3+index] else '[bold red]Disconnected'}[/]\n"

        with self.opp_in_frames.get_lock():
            info_str += f"Opp In Frame: {'[bold green]True' if self.opp_in_frames[1] else '[bold red]False'}[/]\n"

        info_str += "[underline]Last Actions:[/]\n"
        for index, action in enumerate(self.actions["p2"][::-1]):
            info_str += f"  {action}\n"
        for _ in range(self.NUM_ACTIONS - len(self.actions["p2"])):
            info_str += "\n"

        return info_str

    def get_log_str(self, new_log):
        logs_str = str(self.logs_panel.renderable)
        logs_str += "\n" + new_log
        lines = logs_str.split("\n")
        if len(lines) >= self.LOG_HEIGHT:
            logs_str = "\n".join(lines[-self.LOG_HEIGHT :])
        return logs_str

    def update_panels(self):
        while not self.gs_queue.empty():
            self.game_state = self.gs_queue.get()

        while not self.eval_gs_queue.empty():
            self.eval_game_state = self.eval_gs_queue.get()

        gs_str, eval_gs_str = self.get_game_state_strs(
            self.game_state, self.eval_game_state
        )

        self.game_state_panel.renderable = gs_str
        self.eval_game_state_panel.renderable = eval_gs_str

        while not self.action_queue.empty():
            player, action = self.action_queue.get()
            if len(self.actions[player]) == self.NUM_ACTIONS:
                self.actions[player].pop(0)
            self.actions[player].append(action)

        self.info_panel.renderable = self.get_info_str()

        while not self.logs_queue.empty():
            new_log = self.logs_queue.get()
            self.logs_panel.renderable = self.get_log_str(new_log)

    def _run(self):
        self.console.print(self.layout)

        with Live(self.layout, screen=True):
            while True:
                self.update_panels()
                time.sleep(1)

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            time.sleep(3)
            self.update_panels()
            time.sleep(5)
