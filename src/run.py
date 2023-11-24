import os

# curr_dir = os.path.dirname(os.path.abspath(__file__))
# tsb_space_src_dir = os.path.join(curr_dir, '..', 'tsb-space', 'src')
# models_dir = os.path.join(tsb_space_src_dir, '..', 'models')

# import sys
# print("added path = ",tsb_space_src_dir)
# sys.path.append(tsb_space_src_dir)


import asyncio

from up_graphene_engine.engine import GrapheneEngine


from gui import Gui, reload_page
from modified_planning import planning
from threading import Thread



def main():

    engine = GrapheneEngine(port=8061)

    gui = Gui()

    gui_thread = Thread(target=gui.show_gui_thread)
    gui_thread.start()

    while True:
        # wait for the user input to start planning
        gui.start_queue.get(block=True)
        gui.plan = planning(engine, gui, reload_page)

        gui.update_planning_execution()

        gui.reset_execution()
        asyncio.run(reload_page())


    server.wait_for_termination()

    gui_thread.join()

if __name__ == "__main__":
    # asyncio.run(main())
    main()
