import logging
from up_graphene_engine.engine import  GrapheneEngine
from gui import Gui, LOCATIONS_MAP

from unified_planning.shortcuts import *
from unified_planning.model.htn import *
import unified_planning as up
import unified_planning.model.metrics

get_environment().credits_stream = None


def planning(engine: GrapheneEngine, gui: Gui, reload_page):
    logging.info("Generating planning problem...")
    gui.logger.info("Generating planning problem...")
    gui.logger.info(f"with input: {gui.input_values}")

    pb = HierarchicalProblem()  # make it hierarchical instead

    Package = UserType("Package")

    PackageLoc = UserType("PackageLoc")
    Loc = UserType("Location", father=PackageLoc)
    Airport = UserType("Airport", father=Loc)
    City = UserType("City")

    Vehicle = UserType("Vehicle", father=PackageLoc)
    Truck = UserType("Truck", father=Vehicle)
    Airplane = UserType("Airplane", father=Vehicle)
    # city of location
    city = pb.add_fluent("city", City, of=Loc)

    # current location of package / vehicle
    loc = pb.add_fluent("loc", PackageLoc, package=Package)
    at = pb.add_fluent("at", Loc, vehicle=Vehicle)

    load = InstantaneousAction("load", package=Package, vehicle=Vehicle, l=Loc)
    load.add_precondition(Equals(at(load.vehicle), load.l))
    load.add_precondition(Equals(loc(load.package), load.l))
    load.add_effect(loc(load.package), load.vehicle)  # package now in vehicle
    pb.add_action(load)

    unload = InstantaneousAction("unload", package=Package, vehicle=Vehicle, l=Loc)
    unload.add_precondition(Equals(at(unload.vehicle), unload.l))
    unload.add_precondition(Equals(loc(unload.package), unload.vehicle))
    unload.add_effect(loc(unload.package), unload.l)
    pb.add_action(unload)

    move = InstantaneousAction("move", truck=Truck, src=Loc, tgt=Loc)
    move.add_precondition(Equals(city(move.src), city(move.tgt)))
    move.add_precondition(Equals(at(move.truck), move.src))
    move.add_effect(at(move.truck), move.tgt)
    pb.add_action(move)

    fly_plane = InstantaneousAction("fly-plane", plane=Airplane, src=Airport, tgt=Airport)
    fly_plane.add_precondition(Equals(at(fly_plane.plane), fly_plane.src))
    fly_plane.add_effect(at(fly_plane.plane), fly_plane.tgt)
    pb.add_action(fly_plane)

    # Task representing the objective of getting a given truck to a particular location
    bring_truck = pb.add_task("bring-truck", truck=Truck, destination=Loc)

    # Option 1: truck already at destination location, nothing to do
    m = Method("bring-truck-noop", truck=Truck, dest=Loc)

    # declares that m achieves the `bring-truck(truck, dest)` task`
    m.set_task(bring_truck, m.truck, m.dest)

    pb.add_method(m)

    # only usable if the truck is already at the right location
    # no subtasks, implying that if the method is usable, there is nothing left to do
    m.add_precondition(Equals(at(m.truck), m.dest))

    # Option 2: truck not at target location, move it
    m = Method("bring-truck-move", truck=Truck, orig=Loc, dest=Loc)
    # declares that m achieves the `bring-truck(truck, to)` task`
    m.set_task(bring_truck, m.truck, m.dest)

    m.add_precondition(Equals(at(m.truck), m.orig))      # restrict applicability to cases where the truck is
    m.add_precondition(Not(Equals(m.orig, m.dest)))        # in a different location
    m.add_precondition(Equals(city(m.orig), city(m.dest))) # of the same city

    # accomplishing this method requires executing a `move` action
    m.add_subtask(move, m.truck, m.orig, m.dest, ident="move-subtask")

    pb.add_method(m)

    # Task for transporting a given package to a given location,
    # This method assumes that the package is already in the right city
    transport_in_city = pb.add_task("transport-in-city", package=Package, destination=Loc)

    # Method 1: handling the case where the package is already at the destination
    m = Method("transport-in-city-noop", package=Package, to=Loc)
    m.set_task(transport_in_city, m.package, m.to)  # set the task that this method achieve
    m.add_precondition(Equals(loc(m.package), m.to))  # only allow using this method if the package is already at the destination
    # note: no subtasks are added => nothing to do in this method
    pb.add_method(m)

    m = Method("transport-in-city-truck", package=Package, orig=Loc, to=Loc, truck=Truck)
    m.set_task(transport_in_city, m.package, m.to)
    m.add_precondition(Equals(loc(m.package), m.orig)) # package is at origin
    m.add_precondition(Not(Equals(m.orig, m.to)))
    m.add_precondition(Equals(city(m.orig), city(m.to)))  # destination is the same city

    # this method decomposed into a sequence of 4 subtasks (mixing the load/unload action and the 'bring-truck' task)
    t1 = m.add_subtask(bring_truck, m.truck, m.orig)  # bring truck to package location
    t2 = m.add_subtask(load, m.package, m.truck, m.orig)  # load package in truck
    t3 = m.add_subtask(bring_truck, m.truck, m.to)  # bring truck to target location
    t4 = m.add_subtask(unload, m.package, m.truck, m.to)  # unload package at target location
    m.set_ordered(t1, t2, t3, t4)  # enforce all 4 subtasks to be done in this order
    pb.add_method(m)

    # bring airplane subtask
    # Task representing the objective of getting a given airplane to a particular location
    bring_airplane = pb.add_task("bring-airplane", airplane=Airplane, destination=Airport)

    # Option 1: truck already at destination location, nothing to do
    m = Method("bring-airplane-noop", airplane=Airplane, dest=Airport)

    # declares that m achieves the `bring-truck(truck, dest)` task`
    m.set_task(bring_airplane, m.airplane, m.dest)

    # only usable if the airplane is already at the right airport
    # no subtasks, implying that if the method is usable, there is nothing left to do
    m.add_precondition(Equals(at(m.airplane), m.dest))

    pb.add_method(m)

    # Option 2: airplane not at target airport, move it
    m = Method("bring-airplane-fly", airplane=Airplane, orig=Airport, dest=Airport)
    # declares that m achieves the `bring-airplane(airplane, to)` task`
    m.set_task(bring_airplane, m.airplane, m.dest)

    m.add_precondition(Equals(at(m.airplane), m.orig))      # restrict applicability to cases where the airplane is
    m.add_precondition(Not(Equals(m.orig, m.dest)))        # in a different location

    # accomplishing this method requires executing a `move` action
    m.add_subtask(fly_plane, m.airplane, m.orig, m.dest, ident="fly-subtask")

    pb.add_method(m)

    # Task for transporting a given package to a given Airport,
    transport_outside_city = pb.add_task("transport-outside-city", package=Package, destination=Airport)

    # Method 1: handling the case where the package is already at the destination
    m = Method("transport-outside-city-noop", package=Package, to=Airport)
    m.set_task(transport_outside_city, m.package, m.to)  # set the task that this method achieve
    m.add_precondition(Equals(loc(m.package), m.to))  # only allow using this method if the package is already at the destination
    # note: no subtasks are added => nothing to do in this method
    pb.add_method(m)

    m = Method("transport-outside-city-airplane", package=Package, orig=Airport, to=Airport, airplane=Airplane)
    m.set_task(transport_outside_city, m.package, m.to)
    m.add_precondition(Equals(loc(m.package), m.orig)) # package is at origin
    m.add_precondition(Not(Equals(m.orig, m.to)))

    # this method decomposed into a sequence of 4 subtasks (mixing the load/unload action and the 'fly-airplane' task)
    t1 = m.add_subtask(bring_airplane, m.airplane, m.orig)  # bring airplane to package location
    t2 = m.add_subtask(load, m.package, m.airplane, m.orig)  # load package in airplane
    t3 = m.add_subtask(bring_airplane, m.airplane, m.to)  # bring airplane to target location
    t4 = m.add_subtask(unload, m.package, m.airplane, m.to)  # unload package at target location
    m.set_ordered(t1, t2, t3, t4)  # enforce all 4 subtasks to be done in this order
    pb.add_method(m)

    # Task for transporting a given package to a given Loc,
    transport_package = pb.add_task("transport-package", package=Package, destination=Loc)

    m = Method("transport-package-noop", package=Package, to=Loc)
    m.set_task(transport_package, m.package, m.to)
    m.add_precondition(Equals(loc(m.package), m.to)) # package is at origin
    pb.add_method(m)

    m = Method("transport-package-truck", package=Package, orig=Loc, to=Loc, truck=Truck)
    m.set_task(transport_package, m.package, m.to)
    t1 = m.add_subtask(transport_in_city, m.package, m.to)
    pb.add_method(m)

    m = Method("transport-package-airplane", package=Package, to=Loc, intermediate=Airport)
    m.set_task(transport_package, m.package, m.to)
    m.add_precondition(Equals(city(m.intermediate), city(m.to)))
    t1 = m.add_subtask(transport_outside_city, m.package, m.intermediate)
    t2 = m.add_subtask(transport_in_city, m.package, m.to)
    m.set_ordered(t1, t2)
    pb.add_method(m)

    m = Method("transport-package-truck-airplane", package=Package, orig=Loc, to=Loc, orig_airport=Airport, to_airport=Airport)
    m.set_task(transport_package, m.package, m.to)
    m.add_precondition(Equals(city(m.orig), city(m.orig_airport)))
    m.add_precondition(Equals(city(m.to_airport), city(m.to)))
    t1 = m.add_subtask(transport_in_city, m.package, m.orig_airport)
    t2 = m.add_subtask(transport_outside_city, m.package, m.to_airport)
    t3 = m.add_subtask(transport_in_city, m.package, m.to)
    m.set_ordered(t1, t2, t3)
    pb.add_method(m)

    locations_id_mapping: Dict[int, Object] = {}
    for city_name, locations in LOCATIONS_MAP.items():
        if not locations:
            continue
        city_object = pb.add_object(city_name, City)
        airport_id = locations[0]
        airport_name = f"airport_{airport_id}"
        airport_object = pb.add_object(airport_name, Airport)
        pb.set_initial_value(city(airport_object), city_object)
        assert airport_id not in locations_id_mapping
        locations_id_mapping[airport_id] = airport_object
        for location_id in locations[1:]:
            location_name = f"location_{location_id}"
            location_object = pb.add_object(location_name, Loc)
            pb.set_initial_value(city(location_object), city_object)
            assert location_id not in locations_id_mapping
            locations_id_mapping[location_id] = location_object
    object_type_map = {
        "package": Package,
        "truck": Truck,
        "airplane": Airplane,
    }
    # for object_name, start_dest_ids in default.items():
    for object_name, start_dest_ids in gui.input_values.items():
        start, dest = map(locations_id_mapping.get, start_dest_ids)
        object_type = object_type_map.get(object_name.split("_")[0], None)
        assert object_type is not None, f"Error: undefined object type for {object_name}"
        obj = pb.add_object(object_name, object_type)
        if object_type == Package:
            pb.set_initial_value(loc(obj), start)
            pb.task_network.add_subtask(transport_package, obj, dest)
            pb.add_goal(Equals(loc(obj), dest))
        else:
            pb.set_initial_value(at(obj), start)
            pb.add_goal(Equals(at(obj), dest))
            if obj.type == Truck:
                pb.task_network.add_subtask(bring_truck, obj, dest)
            if obj.type == Airplane:
                pb.task_network.add_subtask(bring_airplane, obj, dest)

    logging.info("Planning...")
    gui.logger.info("Planning...")

    res = engine.solve(pb)
    plan = res.plan
    gui.logger.info("Received result...")

    if plan is not None:
        try:
            plan = plan.convert_to(PlanKind.SEQUENTIAL_PLAN, pb)
        except Exception as e:
            tt_plan = plan.convert_to(PlanKind.TIME_TRIGGERED_PLAN, pb)
            plan = up.plans.SequentialPlan([a for _, a, _ in tt_plan.timed_actions])
    gui.logger.info("Returning plan..")
    gui.logger.info(str(plan))
    gui.logger.info(str(res))
    return plan
