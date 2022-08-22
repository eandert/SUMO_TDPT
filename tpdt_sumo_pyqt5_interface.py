from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor
import subprocess
import sys
from sys import executable
from subprocess import *
import time
import os
from timeloop import Timeloop
from datetime import timedelta
import random
import math
import json

tl = Timeloop()

global mainWin

@tl.job(interval=timedelta(seconds=1))
def read_simulation_every_1s():
    global mainWin
    mainWin.checkStatus()

class MainWindow(QMainWindow):
    def __init__(self):
        self.simulation = []
        self.simulationP = []
        
        # Store the launch information so that if we crash we can restart
        self.simulatorLaunchCode = []
        
        # Store the long term status of a thread
        self.threadStatus = []
        self.checkingblocked = True

        self.mapNameText = 'default/'
        
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(320, 800))    
        self.setWindowTitle("SUMO TPDT GUI") 
        
        self.tableWidget = QTableWidget(self)

        self.labelTestName = QLabel(self)
        self.labelTestName.setText('Test name:')
        self.labelTestName.move(20, 20)
        
        self.lineTestName = QLineEdit(self)
        self.lineTestName.move(80, 20)
        self.lineTestName.resize(200, 32)
        
        self.butonSimulationGui = QPushButton("Simulation GUI", self)
        self.butonSimulationGui.setCheckable(True)
        #self.butonSimulationGui.toggle() start in off position
        self.butonSimulationGui.resize(100, 32)
        self.butonSimulationGui.move(5, 60)
        
        self.labelAutomatedTests = QLabel(self)
        self.labelAutomatedTests.setText('Automated Test Suites:')
        self.labelAutomatedTests.resize(150, 32)
        self.labelAutomatedTests.move(20, 100)
        
        self.testGroup = QButtonGroup(self) # Radio button group

        self.radioSpreadTest = QRadioButton("Spread Test", self)
        self.radioSpreadTest.resize(100, 32)
        self.radioSpreadTest.move(40, 140)
        self.radioSpreadTest.clicked.connect(self.showCustomOptions)
        self.testGroup.addButton(self.radioSpreadTest)

        self.labelSpreadOptions = QLabel(self)
        self.labelSpreadOptions.setText('Spread Test Options:')
        self.labelSpreadOptions.move(20, 180)
        self.labelSpreadOptions.hide()

        self.labelNumSpreadTests = QLabel(self)
        self.labelNumSpreadTests.setText('Test File Name')
        self.labelNumSpreadTests.move(20, 220)
        self.labelNumSpreadTests.hide()

        self.lineSpreadTestName = QLineEdit(self)
        self.lineSpreadTestName.resize(200, 32)
        self.lineSpreadTestName.move(100, 220)
        self.lineSpreadTestName.setText("test.csv")
        self.lineSpreadTestName.hide()
        
        self.labelCustomOptions = QLabel(self)
        self.labelCustomOptions.setText('Custom Test Options:')
        self.labelCustomOptions.move(20, 260)
        self.labelCustomOptions.show()
        
        self.labelAvPercentage = QLabel(self)
        self.labelAvPercentage.setText('AV %(0->1)')
        self.labelAvPercentage.move(20, 300)
        self.labelAvPercentage.show()
        
        self.lineAvPercentage = QLineEdit(self)
        self.lineAvPercentage.resize(40, 32)
        self.lineAvPercentage.move(100, 300)
        self.lineAvPercentage.setText("0.0")
        self.lineAvPercentage.show()
        
        self.labelCameraPercentage = QLabel(self)
        self.labelCameraPercentage.setText('Camera %(0->1)')
        self.labelCameraPercentage.move(160, 300)
        self.labelCameraPercentage.show()

        self.lineCameraPercentage = QLineEdit(self)
        self.lineCameraPercentage.resize(40, 32)
        self.lineCameraPercentage.move(260, 300)
        self.lineCameraPercentage.setText("0.0")
        self.lineCameraPercentage.show()
        
        self.labelOBDPercentage = QLabel(self)
        self.labelOBDPercentage.setText('OBD %(0->1)')
        self.labelOBDPercentage.move(20, 340)
        self.labelOBDPercentage.show()

        self.lineOBDPercentage = QLineEdit(self)
        self.lineOBDPercentage.resize(40, 32)
        self.lineOBDPercentage.move(100, 340)
        self.lineOBDPercentage.setText("0.0")
        self.lineOBDPercentage.show()
        
        self.labelScale = QLabel(self)
        self.labelScale.setText('Scale (0-10')
        self.labelScale.move(160, 340)
        self.labelScale.show()

        self.lineScale = QLineEdit(self)
        self.lineScale.resize(40, 32)
        self.lineScale.move(260, 340)
        self.lineScale.setText("1")
        self.lineScale.show()
        
        self.labelTFLDistance = QLabel(self)
        self.labelTFLDistance.setText('TFL Distance')
        self.labelTFLDistance.move(20, 380)
        self.labelTFLDistance.show()

        self.lineTFLDistance = QLineEdit(self)
        self.lineTFLDistance.resize(40, 32)
        self.lineTFLDistance.move(100, 380)
        self.lineTFLDistance.setText("200.0")
        self.lineTFLDistance.show()

        self.labelControlMethod = QLabel(self)
        self.labelControlMethod.setText('Control Method 0-E,1-L')
        self.labelControlMethod.move(160, 380)
        self.labelControlMethod.show()

        self.lineControlMethod = QLineEdit(self)
        self.lineControlMethod.resize(40, 32)
        self.lineControlMethod.move(260, 380)
        self.lineControlMethod.setText("0")
        self.lineControlMethod.show()
        
        self.buttonNoMaxTimeConstraints = QPushButton("No Max Timout", self)
        self.buttonNoMaxTimeConstraints.setCheckable(True)
        #self.buttonNoMaxTimeConstraints.toggle()
        self.buttonNoMaxTimeConstraints.resize(100, 32)
        self.buttonNoMaxTimeConstraints.move(5, 420)
        
        self.buttonCreateSave = QPushButton("Save Probability", self)
        self.buttonCreateSave.setCheckable(True)
        #self.buttonCreateSave.toggle() start in the off position
        self.buttonCreateSave.resize(100, 32)
        self.buttonCreateSave.move(110, 420)
        
        self.buttonTrafficControlEnabled = QPushButton("TFL Control EN", self)
        self.buttonTrafficControlEnabled.setCheckable(True)
        self.buttonTrafficControlEnabled.toggle()
        self.buttonTrafficControlEnabled.resize(100, 32)
        self.buttonTrafficControlEnabled.move(215, 420)
        
        self.buttonRoutePrediction = QPushButton("Route Prediction", self)
        self.buttonRoutePrediction.setCheckable(True)
        #self.buttonRoutePrediction.toggle() start in the off position
        self.buttonRoutePrediction.resize(120, 32)
        self.buttonRoutePrediction.move(40, 460)
        
        self.buttonRouteTrackingPerfect = QPushButton("Perfect Prediction", self)
        self.buttonRouteTrackingPerfect.setCheckable(True)
        #self.buttonRouteTrackingPerfect.toggle() start in the off position
        self.buttonRouteTrackingPerfect.resize(120, 32)
        self.buttonRouteTrackingPerfect.move(180, 460)
        
        self.labelThreads = QLabel(self)
        self.labelThreads.setText('Number of threads:')
        self.labelThreads.move(160, 500)

        self.lineThreads = QLineEdit(self)
        self.lineThreads.resize(40, 32)
        self.lineThreads.move(260, 500)
        self.lineThreads.textChanged.connect(self.createTable)
        self.lineThreads.setText("1")
        
        self.buttonSelectMap = QPushButton("Select Map", self)
        self.buttonSelectMap.clicked.connect(self.selectMapName)
        #self.buttonRouteTrackingPerfect.toggle() start in the off position
        self.buttonSelectMap.resize(100, 32)
        self.buttonSelectMap.move(20, 540)
        
        self.mapName = QLabel(self)
        self.mapName.setText(self.mapNameText)
        self.mapName.move(130, 540)

        self.startButton = QPushButton('Start Test', self)
        self.startButton.clicked.connect(self.on_start_clicked)
        self.startButton.resize(140,32)
        self.startButton.move(10, 600)     

        self.endButton = QPushButton('End Test', self)
        self.endButton.clicked.connect(self.on_end_clicked)
        self.endButton.resize(140,32)
        self.endButton.move(160, 600)

        # Set default view
        self.radioSpreadTest.click()

        # Parse settings
        file = open('settings.json')
        settings = json.load(file)

        # Default test values from settings
        self.lineTestName.setText(settings['output_file'])
        self.lineSpreadTestName.setText(settings['input_file'])
        self.threadMonitor = settings['thread_monitor']

    def createTable(self):
        # Create table
        threads = int(self.lineThreads.text())
        self.tableWidget.setRowCount(math.ceil(threads/3))
        self.tableWidget.setColumnCount(3)
        counter = 0
        for column in range(math.ceil(threads/3)):
            for row in range(3):
                if counter < threads:
                    self.tableWidget.setItem(column, row, QTableWidgetItem())
                    self.tableWidget.item(column, row).setBackground(QColor(10,10,10))
                    self.tableWidget.item(column, row).setText(str(counter))
                    counter += 1
        self.tableWidget.move(0,650)
        self.tableWidget.resize(320,150)
        
    def colorAccordingToResult(self, thread, result):
        row = thread%3
        column = math.floor(thread/3)
        #print ( row , column )
        if result == 1:
            # Alive, color accordingly
            self.tableWidget.setItem(column, row, QTableWidgetItem())
            self.tableWidget.item(column, row).setBackground(QColor(0,255,0))
            self.tableWidget.item(column, row).setText(str(thread))
        elif result == 2:
            # Successful finish, color accordingly
            self.tableWidget.setItem(column, row, QTableWidgetItem())
            self.tableWidget.item(column, row).setBackground(QColor(0,0,255))
            self.tableWidget.item(column, row).setText(str(thread))
        elif result == 3:
            # Died with a known error, color accordingly
            self.tableWidget.setItem(column, row, QTableWidgetItem())
            self.tableWidget.item(column, row).setBackground(QColor(255,255,0))
            self.tableWidget.item(column, row).setText(str(thread))
        else:
            # Died color accordingly
            self.tableWidget.setItem(column, row, QTableWidgetItem())
            self.tableWidget.item(column, row).setBackground(QColor(255,0,0))
            self.tableWidget.item(column, row).setText(str(thread))

    def selectMapName(self):
        directory = QFileDialog.getExistingDirectory(None, 'Select map folder:', str(os.getcwd()) + "maps/" , QFileDialog.ShowDirsOnly)
        if directory != None:
            self.mapNameText = directory
            self.mapName.setText(self.mapNameText)
        else:
            alert = QMessageBox()
            alert.setText('Please select a valid map folder')
            alert.exec_()

    def showCustomOptions(self):
        self.labelCustomOptions.hide()
        self.labelAvPercentage.hide()
        self.lineAvPercentage.hide()
        self.labelCameraPercentage.hide()
        self.lineCameraPercentage.hide()
        self.labelOBDPercentage.hide()
        self.lineOBDPercentage.hide()
        self.labelScale.hide()
        self.lineScale.hide()
        self.labelTFLDistance.hide()
        self.lineTFLDistance.hide()
        self.labelControlMethod.hide()
        self.lineControlMethod.hide()
        self.buttonNoMaxTimeConstraints.hide()
        self.buttonTrafficControlEnabled.hide()
        self.buttonCreateSave.hide()
        self.buttonRoutePrediction.hide()
        self.buttonRouteTrackingPerfect.hide()
        self.mapName.hide()
        self.buttonSelectMap.hide()

        self.labelSpreadOptions.show()
        self.labelNumSpreadTests.show()
        self.lineSpreadTestName.show()

    def on_start_clicked(self):
        # Declare the button pushed
        self.startButton.setEnabled(False)
        
        # Create the output file name that we will reuse for all the results
        outputFiletime = time.strftime("%Y%m%d-%H%M%S")
        startPort = random.randint(12345,65535)
    
        os.chdir('src')
        
        popenArraySimulation = ['python', 'runner_atlas_simulation.py']
        popenArraySimulation.append('--mapname')
        popenArraySimulation.append(self.mapNameText)
        if self.butonSimulationGui.isChecked():
            popenArraySimulation.append('--gui')
        if len(self.lineTestName.text()) > 0:
            popenArraySimulation.append('--filename')
            # TODO: make this a setting
            #popenArraySimulation.append(self.lineTestName.text()+outputFiletime)
            popenArraySimulation.append(self.lineTestName.text())
        if len(self.lineSpreadTestName.text()) > 0:
            popenArraySimulation.append('--testname')
            popenArraySimulation.append(self.lineSpreadTestName.text())
        # For now we are just going to automatically set the port
        if int(self.lineThreads.text()) == 1:
            self.colorAccordingToResult(0, 1)
            self.threadStatus = [0]
            popenArraySimulation.append('--portid')
            popenArraySimulation.append(str(startPort))
            popenArraySimulation.append('--thread_management_sheet')
            popenArraySimulation.append(str(self.threadMonitor))
            self.simulationP.append(Popen(popenArraySimulation, creationflags=CREATE_NEW_CONSOLE))
            self.simulatorLaunchCode.append(popenArraySimulation)
            self.simulation.append(True)
            print ( "spawning sim with opts: " )
            print ( popenArraySimulation )
        elif int(self.lineThreads.text()) > 1 and int(self.lineThreads.text()) < 257:
            self.threadStatus = [0] * int(self.lineThreads.text())
            portcountertemp = startPort
            for idx in range(int(self.lineThreads.text())):
                self.colorAccordingToResult(idx, 1)
                popenArraySimulationTemp = []
                popenArraySimulationTemp.append('--thread_management_sheet')
                popenArraySimulationTemp.append(str(self.threadMonitor))
                popenArraySimulationTemp.append('--portid')
                portcountertemp = portcountertemp + 1
                popenArraySimulationTemp.append(str(portcountertemp))
                self.simulationP.append(Popen(popenArraySimulation + popenArraySimulationTemp, creationflags=CREATE_NEW_CONSOLE))
                self.simulatorLaunchCode.append(popenArraySimulation + popenArraySimulationTemp)
                self.simulation.append(True)
                print ( "spawning sim with opts: " )
                print ( popenArraySimulation + popenArraySimulationTemp )
                time.sleep(30) # give it some arbitrary time to sleep and finish
        else:
            alert = QMessageBox()
            alert.setText('1 - 256 threads must be set!')
            alert.exec_()
            return
        
        self.checkingblocked = False
        
        os.chdir('..')
        
        # alert = QMessageBox()
        # alert.setText('Controller has been started!')
        # alert.exec_()
        
    def on_end_clicked(self):
        self.kill_simulation()

        alert = QMessageBox()
        alert.setText('Test is over!')
        alert.exec_()
        
        # Clear the watch queues
        self.simulation = []
        self.simulationP = []
        
        # Declare the button pushable
        self.startButton.setEnabled(True)
        
    def markAsAlive(self, thread):
        self.threadStatus[thread] = 0
        
    def addAndcheckMissCount(self, thread):
        # Check the current time and add it as our time if there is none
        checkTime = time.time()
        if self.threadStatus[thread] == 0:
            self.threadStatus[thread] = checkTime
        
        # Check if more than 15 minutes has past since we saw tht thread alive
        if (checkTime - self.threadStatus[thread]) > 900:
            self.checkingblocked = True
            self.endAndRestart(thread)
            self.markAsAlive(thread)
            self.checkingblocked = False
        
    def checkStatus(self):
        if self.checkingblocked == False:
            #print ( "st1s job current time : {}".format(time.ctime()) )
            for thread, (sim, simp) in enumerate(zip(self.simulation, self.simulationP)):
                if sim == True:
                    if simp.poll() is None:
                        #simulation = False
                        #alert = QMessageBox()
                        #alert.setText('Simulation has exited!')
                        #alert.exec_()
                        self.markAsAlive(thread)
                        pass
                    else:
                        rc = simp.returncode
                        #print (rc)
                        if rc == 4294967197:
                            self.colorAccordingToResult(int(thread), 3)
                            self.addAndcheckMissCount(thread)
                            #print ( " here 3 1 " )
                        elif rc == 99:
                            self.colorAccordingToResult(int(thread), 2)
                            # Time to end this thread we are done!
                            sim = False
                        else:
                            self.colorAccordingToResult(int(thread), 0)
                            self.addAndcheckMissCount(thread)
                            #print ( " here 0 1 " )
        
    def kill_simulation(self):
        for sim, simp in zip(self.simulation, self.simulationP):
            if sim == True:
                subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=simp.pid))
                sim = False
                
    def endAndRestart(self, thread):
        print ( " Restarting thread " , thread )
        
        os.chdir('src')
    
        # Check and end both simulator
        self.simulation[thread] = False
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.simulationP[thread].pid))
        
        time.sleep(2)
        
        # Restart simulator
        self.colorAccordingToResult(thread, 1)
        self.simulationP[thread] = Popen(self.simulatorLaunchCode[thread], creationflags=CREATE_NEW_CONSOLE)
        print ( self.simulatorLaunchCode[thread] )
        time.sleep(30)
        
        os.chdir('..')

        self.simulation[thread] = True
            
    def closeEvent(self, event):
        # We are dead, kill everything that is open
        mainWin.kill_simulation()

if __name__ == "__main__":
    global mainWin
    
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    
    tl.start(block=False)
    
    sys.exit( app.exec_() )