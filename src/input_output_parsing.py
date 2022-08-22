from filelock import FileLock
import csv
import sys
import time
import statistics
import operator
import gspread
import math
from oauth2client.service_account import ServiceAccountCredentials

class ATLASTestContainer:
    def __init__(self, processID):
        self.processID = processID
        self.proccessed = 0
        self.testIdx = -1
        self.threadInfoRow = -1
        self.expectedLength = 9
        
        # Stored whether the last read was valid or not
        self.validTest = False
        self.workingOn = -1
        
        # Names
        self.mapname = None
        self.simmapname = None
        
        # Percentages 0.0 - 1.0 (FP)
        self.avProbability = 0.0
        self.cavProbability = 0.0
        
        # Integers
        self.scale = 0
        self.trafficSet = 0

        # Floating Points
        self.timestep = 1.0
        self.trafficLightViewDistance = 0.0
        
        # Booleans
        self.logEmisisonsData = False

        # Do not change
        self.working_on_id = 10
        
        # Header to be reused in the results
        self.fileHeader = "AV Probability, CAV Probability, Scale, Step Count, Total Vehicles, Total AVs, Total CAVs," + "totalVehicles,totalTimeLoss,averageTimeLoss,averagewaitingTime,waitingTimeSTDDev,totalWaitingTime,averageSpeed,noramlizedDurationSTDDev,noramlizedDurationMean,minTimeLoss,maxTimeLoss,average co2,average co,average hc,average nox,average pmx,fuel usage,electicity usage" + '\n'
        
    def testInputFile(self, inputFile):
        if len(inputFile) != self.expectedLength:
            print ( "ERROR: not enough rows in options list, should be ", self.expectedLength, " got ", len(inputFile))
            return False
        lengthTest = len(inputFile[0])
        for each in inputFile:
            if lengthTest == len(each):
                pass
            else:
                print ( "ERROR: mismatch of lengths of rows options lists " )
                return False
        return True

    def readNextInputParallel(self, filename):
        lock_path = filename + ".lock"
        lock = FileLock(lock_path)
        with lock:
            # work with the file as it is now locked
            print("Lock acquired.")
            # Read the csv file containing all of our test data
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                inputList = list(reader)
                
                if self.testInputFile(inputList) == False:
                    self.validTest = False
                    return False
                
                self.testIdx = -1
                # This row contains the iterations left to complete
                for idx, iterationsLeft in enumerate(inputList[0][1:]):
                    if int(iterationsLeft) > 0:
                        # Offset for the fact we started at idx = 1
                        self.testIdx = idx + 1
                        break
                
                # Remove the iteration from the counter
                inputList[0][self.testIdx] = int(inputList[0][self.testIdx]) - 1
                
                # Add our instance to the working flags
                inputList[self.expectedLength-1][self.testIdx] = int(inputList[self.expectedLength-1][self.testIdx]) + 1
                
                # Remove our old working flag if there is one
                if self.workingOn != -1:
                    # Here we are removing our working on flag from the list
                    inputList[self.expectedLength-1][self.workingOn] = int(inputList[self.expectedLength-1][self.workingOn]) - 1
                
                print ( inputList )
                
            with open(filename, 'w', newline='') as file:
                # Write back the csv lines with the modified durations remaining
                writer = csv.writer(file)
                writer.writerows(inputList)
            
        # Get the test values
        if self.testIdx != -1:
            # Names
            self.mapname = inputList[1][self.testIdx]
            self.simmapname = self.mapname + "/osm.sumocfg"
            self.avProbability = float(inputList[2][self.testIdx])
            self.cavProbability = float(inputList[3][self.testIdx])
            self.scale = float(inputList[4][self.testIdx])
            self.timestep = float(inputList[5][self.testIdx])
            self.trafficSet = int(inputList[6][self.testIdx])
            self.logEmisisonsData = int(inputList[7][self.testIdx])
            
            self.validTest = True
            self.workingOn = self.testIdx
            return True
        else:
            self.validTest = False
            self.workingOn = -1
            return False

    def tryread(self, worksheet, row, col):
        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                return worksheet.cell(row, col).value
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...7")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...8", str(e) )
            
    def tryupdate(self, worksheet, row, col, val):
        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                worksheet.update_cell(row, col, val)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...9")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...10", str(e) )
                    
    def trygetworksheet(self, sheet, num):
        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                return sheet.get_worksheet(num)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...11")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...12", str(e) )
                    
    def trygetfile(self, gc, filename):
        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                return gc.open_by_key(filename)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...13")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...14", str(e) )
                    
    def trygetauthorization(self, gspread, credentials):
        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                return gspread.authorize(credentials)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...15")
                    time.sleep(10)
                elif str(e).find("TimeoutError")>-1:
                    print ("TimeoutError...16")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...17", str(e) )
            
    def readNextInputParallelGoogleSheets(self, filename):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('../credentials/sheets_credentials.json', scope)

        gc = self.trygetauthorization(gspread, credentials)

        # If you want to be specific, use a key (which can be extracted from
        # the spreadsheet's url)
        #sheet = gc.open_by_key(filename)
        sheet = self.trygetfile(gc, filename)

        # Select worksheet by index. Worksheet indexes start from zero
        #worksheet = sheet.get_worksheet(0)
        worksheet = self.trygetworksheet(sheet, 0)

        #if self.testInputFile(worksheet) == False:
        #    self.validTest = False
        #    return False
        
        # trycount = 0
        # while True:
            # print ( " Trying " , trycount )
            # trycount = trycount + 1

        self.testIdx = -1
        idx = 2
        val = -1
        
        # This row contains the iterations left to complete
        while True:
            try:
                row_values_list = [0] + worksheet.row_values(2)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...18")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...19" , str(e) )
                    
        while True:
            if idx >= len(row_values_list):
                self.testIdx == -99
                break
            # Get all value with coords
            # Use try catch here in case we hit the end of the sheet!
            try:
                val = int(row_values_list[idx])
            except:
                break

            #val = int(worksheet.cell(2, idx).value)
            if val > 0:
                # save this index
                self.testIdx = idx
                break
            elif val <= 0:
                idx = idx + 1
            else:
                break

        if self.testIdx == -1:
            self.validTest = False
            self.workingOn = -1
            return False
            
        # Remove our old working flag if there is one
        if self.workingOn != -1:
            self.proccessed = self.proccessed + 1
            # Here we are removing our working on flag from the list
            self.tryupdate(worksheet, self.working_on_id, self.workingOn, int(self.tryread(worksheet, self.working_on_id, self.workingOn)) - 1)
            #worksheet.update_cell(20, self.workingOn, int(worksheet.cell(20, self.workingOn).value) - 1)
        
        # Test succeess
        if self.testIdx == -99:
            self.validTest = False
            #self.workingOn = -1
            return False

        # Remove the iteration from the counter
        self.tryupdate(worksheet, 2, self.testIdx, val - 1)
        #worksheet.update_cell(2, self.testIdx, val - 1)
        
        # Get the test values
        while True:
            try:
                col_values_list = worksheet.col_values(self.testIdx)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...1")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...2" , str(e) )

        # Add our instance to the working flags
        flag = int(self.tryread(worksheet, self.working_on_id, self.testIdx)) + 1
        self.tryupdate(worksheet, self.working_on_id, self.testIdx, flag)
        #worksheet.update_cell(20, self.testIdx, int(worksheet.cell(20, self.testIdx).value) + 1)

        # Names
        print(col_values_list)
        self.mapname = col_values_list[3 - 1]
        self.simmapname = self.mapname + "/osm.sumocfg"
        self.avProbability = float(col_values_list[4 - 1])
        self.cavProbability = float(col_values_list[5 - 1])
        self.scale = float(col_values_list[6 - 1])
        self.timestep = float(col_values_list[7 - 1])
        self.trafficSet = int(col_values_list[8 - 1])
        self.logEmisisonsData = int(col_values_list[9 - 1])

        self.validTest = True
        self.workingOn = self.testIdx

        return True

    def printHeaders(self):   
        headerArray = []
        headerArray.append("mapname")
        headerArray.append("avProbability")
        headerArray.append("cavProbability")
        headerArray.append("scale")
        headerArray.append("trafficSet")

        return headerArray
        
    def returnXMLDataHeader(self):
        headerArray = []
        headerArray.append("totalVehicles")
        headerArray.append("totalTimeLoss")
        headerArray.append("averageTimeLoss")
        headerArray.append("averagewaitingTime")
        headerArray.append("waitingTimeSTDDev")
        headerArray.append("totalWaitingTime")
        headerArray.append("averageSpeed")
        headerArray.append("noramlizedDurationSTDDev")
        headerArray.append("noramlizedDurationMean")
        headerArray.append("minTimeLoss")
        headerArray.append("maxTimeLoss")
        headerArray.append("averageco2")
        headerArray.append("averageco")
        headerArray.append("averagehc")
        headerArray.append("averagenox")
        headerArray.append("averagepmx")
        headerArray.append("averagefuel")
        headerArray.append("averageelectricity")

        return headerArray
        
    def returnStatsDataHeader(self):
        headerArray = []
        headerArray.append("step")
        headerArray.append("totalVehicles")
        headerArray.append("totalAVs")
        headerArray.append("totalCAVs")
        return headerArray
        
    def writeOutputFile(self, traciStats, xmlStats, overallFileName):
        lock_path = overallFileName + ".lock"
        lock = FileLock(lock_path)
        with lock:
            file = open(overallFileName,"a")
            
            file.write(self.mapname + ",")
            file.write(str(self.avProbability) + ",")
            file.write(str(self.cavProbability) + ",")
            file.write(str(self.scale) + ",")
            file.write(str(self.trafficSet) + ",")
            
            file.write(xmlStats + ",")
            file.write(traciStats + '\n')

            file.close()
            
    def writeOutputFileGoogleSheets(self, traciStats, overallFileName, SUMOStats = None, collisionStats = None):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('../credentials/sheets_credentials.json', scope)

        gc = self.trygetauthorization(gspread, credentials)

        # If you want to be specific, use a key (which can be extracted from
        # the spreadsheet's url)
        #sheet = gc.open_by_key(overallFileName)
        sheet = self.trygetfile(gc, overallFileName)

        # Select worksheet by index. Worksheet indexes start from zero
        #worksheet = sheet.get_worksheet(0)
        worksheet = self.trygetworksheet(sheet, 0)

        output = []
        output.append(self.mapname)
        output.append(str(self.avProbability))
        output.append(str(self.cavProbability))
        output.append(str(self.scale))
        output.append(str(self.timestep))
        output.append(str(self.trafficSet))
        output.append(str(self.logEmisisonsData))

        print ( output )

        output.append(str(traciStats["totalVehicles"]))
        output.append(str(traciStats["totalAVs"]))
        output.append(str(traciStats["totalCAVs"]))
        output.append(str(traciStats["step"]))
        
        print ( output )

        if SUMOStats != None:
            output.append(SUMOStats.totalVehicles)
            output.append(SUMOStats.totalTimeLoss)
            output.append(SUMOStats.averageTimeLoss)
            output.append(SUMOStats.averageWaitingTime)
            output.append(SUMOStats.waitingTimeSTDDev)
            output.append(SUMOStats.totalWaitingTime)
            output.append(SUMOStats.averageSpeed)
            output.append(SUMOStats.noramlizedDurationSTDDev)
            output.append(SUMOStats.noramlizedDurationMean)
            output.append(SUMOStats.minTimeLoss)
            output.append(SUMOStats.maxTimeLoss)
            output.append(SUMOStats.averageco2)
            output.append(SUMOStats.averageco)
            output.append(SUMOStats.averagehc)
            output.append(SUMOStats.averagenox)
            output.append(SUMOStats.averagepmx)
            output.append(SUMOStats.averagefuel)
            output.append(SUMOStats.averageelectricity)

        if collisionStats != None:
            output.append(collisionStats)

        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                worksheet.append_row(output)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...3")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...4" , str(e)  )
                    time.sleep(10)
        
    def writeThreadStartSheets(self, fileName, timestamp):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('../credentials/sheets_credentials.json', scope)

        gc = self.trygetauthorization(gspread, credentials)

        # If you want to be specific, use a key (which can be extracted from
        # the spreadsheet's url)
        #sheet = gc.open_by_key(fileName)
        sheet = self.trygetfile(gc, fileName)

        # Select worksheet by index. Worksheet indexes start from zero
        #worksheet = sheet.get_worksheet(0)
        worksheet = self.trygetworksheet(sheet, 0)

        output = []
        output.append(self.processID)
        output.append(self.testIdx)
        output.append(self.proccessed)
        output.append(timestamp)
        output.append(-1)

        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                worksheet.append_row(output)
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...5")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error...6" , str(e)  )
        
        tempThreadInfoRow = worksheet.row_count + 1
        #if worksheet.cell(tempThreadInfoRow, 1).value == self.processID:
        self.threadInfoRow = tempThreadInfoRow
        
        print ( self.threadInfoRow )
        #else:
        #    self.threadInfoRow = -1

    def trygetrange(self, worksheet, threadInfoRow):
        # We need to make sure that this is added even if we exceed the requests per minute quota of google API
        while True:
            try:
                return worksheet.range('A' + str(threadInfoRow) + ':E' + str(threadInfoRow))
                break
            except Exception as e:
                if str(e).find("RESOURCE_EXHAUSTED")>-1:
                    print ("resource exhausted...")
                    time.sleep(10)
                else:
                    print ( "unknown GSUITE error..." , str(e)  )
            
    def writeThreadUpdateSheets(self, fileName, timestamp, step):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name('../credentials/sheets_credentials.json', scope)

        gc = self.trygetauthorization(gspread, credentials)

        # If you want to be specific, use a key (which can be extracted from
        # the spreadsheet's url)
        #sheet = gc.open_by_key(fileName)
        sheet = self.trygetfile(gc, fileName)

        # Select worksheet by index. Worksheet indexes start from zero
        #worksheet = sheet.get_worksheet(0)
        worksheet = self.trygetworksheet(sheet, 0)
        
        if self.threadInfoRow != -1:
            # Select a range
            #cell_list = worksheet.range('A' + str(self.threadInfoRow) + ':E' + str(self.threadInfoRow))
            cell_list = self.trygetrange(worksheet, self.threadInfoRow)

            cell_list[0].value = self.processID
            cell_list[1].value = self.testIdx
            cell_list[2].value = self.proccessed
            cell_list[3].value = timestamp
            cell_list[4].value = step

            # Update in batch
            # We need to make sure that this is added even if we exceed the requests per minute quota of google API
            while True:
                try:
                    worksheet.update_cells(cell_list)
                    break
                except Exception as e:
                    if str(e).find("RESOURCE_EXHAUSTED")>-1:
                        print ("resource exhausted...")
                        time.sleep(10)
                    else:
                        print ( "unknown GSUITE error..." , str(e)  )
                        time.sleep(10)
        
        # Old way
        # if self.threadInfoRow != -1:
            # worksheet.update_cell(self.threadInfoRow, 1, self.processID)
            # worksheet.update_cell(self.threadInfoRow, 2, self.testIdx)
            # worksheet.update_cell(self.threadInfoRow, 3, self.proccessed)
            # worksheet.update_cell(self.threadInfoRow, 4, time)
            # worksheet.update_cell(self.threadInfoRow, 5, step)
            
    def parseOutputFile(self, outputFileName):
        parsedOutputFileName = outputFileName.replace(".csv", "_parsed.csv")
        
        parsedResults = []
        parsedSubsetResults = []
        
        # Read the values within the outputFileName
        lock_path = outputFileName + ".lock"
        lock = FileLock(lock_path)
        with lock:
            # work with the file as it is now locked
            print("Lock acquired.")
            # Read the csv file containing all of our test data
            with open(outputFileName, 'r') as file:
                reader = csv.reader(file)
                inputList = list(reader)
            
            # Pop the first element because it is just labels
            inputList.pop(0)
            
            # We should sort the output first so this looks orderly
            s = sorted(inputList, key = operator.itemgetter(0, 1, 2, 3, 4, 5, 6))

            for idx, row in enumerate(s):
                print ( len(row), row )
                found = False
                for parsedIdx, dataset in enumerate(parsedResults):
                    if row[0:6] == dataset:
                        found = True
                        parsedSubsetResults[parsedIdx].append(row[7:])
                        break
                if found == False:
                    parsedResults.append(row[0:6])
                    parsedSubsetResults.append([row[7:]])
        
            #print ( parsedResults )
            
            averagedResults = []
            stdDevResults = []
            for entry in parsedSubsetResults:
                tempAverages = []
                tempStdDeviations = []
                if len(entry) > 0:
                    for columnIdx in range(len(entry[0])):
                        column = [float(row[columnIdx]) for row in entry]
                        tempStdDeviations.append(len(column))
                        if len(column) > 1:
                            tempAverages.append(statistics.mean(column))
                            tempStdDeviations.append(statistics.stdev(column))
                        else:
                            tempAverages.append(column[0])
                            tempStdDeviations.append(column[0])
                averagedResults.append(tempAverages)
                stdDevResults.append(tempStdDeviations)

            with open(parsedOutputFileName, 'w', newline='') as file:
                # Write back the csv lines with the modified durations remaining
                writer = csv.writer(file)
                
                writer.writerow(self.printHeaders() + self.returnStatsDataHeader() + self.returnXMLDataHeader() + ["numberOfRuns"] + self.returnStatsDataHeader() + self.returnXMLDataHeader())
                
                for idx, row in enumerate(parsedResults):
                     writer.writerow(row[0:6] + averagedResults[idx] + stdDevResults[idx])
