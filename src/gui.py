
import asyncio
from enum import Enum, auto
from typing import Tuple


import logging
import queue
import justpy as jp
# FOR FUTURE PROJECTS: check out the justpy.react functionality: https://justpy.io/blog/reactivity/


import unified_planning as up
from unified_planning.shortcuts import *

TOTAL_LOCATIONS = 10
TOTAL_PACKAGES = 5
TOTAL_TRUCKS = 3
TOTAL_AIRPLANES = 2

LOCATIONS_MAP = {
    "city_1": (1, 2, 3),
    "city_4": (4, 5, 6),
    "city_7": (7, 8, 9, 10),
}

DEFAULTS = {
    "packages": {
        1:  (1, 4),
        2:  (2, 5),
        3:  (2, 6),
        4:  (8, 4),
        5:  (8, 5),
    },
    "trucks": {
        1: (1, 1),
        2: (4, 4),
        3: (7, 8),
    },
    "airplanes": {
        1: (1, 1),
        2: (1, 4),
    }
}

BUTTON_CLASS = 'bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded m-2'


class Mode(Enum):
    GENERATING_PROBLEM = auto()
    OPERATING = auto()


class Gui():
    def __init__(self):
        # a queue where the interface waits the start
        self.start_queue = queue.Queue()

        self.mode = Mode.GENERATING_PROBLEM
        self.jp_components: Optional[Dict[str, Tuple[jp.Input, jp.Input]]] = None
        self.input_values: Dict[str, Tuple[int, int]] = {}

        self.plan = None
        self.plan_expected = False

        self.plan_div: Optional[jp.Div] = None

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.logger.setLevel(logging.INFO)
        return
        if self.graph_image_div is None:
            return
        if reset_plan:
            self.plan = None

        # from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        # self.graph_image_div.delete_components()
        # texts = [f"Locations: {', '.join(self.graph.nodes)}."]
        # texts.append(f"Start: {self.start}.")
        # texts.append(f"Destination: {self.destination}.")
        # for node, nbrdict in self.graph.adjacency():
        #     texts.append(f"{node} connected to: {', '.join(map(str, nbrdict.keys()))}.")

        # for t in texts:
        #     _ = jp.P(
        #         a=self.graph_image_div,
        #         text=t,
        #         classes=PLAN_PART_P_CLASS,
        #         style=PLAN_PART_P_STYLE,
        #     )
        # pos = nx.nx_agraph.graphviz_layout(self.graph, prog="twopi")
        # fig = plt.figure(figsize = FIGSIZE)
        # ax = fig.add_subplot()
        # color_map = {self.start: START_NODE_COLOR, self.destination: DESTINATION_NODE_COLOR}
        # if self.plan is not None:
        #     path = set((str(ai.actual_parameters[1]) for ai in self.plan.actions[0:-1]))
        #     node_colors = [color_map.get(n, NORMAL_NODE_COLOR) if n not in path else PATH_COLOR for n in self.graph ]
        # else:
        #     node_colors = [color_map.get(n, NORMAL_NODE_COLOR) for n in self.graph]

        # nx.draw(self.graph, pos, with_labels=True, font_weight='bold', ax=ax, node_color=node_colors, font_size=NODE_LABEL_FONT_SIZE, node_size=NODE_SIZE)
        # img_loc = f"{GRAPH_IMAGE_LOCATION}_{self.image_id}.png"
        # self.image_id += 1
        # fig.savefig(f".{img_loc}")

        # self.graph_image_div.delete_components()

        # _ = jp.Img(
        #     a=self.graph_image_div,
        #     src=f"static{img_loc}",
        #     style='max-width: 100%; height: auto;'
        # )

    def reset_execution(self):
        self.mode = Mode.GENERATING_PROBLEM
        self.components_disabled(False)

    def update_planning_execution(self):
        from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        if self.plan_div is not None:
            self.plan_div.delete_components()
            if self.plan is not None:
                _ = jp.P(
                    a=self.plan_div,
                    text=f"Found a plan!",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
                for action_instance in self.plan.actions:
                    text = write_action_instance(action_instance)
                    _ = jp.P(
                        a=self.plan_div,
                        text=text,
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
                _ = jp.P(
                    a=self.plan_div,
                    text=f"After this sequence all packages, trucks and airplanes are at the required destination!",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )

            elif self.plan_expected:
                if self.mode == Mode.GENERATING_PROBLEM:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="No plan found; Are you sure that every city has a truck to deliver packages and that Trucks are not required to move between different cities?",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
                else:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="Wait for planning to finish!",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
            else:
                single_p = jp.P(
                    a=self.plan_div,
                    text="Define start and destinations and press DELIVER!",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
            try:
                asyncio.run(self.plan_div.update())
            except RuntimeError:
                self.plan_div.update()

    def clear_activities_click(self, msg):
        self.logger.info("Clearing")
        if self.mode == Mode.GENERATING_PROBLEM:
            self.plan = None
            self.input_values = {}
            self.plan_expected = False
            self.update_planning_execution()

    def show_gui_thread(self):
        from main_page import main_page
        @jp.SetRoute("/")
        def get_main_page():
            return main_page(self)
        jp.justpy(get_main_page)

    def generate_problem_click(self, msg):
        self.logger.info("Generating")
        if self.mode == Mode.GENERATING_PROBLEM:
            self.mode = Mode.OPERATING
            self.components_disabled(True)
            if self.validate_input():
                self.logger.info("Valid input")
                self.plan = None
                self.plan_expected = True
                self.update_planning_execution()
                # unlock the planing method with the problem correctly generated
                self.start_queue.put(None)
            else:
                self.logger.info("Invalid input")
                self.mode = Mode.GENERATING_PROBLEM
                self.input_values = {}
                self.components_disabled(False)

    def components_disabled(self, disabled: bool):
        for c1, c2 in self.jp_components.values():
            c1.disabled = disabled
            c2.disabled = disabled

    def validate_input(self) -> bool:
        self.input_values = {}
        if self.jp_components is None:
            return False
        for k, (jp_start_text, jp_dest_text) in self.jp_components.items():
            start_text, dest_text = jp_start_text.value, jp_dest_text.value
            try:
                start_value = int(start_text)
            except ValueError:
                jp_start_text.value = "Err: NAN"
                return False
            if start_value < 1:
                jp_start_text.value = "Err: < 1"
                return False
            elif start_value > TOTAL_LOCATIONS:
                jp_start_text.value = f"Err: > {TOTAL_LOCATIONS}"
                return False
            try:
                dest_value = int(dest_text)
            except ValueError:
                jp_dest_text.value = "Err: NAN"
                return False
            if dest_value < 1:
                jp_dest_text.value = "Err: < 1"
                return False
            elif dest_value > TOTAL_LOCATIONS:
                jp_dest_text.value = f"Err: > {TOTAL_LOCATIONS}"
                return False
            self.input_values[k] = (start_value, dest_value)
        return True


def write_action_instance(action_instance: up.plans.ActionInstance) -> str:
    params = action_instance.actual_parameters
    if action_instance.action.name == "load":
        return f" - LOAD {params[0]} ONTO {params[1]} FROM {params[2]}"
    elif action_instance.action.name == "unload":
        return f" - UNLOAD {params[0]} FROM {params[1]} ONTO {params[2]}"
    elif action_instance.action.name == "move":
        return f" - {params[0]} : {params[1]} --> {params[2]}"
    elif action_instance.action.name == "fly-plane":
        return f" - {params[0]} : {params[1]} ---> {params[2]}"
    else:
        return str(action_instance)

async def reload_page():
    for page in jp.WebPage.instances.values():
        if page.page_type == 'main':
            await page.reload()
