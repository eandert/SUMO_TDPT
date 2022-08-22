# SUMO_TPDT
Test parallelization and distribution tool for use with Simulated Urban Mobility traffic simulator. Integrates with google sheets to read test specification and to write test results. Allows for multiple SUMO tests to be run simultaneously on one computer and manages the threads. Allows for multiple computers to be used as distributed compute to run the SUMO tests, with all results being centrally collected via Google Sheets.

Installation:
Install SUMO (newest)
Install Python 3.7 (might work with newer but untested as of yet)
Clone the repo
CD into the repo
pip install -r requirements.txt
python atlas_pyqt5_interface.py
Select number of threads (suggestion is to start with 2-4 depending on computer speed), and click "start test"
Code will automatically connect to Google docs and use your computer as as slave to run tests to the links entered in the file... 
To propoerly set this up, you should copy this sheets file, add your IAM user as an editor https://docs.google.com/spreadsheets/d/1RWMaz2ryNWEKpez4O7rEn8Ysy8_xvhRLkJUOKZKN3hM/edit?usp=sharing, and finally add the unique file code into filename. 
