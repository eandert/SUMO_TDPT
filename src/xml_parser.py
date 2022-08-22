import xml.etree.ElementTree as ET
import numpy


class SUMOXMLDataParser:
    def __init__(self):
        self.totalVehicles = 0
        self.totalTimeLoss = 0.0
        self.averageTimeLoss = 0.0
        self.averageWaitingTime = 0.0
        self.waitingTimeSTDDev = 0.0
        self.totalWaitingTime = 0.0
        self.averageSpeed = 0.0
        self.noramlizedDurationSTDDev = 0.0
        self.noramlizedDurationMean = 0.0
        self.minTimeLoss = 0.0
        self.maxTimeLoss = 0.0
        self.averageco2 = 0.0
        self.averageco = 0.0
        self.averagehc = 0.0
        self.averagenox = 0.0
        self.averagepmx = 0.0
        self.averagefuel = 0.0
        self.averageelectricity = 0.0


class SUMOOutputParser:
    def __init__(self, filenameTripInfo):
        self.rootTripInfo = ET.parse(filenameTripInfo).getroot()
        self.totalTimeLoss = 0
        self.averageTimeLoss = 0
        self.totalVehicles = 0
        self.totalWaitingTime = 0
        self.averageWaitingTime = 0
        self.routeLengthTotal = 0
        self.routeDurationTotal = 0
        self.totalAverageSpeed = 0
        self.averageSpeed = 0
        
        self.totalco2 = 0
        self.totalco = 0
        self.totalhc = 0
        self.totalnox = 0
        self.totalpmx = 0
        self.totalfuel = 0
        self.totalelectricity = 0
        
        self.maxTimeLoss = 0
        self.minTimeLoss = 9999999

        self.header_array = ["totalVehicles", "totalTimeLoss", "averageTimeLoss", "averageWaitingTime", "waitingTimeSTDDev",
                             "totalWaitingTime", "averageSpeed", "noramlizedDurationSTDDev", "noramlizedDurationMean",
                             "minTimeLoss", "maxTimeLoss", "averageco", "averagehc", "averagenox", "averagepmx",
                             "averagefuel", "averageelectricity"]

    def returnParsedData(self):
        waitingTimeList = []
        noramlizedDurationList = []
        for type_tag in self.rootTripInfo.findall('tripinfo'):
            timeLoss = float(type_tag.get('timeLoss'))
            waitingTime = float(type_tag.get('waitingTime'))
            routeLength = float(type_tag.get('routeLength'))
            duration = float(type_tag.get('duration'))
            
            # Now we parse emissions
            #CO2="9941.81" CO="146.64" HC="0.91" NOx="4.27" PMx="0.21"
            co2 = float(type_tag[0].get('CO2_abs'))
            hc = float(type_tag[0].get('HC_abs'))
            co = float(type_tag[0].get('CO_abs'))
            nox = float(type_tag[0].get('NOx_abs'))
            pmx = float(type_tag[0].get('PMx_abs'))
            fuel = float(type_tag[0].get('fuel_abs'))
            electricity = float(type_tag[0].get('electricity_abs'))

            self.totalco2 = self.totalco2 + co2
            self.totalco = self.totalco + hc
            self.totalhc = self.totalhc + co
            self.totalnox = self.totalnox + nox
            self.totalpmx = self.totalpmx + pmx
            self.totalfuel = self.totalfuel + fuel
            self.totalelectricity = self.totalelectricity + electricity
            
            noramlizedDuration = duration/(duration-timeLoss)
            if noramlizedDuration > self.maxTimeLoss:
                self.maxTimeLoss = noramlizedDuration
            if noramlizedDuration < self.minTimeLoss and noramlizedDuration >= 0:
                self.minTimeLoss = noramlizedDuration
            
            self.totalVehicles = self.totalVehicles + 1
            self.totalTimeLoss = self.totalTimeLoss + timeLoss
            self.totalWaitingTime = self.totalWaitingTime + waitingTime
            self.routeLengthTotal = self.routeLengthTotal + routeLength
            self.routeDurationTotal = self.routeDurationTotal + duration
            self.totalAverageSpeed = self.totalAverageSpeed + (routeLength/duration)
            
            waitingTimeList.append(timeLoss)
            noramlizedDurationList.append(noramlizedDuration)
            
        self.averageTimeLoss = self.totalTimeLoss / self.totalVehicles
        self.averageWaitingTime = self.totalWaitingTime / self.totalVehicles
        self.averageSpeed = self.totalAverageSpeed / self.totalVehicles
        
        waitingTimeListNumpy = numpy.array(waitingTimeList)
        waitingTimeSTDDev = numpy.std(waitingTimeListNumpy, ddof=0, dtype=numpy.float64)
        
        noramlizedDurationListNumpy = numpy.array(noramlizedDurationList)
        noramlizedDurationSTDDev = numpy.std(noramlizedDurationListNumpy, ddof=0, dtype=numpy.float64)
        noramlizedDurationMean = numpy.mean(noramlizedDurationListNumpy, dtype=numpy.float64)

        averageco2 = self.totalco2/self.totalVehicles
        averageco = self.totalco/self.totalVehicles
        averagehc = self.totalhc/self.totalVehicles
        averagenox = self.totalnox/self.totalVehicles
        averagepmx = self.totalpmx/self.totalVehicles
        averagefuel = self.totalfuel/self.totalVehicles
        averageelectricity = self.totalelectricity/self.totalVehicles
        
        return str(self.totalVehicles) + "," + str(self.totalTimeLoss) + "," + str(self.averageTimeLoss) + "," + str(self.averageWaitingTime) + "," + str(waitingTimeSTDDev) + "," + str(self.totalWaitingTime) + "," + str(self.averageSpeed) + "," + str(noramlizedDurationSTDDev) + "," + str(noramlizedDurationMean) + "," + str(self.minTimeLoss) + "," + str(self.maxTimeLoss) + "," + str(averageco2) + "," + str(averageco) + "," + str(averagehc) + "," + str(averagenox) + "," + str(averagepmx) + "," + str(averagefuel) + "," + str(averageelectricity)

    def returnParsedDataGoogleSheets(self):
        waitingTimeList = []
        noramlizedDurationList = []
        for type_tag in self.rootTripInfo.findall('tripinfo'):
            timeLoss = float(type_tag.get('timeLoss'))
            waitingTime = float(type_tag.get('waitingTime'))
            routeLength = float(type_tag.get('routeLength'))
            duration = float(type_tag.get('duration'))
            
            # Now we parse emissions
            #CO2="9941.81" CO="146.64" HC="0.91" NOx="4.27" PMx="0.21"
            co2 = float(type_tag[0].get('CO2_abs'))
            hc = float(type_tag[0].get('HC_abs'))
            co = float(type_tag[0].get('CO_abs'))
            nox = float(type_tag[0].get('NOx_abs'))
            pmx = float(type_tag[0].get('PMx_abs'))
            fuel = float(type_tag[0].get('fuel_abs'))
            electricity = float(type_tag[0].get('electricity_abs'))

            self.totalco2 = self.totalco2 + co2
            self.totalco = self.totalco + hc
            self.totalhc = self.totalhc + co
            self.totalnox = self.totalnox + nox
            self.totalpmx = self.totalpmx + pmx
            self.totalfuel = self.totalfuel + fuel
            self.totalelectricity = self.totalelectricity + electricity
            
            noramlizedDuration = duration/(duration-timeLoss)
            if noramlizedDuration > self.maxTimeLoss:
                self.maxTimeLoss = noramlizedDuration
            if noramlizedDuration < self.minTimeLoss and noramlizedDuration >= 0:
                self.minTimeLoss = noramlizedDuration
            
            self.totalVehicles = self.totalVehicles + 1
            self.totalTimeLoss = self.totalTimeLoss + timeLoss
            self.totalWaitingTime = self.totalWaitingTime + waitingTime
            self.routeLengthTotal = self.routeLengthTotal + routeLength
            self.routeDurationTotal = self.routeDurationTotal + duration
            self.totalAverageSpeed = self.totalAverageSpeed + (routeLength/duration)
            
            waitingTimeList.append(timeLoss)
            noramlizedDurationList.append(noramlizedDuration)
            
        self.averageTimeLoss = self.totalTimeLoss / self.totalVehicles
        self.averageWaitingTime = self.totalWaitingTime / self.totalVehicles
        self.averageSpeed = self.totalAverageSpeed / self.totalVehicles
        
        waitingTimeListNumpy = numpy.array(waitingTimeList)
        waitingTimeSTDDev = numpy.std(waitingTimeListNumpy, ddof=0, dtype=numpy.float64)
        
        noramlizedDurationListNumpy = numpy.array(noramlizedDurationList)
        noramlizedDurationSTDDev = numpy.std(noramlizedDurationListNumpy, ddof=0, dtype=numpy.float64)
        noramlizedDurationMean = numpy.mean(noramlizedDurationListNumpy, dtype=numpy.float64)

        averageco2 = self.totalco2/self.totalVehicles
        averageco = self.totalco/self.totalVehicles
        averagehc = self.totalhc/self.totalVehicles
        averagenox = self.totalnox/self.totalVehicles
        averagepmx = self.totalpmx/self.totalVehicles
        averagefuel = self.totalfuel/self.totalVehicles
        averageelectricity = self.totalelectricity/self.totalVehicles
        
        returnPacket = SUMOXMLDataParser()
        returnPacket.totalVehicles = self.totalVehicles
        returnPacket.totalTimeLoss = self.totalTimeLoss
        returnPacket.averageTimeLoss = self.averageTimeLoss
        returnPacket.averageWaitingTime = self.averageWaitingTime
        returnPacket.waitingTimeSTDDev = waitingTimeSTDDev
        returnPacket.totalWaitingTime = self.totalWaitingTime
        returnPacket.averageSpeed = self.averageSpeed
        returnPacket.noramlizedDurationSTDDev = noramlizedDurationSTDDev
        returnPacket.noramlizedDurationMean = noramlizedDurationMean
        returnPacket.minTimeLoss = self.minTimeLoss
        returnPacket.maxTimeLoss = self.maxTimeLoss
        returnPacket.averageco2 = averageco2
        returnPacket.averageco = averageco
        returnPacket.averagehc = averagehc
        returnPacket.averagenox = averagenox
        returnPacket.averagepmx = averagepmx
        returnPacket.averagefuel = averagefuel
        returnPacket.averageelectricity = averageelectricity

        return returnPacket

    def return_parsed_data_header(self):
        return self.header_array


class CollisionOutputParser:
    def __init__(self, filenameCollisions):
        self.rootTripInfo = ET.parse(filenameCollisions).getroot()
        self.totalCollisions = 0

    def returnParsedData(self):
        for type_tag in self.rootTripInfo.findall('collision'):
            self.totalCollisions += 1

        return self.totalCollisions

# Usage example for calling from another file
#sumoparser = SUMOOutputParser("../output/deleteme0simulation_tripinfo.xml")
#print ( sumoparser.returnParsedData() )