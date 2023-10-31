# DMCTK upload script

To run the DCMTK script you will need to do the following:
1. create a folder outside the XNAT Docker (anywhere in your file system is fine but on the same server as your XNAT)
2. put into said folder 2 directories: an 'incoming_data' directory and 'xnatscripts' directory
3. put your dqr.py file into the xnatscripts directory
4. put your .csv into the xnatscripts directory
5. You will not be going via XNAT but you will use its DICOM receiver.
6. You will have to edit docker-compose.yml (in the xnat-setup file) to remove the port mapping and restart docker (./restart.sh) to free up the port.
7. Edit dqr.py - you must enter the AET and PACS IP/PORT in the variables at the top. 
8. You may need to edit in_dir to reflect where you put your incoming_data directory
9. You may need to adjust time delays and batch sizes based on the data size and complexity - do this in dqr.py
10. Check that the path in line shutil.move points to correct directory for XNAT import
11. Follow the instructions below

Start a dicom receiver as a process as root:

``nohup storescp -aet XNAT -od [PATH TO]/incoming_data -su diverter DICOM_RECEIVER_PORT &``

Replace DICOM_RECEIVER_PORT to whatever port your PACS DICOM node is set to.

To run program, also as root as process:

``sudo -i``

Then 

``cd /home/hnadmin/test_qr/``

Then run:

``nohup python3 -u /xnat-install/xnatscripts/dqr.py CSV_FILENAME PROJECT_NAME 0 &``

if you have an accession numbers list and 

``nohup python3 -u /xnat-install/xnatscripts/dqr.py CSV_FILENAME PROJECT_NAME 1 &``

if you have a patient ID + study date list (NB. - not thoroughly tested method!)


Replace CSV_FILENAME with the name of the csv file - this must be in the same directory as dqr.py, do not include the path to the file.

You can keep an eye on your import by checking the 

To stop
``ps aux | grep store``
``ps aux | grep dqr``

Find the process number and:

``kill PROC_NUMBER``

Replacing PROC_NUMBER with the actual process number.
 
 
