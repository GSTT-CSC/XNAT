[![image](assets/transparent-CSC-logo.png)](https://github.com/GSTT-CSC/XNAT)

# Data Import

This SOP identifies and explains the process of data import in XNAT. For any further information please contact Dika or Haleema.

[View Repo](https://github.com/GSTT-CSC/XNAT) . [Report Error](https://github.com/GSTT-CSC/XNAT/issues) . [Request Feature](https://github.com/GSTT-CSC/XNAT/issues) . [Request Document](https://github.com/GSTT-CSC/XNAT/issues)


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#overview">Overview</a>
      <ul>
        <li><a href="#projects">Projects</a></li>
        <li><a href="#subjects">Subjects</a></li>
        <li><a href="#sessions">Sessions</a></li>
        <li><a href="#Importing-longitudional-data">Importing longitudional data</a></li>
      </ul>
    </li>
    <li>
      <a href="#direct-import">Direct import</a>
      <ul>
        <li><a href="#User-interface">User interface</a></li>
        <li><a href="#Rest-API">RestAPI</a></li>
      </ul>
    </li>
    <li>
      <a href="#Importing-with-scripts">Importing with scripts</a>
      <ul>
        <li><a href="#Importing-MRI-images">Importing MRI images</a></li>
        <li><a href="#Importing-other-large-imaging-data">Importing other large imaging data</a></li>
        <li><a href="#Importing-ultrasounds-from-ISCV">Importing ultrasounds from ISCV</a></li>
        <li><a href="#Importing-complex-data">Importing complex data</a></li>
      </ul>
    </li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
   <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- Overview -->
## Overview

A PACS, which stands for Picture Archiving and Communication Systems, is any system which holds and catalogues images in a way which is economical (usually compressed) 
and practical (searchable). The main radiology PACS at GSTT is a Sectra system - radiological systems such as X-ray machines, gamma cameras and PET scanners, MRI scanners
and CT scanners, all feed the images they acquire into this main system in DICOM format. The PACS assigns each DICOM an accession number which
uniquely identifies the image in this specific PACS, and organises the images such that ownership of each image is assigned to a patient. This allows us to look up a patient 
on a PACS system and find all the images that PACS has ever received for that patient ID. Sectra is not the only PACS in use at GSTT, as other departments also
use imaging scanners and may have local PACS systems to organise their own data (for example, foetal cardiology uses ISCV, cardiology uses CVIS, radiotherapy uses ARIA and so on).

XNAT is a PACS system designed with clinical trials in mind. It expects DICOM data, organises it by subject and assigns each DICOM a unique XNAT number. 
The main difference between XNAT and a standard clinical PACS is that it organises data into projects (as it was designed for research, not routine care),
and that it allows much, much greater flexibility than a standard clinical PACS: particularly in terms of anonymisation and post-processing.

At GSTT we use XNAT to sufficiently anonymise all images we intend to use for research (within and outside of the hospital) and for service improvement and evaluation. We also
use it to remove the images from the clinical systems in a way which is safe and can never affect a clinical system - the data retrieval is one-directional. Other benefits of XNAT
lie in its powerful RestAPI (meaning many tasks can be automated) and it its container service, which allows us to program and plug in other processing tools, such as facemasking.

The problem with XNAT, however, is that as it was designed for clinical trials, it expects clean data which are well organised, consistent in size and in naming. Routine clinical data 
is anything but that - you will find, especially with MRIs, a myriad of variance in this, some will have extra images, some will have fewer, sometimes some sequences are added, some
data arrives from other hospitals and hides different information it tags, some will be strangely large for no real reasons, some will have Sectra-specific fragments of files attached.

To navigate this difficulty and still achieve scalability in our data exports and processing for research purposes, a few solutions have been created. Each have their own advantages
and disadvantages and caution and care must be taken when choosing which one to go with. If in any doubt, speak to Haleema or Dika or discuss it with the rest of the team. The consequence
of getting it wrong is mostly in the loss of time and many lessons were learned through trial and error. Similarly, if any strange behaviour is noticed, please let us know!


<!-- PROJECTS-->
### Projects

Projects can only be created by someone with admin rights. If you are a user without those, please speak to either Haleema or Dika about creating your project. You will need to know 3 things: 
the project title (full project title), running title (shortened version of the title, up to 24 characters which will appear in menus), and the project ID (a unique one word identifier - this cannot be changed and cannot be reused even if
the project is deleted), and a project description (this will let others know what the project is about). It is useful to know who the PI is, but this is optional. It is almost always the best idea to have the project ID and 
the project running title be the same.

To make a new project, in the top navigation bar, go to New -> New Project and fill in the details. Define the accessibility of the project at this point: private (only users allocated can see the data), 
protected (all users can see study title and description but can't analyse and download data), public (all users can access and download data). This should always be private unless you're using the 
project for teaching purposes. 

Once the project is created you must allocate the users who should access the project's data (go to project, then Access, then add/invite user by XNAT username).

You must also add the anonymisation script (go to project, then Manage, then Anonymization Script) to your project.

Finally, define the pre-archive behaviour of your project (go to project, then Manage, then Define Prearchive Settings) - if you need to check the data before putting it in the 
project please select the first option, else select the second one - this will allow automatic archiving.

You will be able to import data from here (<a href="#ui">Import To PACS option</a>), see your data, process your data, add files and other functions.

<!-- SUBJECTS -->
### Subjects

Each subject in an XNAT project must have a unique name - this is most easily achieved by simply numbering the subjects in a sequence. 
It is also frequently useful to add more information about the subject in the subject name directly, such as 002_Negative and 003_Positive, 
so you can understand your data at a glance. You can also code clinical information directly into subject name by assigning numbers to possible diagnoses
and adding the code to the subject name, eg Subject001_2_0 where Subject001 is the number of the subject, 2 stands for 'diabetes type' and 0 stands for 'no cardiovascular disease'.

<!-- SESSIONS -->
### Sessions

Each session within a project must have a unique name - this means across all subjects in the project! For example, if you have subject 001 with 2 sessions, say session_01 and session_02,
subject 002 cannot contain a session called session_01 or session_02 even though the session. The easiest way to navigate this is to name the sessions by the subject and then the sequence of the session, eg:
subject 001 with sessions 001_1 and 001_2 and subject 002 with sessions 002_1 and 002_2. If this is not followed, you'll get conflicts on data imports. Please also bear in mind that these names should be short and 
easily distinguished. They may also contain clinical information if appropriate, eg subject 001 can have a session 001_PRE and 001_POST where 001_PRE stands for 'before intervention' and 001_POST stands for 'after intervention'.

<!-- LONGITUDIONAL -->
### Importing longitudional data

As discussed in the section above - each subject may have more than one session and the order of these may have relevance to your algorithm. As such, please follow the 
session naming convention highlighted above. XNAT will automatically put sessions belonging to the same subject together, so long as the subject name given is consistent - this
means that if you import two sessions from PACS for one patient and give one session the subject name of 001 and the other session the subject name of 002, XNAT will think these are two separate 
subjects and will catalogue them as such. 

<!-- DIRECT IMPORT -->
## Direct Import

<!-- UI -->
### User interface

XNAT has a neat 'import from PACS' functionality which enables data query and retrieve (DQR) directly from PACS. You can search it by accession number, 
patient name or study date. This method is only appropriate for a handful of imports at a time though, as XNAT will try and display all series descriptions for you first
to give you a choice in which imaging series within a session you wish to download. If many sessions are querried at the same time, the system jams and times out.
This is useful mostly for troubleshooting and testing - it is not suitable for dozens or hundreds of imports because the timing out issue created by series description fetching
means you have to keep refreshing the page and starting again. The XNAT website does not recommend trying more than 20 at a time, but I would lower this to 10.

The detailed process on how to download from XNAT using the UI is available <a href="https://gstt-csc.github.io/SOPs.html#XNATupload">here</a>.

<!-- RestAPI -->
### Rest API

You will need administration rights for this. If this is a functionality you need, please speak to Haleema or Dika. 

RestAPI is, in essence and very simplified, a back door to a web application where data can be exchanged efficiently and effectively without going through the UI. In XNAT this means you can
get data on settings (and change those settings), get information on things like how many items are in the queue for import (and control this queue), and so on. It can be found by going
to Administer ->  Site Administration -> Miscellaneous -> Swagger [view swagger page].

To import data through this method, you will need a csv and details on your project ID and the PACS number for the PACS you want to query. You can get the PACS
number by finding the <b>dqr-pacs-api</b> function and running the <b>pacs</b> function (click on it, then click 'try it out', then 'execute' - the output will be a list of PACS available, you will need the number 
in the "id" section). Your project ID will be visible in your project details under ID. The manner in which the csv must be formatted is described <a href="https://gstt-csc.github.io/SOPs.html#XNATupload">here</a>.
It is vital the csv is formatted correctly with the correct headings or it will not work - if you have trouble, please contact Dika or Haleema.

First you need to run a query. Find <b>dicom-query-retrieve-api</b> on the list and go to <b>/dqr/query/batch</b>. Click 'try it out', choose your csv, add PACS ID number and click execute.
This can only handle about 200 lines in a csv, if there are more, it may time-out. If it does, split your csv and then try again.

A successful query will return a JSON file you can download. Within it will be all the studies that were found on PACS that matched the query and will depend on the content of your csv: 
if you only ran it with patient IDs, you will get a list of all studies related to those IDs, but if you had accession numbers, you will get details only on those accession numbers. Please note that 
it also provides the remapping tag for you as defined in your csv. Each subject will have their own "studies" nested information which will end with remapping information before closing, then another "studies" is open (this 
will make more sense when you have it in front of you).

You will need to edit this JSON now to effectively list the studies you wish to import in a single "studies" command, though the JSON has given you many. 
You have to remove all data you don't need from the list - pay close attention to where the brackets start and end. I find it useful to open the JSON in Excel for editing,
some have used VBA to filter for them, and a programming solution for this is underway. 

Once you have removed all data you don't want to import from your JSON and have a single "studies": at the beginning of the JSON and have carefully ensured each
study to be imported is effectively relabelled with a unique subject and session ID, add the following line to the top of your JSON:

``{"aeTitle": "XNAT","forceImport": true, "pacsId" : 1,"port":8105, "projectId": "PROJECT_ID", "xnatProject" : "PROJECT_NAME", "studies" : [ LIST OF YOUR STUDIES FROM {studyInstanceUid to the 
end of your last relabelMap} }]} ``

Replace the '1' with your actual PACS ID and replace the port number with 51621 if youre importing from RT Aria. Speak to Dika
if you have any issues with this.

Now find the <b>/dqr/import</b> function in the <b>dicom-query-retrieve-api</b> and click on 'Try it out', copy your script into it, and press 'Execute'.

This will queue your downloads and they should appear in the XNAT UI under Upload -> PACS Import Queue and History -> Queue. It may take a couple of minutes.
If they do not appear there, something has gone wrong. Please try again or seek help.

This method is useful for approximately 50 or so scans at a time. More than that and it will time out. This method is also prone to failure of import of individual scans, 
particularly as too many items in the queue jam the Sectra port and the connection is lost until the jam is cleared which depends on size of data already in queue. 
If your dataset is bigger or more complex, we need to use the scripts. Proceed with absolute caution and do not attempt this unless fully trained to do so though, 
as scripts are run on the head node with root privileges and thus the potential for disaster is substantial.

<!-- SCRIPT IMPORT -->
## Importing with scripts

There are two main scripts currently in use for bulk import: one using DCMTK and the other using the RestAPI. The one that uses RestAPI (currently named import-tester) essentially
follows the steps listed above, except that instead of setting off a list of studies at once it tries to queue one at a time with 1 minute between, and if the PACS connection is lost
or the scan fails to import for another reason it will try again 50 times before it moves onto the next one. This was designed specifically to overcome congestion issues. The dcmtk script,
currently named test_qr, does not use XNAT but instead queries the PACS directly, ingests the data, and then pushes that data to XNAT without getting XNAT involved. This was designed to overcome
the issues of MRI imaging sessions not arriving into XNAT completed.

The import-tester will be quicker in retrieving your data, but may return incomplete results if what you're fetching are MRIs. It's fine for most other imaging modalities.
The test_qr is slower but more robust. It is particularly useful for MRIs. Proceed with caution, seek advice if in doubt, and do not do this unless you have been trained to do so 
or are being supervised by an XNAT superuser.

<!-- MRIS -->
### Importing MRI Images

Because the script developed for MRI ingestion uses DCMTK and not XNAT, you'll first need to change the PACS receiver. 
To do this, log into the server via Putty as hnadmin. Input the address (sp-pr-flipml01) and the credentials to gain access. 
Navigate to /home/hnadmin/xnat-setup/ then type in ``sudo mc`` and navigate to ``docker-compose.yml`` using keyboard arrows and then
press F4 - this will open the yaml file for editing. Comment out the line that says ``105:8105`` using ``#``. This command effectively opens the port for XNAT
and closes it for other processes, so when you blank it out of the yaml file, it frees it up again. This is the port that Sectra is connected to. This
is currently the only PACS this script has been designed for, so if you need data from a different PACS, speak to Dika or Haleema.

After you've changed the docker compose, you must restart XNAT for changes to take effect. To do this, close the midnight commander (using F10), then 
navigate into /home/hnadmin/xnat-setup/Linux and run ``sudo ./restart.sh``. 4 processes will close, then 3 will be re-instigated. Once it's done,
you can check if all has been restored successfully with ``docker ps`` - there should be 3 processes that will have been restarted less than a minute ago (nginx, postgres for xnat and xnat).

Now you need to get you csv onto the server. This script ONLY WORKS WITH ACCESSION NUMBERS - patient ID & study date won't work here. You can 
use your patient ID & study date combo to query PACS in the RestAPI (when the correct receiver is on, of course) and get accession numbers that way.

You can either put the csv onto dropbox or use WinSCP on your GSTT desktop to do this. If you put it on your desktop,
navigate to /home/hnadmin/test_qr and put the file there using either WinSCP or by typing in ``wget https://www.dropbox.com/YOUR_FILE_URL``. Once the folder is in, 
obtain root rights by running ``sudo -i`` followed by admin password. You'll now be signed in as <b>root</b>. Now navigate to the test_qr folder (``cd /home/hnadmin/test_qr/``) 
then run 

``nohup /bin/bash dqr.sh CSV_NAME.csv PROJECT_ID``

The process will start. nohup is a text file which will have outputs of what is happening and you can open it win WinSCP. It should be listing one accession 
number at a time and its corresponding studyUID. If you see anything else there may have been an error. 

The process will now run until it is done - this may take a few hours or a few days, depending on the size of your csv. You can close Putty now, the process will continue.

If you want to check if the process is still running, run

``ps aux | grep dqr``

You'll see the process you initiated listed there. If you need to end it, use 

``kill PROCESS ID`` [process ID is the 7 digit number in the second column].

It will take some time before the images begin to appear in XNAT - they will appear in prearchive, probably one at a time. If they do not begin to appear within half an hour, 
there is likely to have been an error: consult your XNAT superusers, the nohup text file and kill and restart the process if need be.

<!-- OTHER IMAGING DATA -->
### Importing other large imaging data

This script is simpler than test_qr and you do not need root access to run it. This script uses XNAT Rest APi so the receiver must be set
such that ``105:8105`` is enabled. If that is not the case, follow the procedure as described in the previous section except delete the ``#`` in front of 
``105:8105`` in the docker compose instead of adding it. Then restart xnat.

For this script you need to put your csv into ``/home/xnat-data/xnat/scripts/import-dqr/`` folder. You can either use WinSCP to get it there or 
use ``wget`` as described in the previous section. Then type in ``cd`` which will take you back to hnadmin home, then run

``./import-tester.sh CSV_NAME.csv PROJECT_ID PACS_ID MODALITY``

Where 'modality' is whatever the main modality in your dataset is. Once you press enter to run it, you'll see the screen become populated
with the contents of your csv file (accession numbers, subject ids, session ids). Please note that this may take a while if you have a very large file (e.g. 1000 ultrasounds).
Then it will begin the import one at a time. It will print each as it tries to import it onto the screen. You will see errors come up if there are issues.
Please note that this script uses Rest API and thus suffers from the same PACS congestion issue as Rest API scheduling, but this script will try and import each scan for up to 50 times until
it is successfully queued. 

You can end this process by pressing ``command + c``. If you want it to continue to run but you want to exit Putty, simply close the Putty window down - the downloads will continue.

<!-- FOETAL CARDIOLOGY ULTRASOUNDS -->
### Importing ultrasounds from ISCV

ISCV is a PACS which is in use for foetal cardiology at GSTT. It differs from Sectra in a few ways but most important one is that accession numbers are not a part
of ISCV in the same way as they are to Sectra - there are faux accession numbers that you will see if you try and import some data but they consist of the date of scan and some
other numbers and are not reliably useful for data fetching. Instead, patient ID and study date must be used to locate images. PACS id for ISCV is 2.

To downloads ISCV data in bulk, first upload your csv file to ``/home/xnat-data/xnat/scripts/import-dqr/`` as above. Then run

``./import-tester-ISCV.sh CSV_NAME.csv PROJECT_ID 2 US``

You should see the same outputs on your screen as when you use import-tester script. If there is an issue an error will be shown on the screen. Sometimes
an error arises from empty spaces in the Excel file before 'patient ID' - these aren't visible in Windows but are visible to a Unix system. If you see ``\f`` or similar being
output onto your screen and the images are failing one after the other, kill the process (``command + c ``) and fix your csv file through the midnight commander 
(``sudo mc -> navigate to csv -> select csv using keyboard arrows -> F4 -> delete the characters before P in Patient ID -> F2 to save -> F10 to exit``) and run the process again.

<!-- COMPLEX DATA -->
## Importing complex data

If you have a need for other complex data, such as very heavy data or something XNAT has not yet been optimised for (e.g. raw PET images, CBCT, Aria plans), 
please speak to Haleema or Dika to discuss how best approach the task at hand, especially if the above solutions are not appropriate.

<!-- RESOURCES -->
## Resources
* [XNAT](https://www.xnat.org/)
* [DICOM Standards Supplements](https://www.dicomstandard.org/supplements)

<!-- ROADMAP -->
## Roadmap
See the [open issues](https://github.com/GSTT-CSC/XNAT/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

<!-- CONTACT -->
## Contact

* [Dika Vilic](mailto:Dijana.Vilic@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Haleema Al Jazzaf](mailto:Haleema.AlJazzaf@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Project Link](https://github.com/GSTT-CSC/XNAT)


