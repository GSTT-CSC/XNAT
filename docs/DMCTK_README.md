# DMCTK upload script WIP
Prelimary:
   you are not using the XNAT dicom receievr. You may have to edit docker-compose.yml (in the xnat-setup file) to remove the port mapping and restart docker (./restart.sh) 
   Edit dqr.sh - you must enter the AEC and PACS IP/PORT in the variables at the top. 
 
 


Start a dicom recieever as a process, user root:
nohup storescp -aet XNAT -od [PATH TO]/incoming_data -ss diverter DICOM_RECEIVER_PORT &

Replace DIOOM_RECEIVER_PORT to whatever port your PACS is pushing to

To run program, also as root as process:
sudo -i
Then cd to /home/hnadmin/test_qr/
Then run:
nohup /bin/bash dqr.sh CSV_FILENAME PROJECT_NAME &
Replace CSV_FILENAME with the name of the csv file - this must be int he same directory as dqr.sh, do not include the path to the file.


To stop
ps aux | grep store
ps aux | grep dqr

Find the process number and:
kill PROC_NUMBER
Replacing PROC_NUMber witht he actual process number.
 
 
