
from typing import Dict, Tuple

import justpy as jp

from gui import Gui, TOTAL_PACKAGES, TOTAL_AIRPLANES, TOTAL_TRUCKS, DEFAULTS

LEFT_MARGIN, RIGHT_MARGIN = " margin-left: 10px; ", " margin-right: 20px; "

TITLE_DIV_CLASS = "grid justify-between gap-2 grid-cols-3"
TITLE_DIV_STYLE = "grid-template-columns: auto auto auto; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN

TITLE_TEXT_DIV_STYLE = "font-size: 80px; text-align: center; text-weight: bold;"

DESCRIPTION_STYLE = "margin-top: 15px; font-size: 16px;" + LEFT_MARGIN + RIGHT_MARGIN
DESCRIPTION_TEXT = """
Logistic demo: this demo allows you to create and solve a logistic problem.
In the problem you can specify the starting location of a package and the desired destination.
You can also do the same for trucks and planes.
 \n
The map represents 3 cities, each one with an airport (where the dashed line starts/ends) and some different locations.
 \n
Airplanes can move only between airports, while Trucks can move only in-between the same city.
"""
SINGLE_DESCRIPTION_STYLE = LEFT_MARGIN + RIGHT_MARGIN


MAIN_BODY_DIV_CLASS = "grid justify-between grid-cols-3 gap-7"
MAIN_BODY_DIV_STYLE = "grid-template-columns: max-content minmax(200px, 45%) 0.9fr; column-gap: 15px; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN
# MAIN_BODY_DIV_STYLE = "grid-template-columns: minmax(max-content, 25%) minmax(max-content, 25%) 10px minmax(max-content, 33%); width: 100vw; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN

ACTIONS_DIV_CLASS = "grid grid-cols-3"
# Setting height to 0 it'sa trick to solve the problem of the goal div changing size
ACTIONS_DIV_STYLE = f"column-gap: 4px; font-size: 30px; font-weight: semibold; height: 0px;"

HEADERS_P_CLASS = ""
HEADERS_P_STYLE = "font-size: 16px; font-weight: semibold;"

OBJECT_NAME_P_CLASS = ""
OBJECT_NAME_P_STYLE = "font-size: 16px; font-weight: normal; margin-top: 10px;"

TEXT_WIDTH = 100 # px
COL_GAP = 4 # px
TEXT_INPUT_P_CLASS = ""
TEXT_INPUT_P_STYLE = f"font-weight: normal; font-size: 16px; border: 0.9px solid #000; background-color: #e1eff7; padding: 5px; width: {TEXT_WIDTH}px; margin-top: 5px;"

ADD_BUTTON_CLASS = "bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded m-2"
ADD_BUTTON_STYLE = f"font-weight: semibold; font-size: 16px; width: {TEXT_WIDTH}px; margin-top: 5px;"

GOALS_DIV_CLASS = ""
GOALS_DIV_STYLE = "font-size: 30px; font-weight: semibold;"


GOALS_CONTAINER_DIV_CLASS = ""
GOALS_CONTAINER_DIV_STYLE = ""

CLEAR_SOLVE_BUTTONS_DIV_CLASS = "flex grid-cols-2"
CLEAR_SOLVE_BUTTONS_DIV_STYLE = f"column-gap: {COL_GAP}px;"

CLEAR_SOLVE_BUTTONS_CLASS = ADD_BUTTON_CLASS
CLEAR_SOLVE_BUTTONS_STYLE = "font-weight: semibold; font-size: 20px;"

PLAN_DIV_CLASS = ""
PLAN_DIV_STYLE = f"font-size: 30px; font-weight: semibold;"

PLAN_PART_P_CLASS = ""
PLAN_PART_P_STYLE = f"font-weight: normal; font-size: 18px;"


def main_page(gui: Gui):
    wp = jp.WebPage(delete_flag = False)
    wp.page_type = 'main'
    title_div = jp.Div(
        a=wp,
        classes=TITLE_DIV_CLASS,
        style=TITLE_DIV_STYLE,
    )
    fbk_logo_div = jp.Div(
        a=title_div,
        # text="FBK LOGO",
        # style="font-size: 30px;",
        style="height: 160px;",
    )
    fbk_logo = jp.Img(
        src="/static/logos/fbk.png",
        a=fbk_logo_div,
        classes="w3-image",
        # style="height: 100%; length: auto;",
    )
    title_text_div = jp.Div(
        a=title_div,
        text="LOGISTIC",
        style=TITLE_TEXT_DIV_STYLE,
    )
    unified_planning_logo_div = jp.Div(
        a=title_div,
        style="height: 160px;",
    )
    unified_planning = jp.Img(
        src="/static/logos/unified_planning_logo.png",
        a=unified_planning_logo_div,
        classes="w3-image",
        style="max-width: 100%; height: 160px;"
    )

    description_div = jp.Div(
        a=wp,
        style=DESCRIPTION_STYLE,
    )
    for single_desc in DESCRIPTION_TEXT.split("\n"):
        description_paragraph = jp.P(
            a=description_div,
            style=SINGLE_DESCRIPTION_STYLE,
            text=single_desc,
        )

    main_body_div = jp.Div(
        a=wp,
        classes=MAIN_BODY_DIV_CLASS,
        style=MAIN_BODY_DIV_STYLE,
    )

    actions_div = jp.Div(
        a=main_body_div,
        text="ACTIONS:",
        classes=ACTIONS_DIV_CLASS,
        style=ACTIONS_DIV_STYLE,
    )
    _ = jp.P(
        a=actions_div
    )
    _ = jp.P(
        a=actions_div
    )

    # Column Headers
    column_header_name = jp.P(
        a=actions_div,
        text="Object Name",
        classes=HEADERS_P_CLASS,
        style=HEADERS_P_STYLE,
    )
    column_header_start = jp.P(
        a=actions_div,
        text="Start",
        classes=HEADERS_P_CLASS,
        style=HEADERS_P_STYLE,
    )
    column_header_destination = jp.P(
        a=actions_div,
        text="Destination",
        classes=HEADERS_P_CLASS,
        style=HEADERS_P_STYLE,
    )
    jp_components: Dict[str, Tuple[jp.Input, jp.Input]] = {}
    pkg_default = DEFAULTS["packages"]
    for i in range(1, TOTAL_PACKAGES+1):
        package_i_text = jp.P(
            a=actions_div,
            text=f"Package {i}",
            classes=OBJECT_NAME_P_CLASS,
            style=OBJECT_NAME_P_STYLE,
        )
        package_i_start = jp.Input(
            a=actions_div,
            classes=TEXT_INPUT_P_CLASS,
            style=TEXT_INPUT_P_STYLE,
        )
        package_i_destination = jp.Input(
            a=actions_div,
            classes=TEXT_INPUT_P_CLASS,
            style=TEXT_INPUT_P_STYLE,
        )
        key = f"package_{i}"
        if gui.input_values:
            package_i_start.value, package_i_destination.value = gui.input_values[key]
        else:
            package_i_start.value, package_i_destination.value = map(str, pkg_default[i])
        jp_components[key] = (package_i_start, package_i_destination)
    trucks_default = DEFAULTS["trucks"]
    for i in range(1, TOTAL_TRUCKS+1):
        truck_i_text = jp.P(
            a=actions_div,
            text=f"Truck {i}",
            classes=OBJECT_NAME_P_CLASS,
            style=OBJECT_NAME_P_STYLE,
        )
        truck_i_start = jp.Input(
            a=actions_div,
            classes=TEXT_INPUT_P_CLASS,
            style=TEXT_INPUT_P_STYLE,
        )
        truck_i_destination = jp.Input(
            a=actions_div,
            classes=TEXT_INPUT_P_CLASS,
            style=TEXT_INPUT_P_STYLE,
        )
        key = f"truck_{i}"
        if gui.input_values:
            truck_i_start.value, truck_i_destination.value = gui.input_values[key]
        else:
            truck_i_start.value, truck_i_destination.value = map(str, trucks_default[i])
        jp_components[key] = (truck_i_start, truck_i_destination)
    airplanes_default = DEFAULTS["airplanes"]
    for i in range(1, TOTAL_AIRPLANES+1):
        airplane_i_text = jp.P(
            a=actions_div,
            text=f"Airplane {i}",
            classes=OBJECT_NAME_P_CLASS,
            style=OBJECT_NAME_P_STYLE,
        )
        airplane_i_start = jp.Input(
            a=actions_div,
            classes=TEXT_INPUT_P_CLASS,
            style=TEXT_INPUT_P_STYLE,
        )
        airplane_i_destination = jp.Input(
            a=actions_div,
            classes=TEXT_INPUT_P_CLASS,
            style=TEXT_INPUT_P_STYLE,
        )
        key = f"airplane_{i}"
        if gui.input_values:
            airplane_i_start.value, airplane_i_destination.value = gui.input_values[key]
        else:
            airplane_i_start.value, airplane_i_destination.value = map(str, airplanes_default[i])
        jp_components[key] = (airplane_i_start, airplane_i_destination)

    gui.jp_components = jp_components

    # placeholder
    _ = jp.P(
        a=actions_div
    )
    reset = jp.Input(
        a=actions_div,
        value="RESET",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    reset.on('click', gui.clear_activities_click)
    solve = jp.Input(
        a=actions_div,
        value="DELIVER",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    solve.on('click', gui.generate_problem_click)

    goals_div = jp.Div(
        a=main_body_div,
        text="MAP:",
        classes=GOALS_DIV_CLASS,
        style=GOALS_DIV_STYLE,
    )

    graph_image_div = jp.Div(
        a=goals_div,
        classes="",
        style="",
    )
    img = jp.Img(
        src="/static/logos/logistic_map.png",
        a=graph_image_div,
        classes="w3-image",
        style="max-width: 100%; height: 400px;"
    )
    plan_div = jp.Div(
        a=main_body_div,
        text="PLAN:",
        classes=PLAN_DIV_CLASS,
        style=PLAN_DIV_STYLE,
    )
    gui.plan_div = plan_div

    gui.update_planning_execution()

    return wp
