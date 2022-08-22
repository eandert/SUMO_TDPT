#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2018 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    runner_tptd.py
# @author  Edward Andert
# @date    2009-03-26
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import time
import xml_parser
import input_output_parsing
import random

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa
import sumolib.net  # noqa


def engage_timer():
    return time.time()


def calculate_and_print_time(start):
    elapsed_time = time.time() - start
    print(" ::::Elapsed Time: ", elapsed_time)


def run(simulation, test_settings_container, thread_management_sheet):
    """execute the TraCI control loop"""
    step = 0

    # Error check to make sure we do not overrun our constraints
    if (test_settings_container.cavProbability + test_settings_container.avProbability) > 1:
        return "Error totalOBDs + totalAVs exceeds 1 which is the max probability"

    # Record this for completion time estimate
    firstCheckTime = engage_timer()
    lastCheckTime = time.time()
    fiveMinuteTester = engage_timer()

    checkedList= []
    av_list_all = []
    cav_list_all = []
    totalAVs = 0
    totalCAVs = 0
	
	# TODO: change this to seed w/ the test number
    random.seed(10)

    while simulation.simulation.getMinExpectedNumber() > 0:

        vehicleIDList = simulation.vehicle.getIDList()

        # Send the routes but only those that are from newly added vehicles
        curList = [x for x in vehicleIDList if x not in checkedList]

        # Calculate if the vehicle is an AV due to probability
        # Also calculate if the vehicle is an CAV due to probability
        if step >= 1:
            for count in range(0, len(curList)):
                randomnum = random.random()
                if (test_settings_container.avProbability != 0) and (randomnum <= test_settings_container.avProbability):
                    try:
                        # Change the vehicle type to AV
                        if test_settings_container.trafficSet:
                            simulation.vehicle.setType(curList[count], "AV_passenger_conservative")
                        else:
                            simulation.vehicle.setType(curList[count], "AV_passenger")
                        print("AV added: ", curList[count])
                        totalAVs = totalAVs + 1
                        # This is an AV, add to AV list
                        av_list_all.append(curList[count])
                    except:
                        print("Couldn't add AV ")
                # (randomnum > testContainer.avProbability) is implied here because it passed the first if statement
                elif (test_settings_container.cavProbability != 0) and (randomnum <= (test_settings_container.cavProbability)):
                    try:
                        # Change the vehicle type to CAV
                        simulation.vehicle.setType(curList[count], "CAV_passenger")
                        print("CAV added:" , curList[count])
                        totalCAVs = totalCAVs + 1
                        # Add to CAV list
                        cav_list_all.append(curList[count])
                    except:
                        print("Couldn't add CAV ")

            checkedList = checkedList + curList

        # We need to know which vehicle id are currently active
        av_list = list(set(av_list_all) & set(vehicleIDList))
        cav_list = list(set(cav_list_all) & set(vehicleIDList))

        # Car following model modification
        if not test_settings_container.trafficSet:
            try:
                for av in av_list:
                    velocity = simulation.vehicle.getSpeed(av)
                    emergency_decel = simulation.vehicle.getEmergencyDecel(av)
                    rss_time = velocity/emergency_decel + 0.1
                    simulation.vehicle.setTau(av, rss_time)
            except:
                print("AV missing ", cav)

        for cav in cav_list:
            try:
                leader = simulation.vehicle.getLeader(cav)
                velocity = simulation.vehicle.getSpeed(cav)
                if leader != None and leader[0] != "" and leader[0] in cav_list and leader[1] <= (3*velocity):
                    # Closely follow since this is another CAV
                    simulation.vehicle.setTau(cav, 0.5)
                else:
                    velocity = simulation.vehicle.getSpeed(cav)
                    emergency_decel = simulation.vehicle.getEmergencyDecel(cav)
                    rss_time = velocity/emergency_decel + 0.1
                    simulation.vehicle.setTau(cav, rss_time)
            except:
                print("CAV missing ", cav)
    
        checkTime = engage_timer()
        print ( "Step " , step )
        
        simulation.simulationStep()
        
        # Finally we have finished an iteration, increment step
        step += 1
        
        print ( " Simulation step completed in ", end = '')
        calculate_and_print_time(checkTime)
        
        # Calculating expected completion time
        print ( " Current loop time (seconds): " , time.time() - lastCheckTime)
        lastCheckTime = time.time()
        elapsed_time = lastCheckTime - firstCheckTime
        if step > 0:
            estimator = elapsed_time/(step*test_settings_container.timestep)
            print ( " Average loop execution time (seconds): " , estimator)
            estimator = estimator*((4200/test_settings_container.timestep)-step)/60 # Our tests are currently averaging about 3600 second + 200
            print ( " Estimated completion time (minutes): " , estimator)
            
        if (lastCheckTime-fiveMinuteTester) >= 300:
            fiveMinuteTester = lastCheckTime
            # Write the thread info to sheets if it is set
            test_settings_container.writeThreadUpdateSheets(thread_management_sheet, lastCheckTime, step)

    # This holder holds all of our stats
    return_stats = {
        "step": 0,
        "totalVehicles": 0,
        "totalAVs": totalAVs,
        "totalCAVs": totalCAVs,
    }

    sys.stdout.flush()
    
    return return_stats


def get_options():
    optParser = optparse.OptionParser()
    # Overall options that apply to entire test
    optParser.add_option("--gui", action="store_true", default=False, help="run the commandline version of sumo")
    optParser.add_option("--filename", type="string", dest="filename", help="Name of file to output to")
    optParser.add_option("--portid", type="int", dest="portid", help="Name of the port id to use for comms between sumo, this must be changed if running parallel tests")
    optParser.add_option("--mapname", type="string", dest="mapname", help="Name of map file to read")
    # Spread test multi options
    optParser.add_option("--testname", type="string", dest="testname", help="Name of file to read test data from")
    optParser.add_option("--thread_management_sheet", type="string", dest="thread_management_sheet", help="Google sheets ID for the sheet to monitor threads")
    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.gui:
        sumoBinary = checkBinary('sumo-gui')
    else:
        sumoBinary = checkBinary('sumo')

    # Name of the simulation so that we do not conflict with any other SUMO instances
    simulationName = "simulation" + str(options.portid)
    testPortID = options.portid

    outputFileName = "../output/" + options.filename + "_spread_scale.csv"
    xmlFileName = "../output/" + options.filename + "_" + str(testPortID) + "_"

    # Create the test container
    test_settings_container = input_output_parsing.ATLASTestContainer(testPortID)

    if len(options.testname) <= 0:
        print ( "ERROR: test name required " )
        sys.exit(-99)

    # Write the thread header to sheets if it is set
    test_settings_container.writeThreadStartSheets(options.thread_management_sheet, time.time())

    runIDX = 0

    # Infinite while to keep checking for tests
    while 1:
        while test_settings_container.readNextInputParallelGoogleSheets(options.testname) == True:

            temp_xml_file_name = xmlFileName + str(runIDX) + "simulation_tripinfo.xml"
            temp_crash_xml_file_name = xmlFileName + str(runIDX) + "simulation_crashinfo.xml"

            # Write the thread info to sheets if it is set
            test_settings_container.writeThreadUpdateSheets(options.thread_management_sheet, time.time(), 0)

            # this is the normal way of using traci. sumo is started as a
            # subprocess and then the python script connects and runs
            if test_settings_container.logEmisisonsData:
                traci.start([sumoBinary, "-c", test_settings_container.simmapname,
                             "--collision-output", temp_crash_xml_file_name,
                             "--collision.action", "teleport",
                             "--duration-log.statistics", "--tripinfo-output", temp_xml_file_name,
                             "--device.emissions.probability", "1.0", "--scale", str(test_settings_container.scale),
                             "--step-length", str(test_settings_container.timestep)], label=simulationName)
            else:
                # We are not logging anything unnecessary to reduce the workload
                traci.start([sumoBinary, "-c", test_settings_container.simmapname,
                            "--scale", str(test_settings_container.scale), "--step-length", str(test_settings_container.timestep)], label=simulationName)

            # Select the correct traci
            simulation = traci.getConnection(simulationName)

            # Run the simulator
            returnedData = run(simulation, test_settings_container, options.thread_management_sheet)

            # Sleep here to allow for data export from the controller
            time.sleep(2)

            # Close and sleep for some time to allow time for the server to reset
            traci.close()
            
            time.sleep(5)

            # Parse our output file and get the data
            try:
                if test_settings_container.logEmisisonsData:
                    sumoparser = xml_parser.SUMOOutputParser(temp_xml_file_name)
                    xmlData = sumoparser.returnParsedDataGoogleSheets()
                    sumoparser2 = xml_parser.CollisionOutputParser(temp_crash_xml_file_name)
                    collisions = sumoparser2.returnParsedData()
            except Exception as e:
                print ( e )
                xmlData = ["xml data error"]

            if test_settings_container.logEmisisonsData:
                test_settings_container.writeOutputFileGoogleSheets(returnedData, options.filename, xmlData, collisions)
            else:
                test_settings_container.writeOutputFileGoogleSheets(returnedData, options.filename, None, None)

            runIDX = runIDX + 1
            time.sleep(2)

        print ( "All tests complete! Checking again in 5 minutes... ")

        test_settings_container.writeThreadUpdateSheets(options.thread_management_sheet, time.time(), 0)

        time.sleep(300)

        # Reset the test parser index so we begin again
        test_settings_container.testIdx = 0

    # Send the successful exit command
    sys.exit(99)
