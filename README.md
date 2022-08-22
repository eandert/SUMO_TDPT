# SUMO_TPDT
Test parallelization and distribution tool for use with Simulated Urban Mobility traffic simulator. Integrates with google sheets to read test specification and to write test results. Allows for multiple SUMO tests to be run simultaneously on one computer and manages the threads. Allows for multiple computers to be used as distributed compute to run the SUMO tests, with all results being centrally collected via Google Sheets.

##Installation:

1. Install SUMO (newest)
2. Install Python 3.7 (might work with newer but untested as of yet)
3. Clone the repo
4. CD into the repo
5. 'pip install -r requirements.txt'
6. Set up a Google IAM user if you have not already: https://cloud.google.com/iam/docs/creating-managing-service-accounts
7. To properly set this up, you should copy this sheets file https://docs.google.com/spreadsheets/d/1RWMaz2ryNWEKpez4O7rEn8Ysy8_xvhRLkJUOKZKN3hM/edit?usp=sharing , add your IAM user as an editor, and finally add the unique file code into settings.json as the "input_file" field. 
8. Next your need to copy this sheets file https://docs.google.com/spreadsheets/d/1Vq31R13NK41VGh8cxcdQbqVgtaChXSy9zgzSEsdrvxo/edit?usp=sharing, add your IAM user as an editor, and the unique ID as "output_file" in the settings.json file.
9. Next your need to copy this sheets file https://docs.google.com/spreadsheets/d/14HkluJxeqEWhP14ZKEZifmuXP1DvDyD-L9x7MaQ0dYg/edit?usp=sharing, add your IAM user as an editor, and the unique ID as "thread_monitor" in the settings.json file.
10. Finally, type in the command 'python atlas_pyqt5_interface.py'
11. Select number of threads (suggestion is to start with 2-4 depending on computer speed), and click "start test"
12. Code will automatically connect to Google docs and use your computer as as slave to run tests to the links entered in "settings.json"
