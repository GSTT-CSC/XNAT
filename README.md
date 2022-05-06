<!-- PROJECT HEADING -->
<br />
<p align="center">
<a href="https://github.com/GSTT-CSC/CSC-QMS">
    <img src="https://raw.githubusercontent.com/GSTT-CSC/gstt-csc.github.io/main/assets/transparent-CSC-logo-cropped.png" alt="Logo" width="50%">
  </a>
<h1 align="center">XNAT</h1>
<p align="center">
Tracked documentation on XNAT
<br />

<br />
<a href="https://github.com/GSTT-CSC/XNAT">View repo</a>
·
<a href="https://github.com/GSTT-CSC/XNAT/issues">Report Error</a>
·
<a href="https://github.com/GSTT-CSC/XNAT/issues">Request Feature</a>
·
<a href="https://github.com/GSTT-CSC/XNAT/issues">Request Document</a>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#open-source-components">Open source components</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
   <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project aims to track general documentation, standard operating procedures (SOP) and helper scripts for XNAT. 

### Open source components
* [XNAT](https://xnat.org/) Imaging informatics platform which can be used to support a wide range of imaging-based projects
* [Grassroots DICOM (GDCM)](https://gdcm.sourceforge.net/) C++ library for DICOM and ACR-NEMA medical images, which is automatically wrapped to Python, C#, Java and PHP (using [SWIG](https://www.swig.org/))
* [Midnight Commander](https://midnight-commander.org/) Visual file manager, which is licensed under GNU General Public License
* [PuTTY](https://www.putty.org/) Terminal emulator, serial console and network file transfer application, which supports several network protocols, including SCP, SSH, Telnet, rlogin, and raw socket connection

<!-- GETTING STARTED -->
## Getting Started
<!-- PREREQUISITES -->
### Prerequisites
#### Secure Enclave XNAT Access

#### Local installation of PuTTY and WinSCP

<!-- OVERVIEW -->
## Overview
XNAT is a virtual platform capable of storing and managing medical images and associated data. Within Guy’s and St Thomas’ NHS Foundation Trust, it forms a part of the local secure enclave for the purposes of federated learning in artificial intelligence projects. The data is ingested from PACS into XNAT where it is anonymised and sorted into relevant projects, ensuring data is only visible to those who need it, and allowing for data deletion upon project completion. This guide describes the process of data collection, de-identification and data storage in XNAT and details how compliance with DICOM Supplement 142 is achieved.

Medical imaging data is stored in a DICOM format. DICOM stands for *Digital Imaging and Communications in Medicine* and is an international standard format for medical image storage, retrieval, processing and transfer. DICOM images consist of the actual acquired image as a set of pixels and a DICOM header. Data coded within the DICOM header are a series of attributes describing the scan and the patient. Each attribute is tagged with a unique DICOM tag which consists of a group and element number and each tag has a name to identify the type of information (or attribute) contained within the tag. This principle of data tagging allows DICOMs to be compared, transferred, stored and queried.

Before any medical data can be used in research or for training of AI algorithms, it must first be completely de-identified such that no data used can be traced back to any individual. To do this, the DICOM tags need to be altered, deleted or manipulated in such a way that the image no longer describes the individual. Because there are many DICOM tags within a DICOM header and since what is and what is not identifiable information is not always straightforward, a DICOM Standard Supplement 142 was created, outlining best anonymisation practices for purposes of clinical trials. We adopted the same standard for our de-identification purposes.

Anonymisation in XNAT is done at 2 levels: firstly when data arrives into XNAT from PACS (site-wide anonymisation) and secondly when data are moved from the pre-archive into the assigned project (project-level anonymisation).

### Data collection
Data can be ingested into XNAT via two routes:

* Pushed from PACS via Teleradiology
* Pulled from within XNAT using query-retrieve (Q/R)

Teleradiology is used for sending individual DICOM objects to XNAT. The sender must have access to Sectra and the necessary permissions to send from Sectra to ‘GSTT_XNAT’ destination. The permissions are managed by the PACS team.

Q/R is used for importing batches of data. The data required can be manually searched by accession number, patient name, patient ID or the date range; or they can be requested by uploading a .csv file. The instructions on how to format the .csv file can be found [here](https://wiki.xnat.org/xnat-tools/dicom-query-retrieve-plugin/using-dqr-bulk-querying-and-importing-via-csv-file).

### De-identification via teleradiology
Teleradiology is used to send individual DICOM objects from PACS to XNAT. As the data leave PACS, text is automatically appended to two DICOM tags: the Patient Comment Field (0010,4000) and Study Comment Field (0032,4000). The text is: 

    Project:Unassigned Subject:subj001 Session:subj001_sess001

This ensures that the patient name and accession number do not reach XNAT’s pre-archive. It instead sets the subject ID to subj001 and the session ID as subj001_sess001. This means that all data which is sent via Teleradiology from PACS will arrive in XNAT with the same subject and session ID. These are then manually changed when moving the data from pre-archive to archive by the project owner. The data in XNAT can be distinguished based on timestamp of arrival matched to the timestamp in Sectra so the project owner can tell which DICOM object belongs to which study subject. Only individual scans should be sent via this route – for batches larger than 3 to 5 scans, please use Q/R.

All other data in the DICOM headers is removed, changed or replaced as detailed in the anonymisation scripts.

### De-identification via Q/R
When data is imported using Q/R functionalities of XNAT, new subject ID and session ID can be assigned to each scan imported. It's recommended a .csv is used for DQR upload, in which case the subject and session IDs can be specified in directly in the .csv.

All other data in the DICOM headers is removed, changed or replaced as detailed in the anonymisation scripts.

### Data access and storage
The project owner has the reading, writing, updating and deleting rights of all data they own. They can grant access to other users to either view-only or modify the existing data. Data can also be shared between projects as read-only.

The data will be stored on physical storage kept with GSTT.

### Uploading data to XNAT
Before you start make yourself a cup of tea or get a snack, put on some soothing music or a podcast in the background. XNAT is slow and you will need to be patient with it else you will keep cancelling your own commands. Pop-ups can be slow and the amount of data moved takes much time. I recommend you start this at the end of the day instead of at the beginning and leave it to go over night to account for higher bandwidth demands on PACS during office hours.

1. Log into the GSTT network and open a browser.
2. Go to https://sp-pr-flipml01.gstt.local and log in with your username. If you do not have a username, contact Dika to make one for you.
3. If the project doesn’t exist yet, please contact Dika to create it. If you have any specific anonymisation requirements, please let her know about them.
4. To open your project page, click on Browse - My Projects - and select the project you're working with. This will open your project page. On the right-hand side, choose ‘Import From PACS’. Please only use this option if you have a small number of scans to upload (<100). If you have a large cohort, it's recommended to use the Rest API to perform the upload. Speak to Dika about this.
5. If your dataset is reasonably small, use the DQR. Clicking on 'Import from PACS' will open the data query-retrieve (DQR) page which allows you to query Sectra PACS for the requested images.
   1. You can use the DQR in two ways: by entering the search criteria or by importing a CSV file.
      1. Search criteria: you can use accession number or patient ID and date range and you can use * for wildcard. 
      2. Click on ‘Search PACS’. Wait for the results to show. 
      3. Once you find the correct scan(s), tick the box on the left-hand side. 
      4. Then press the ‘Begin Import’ button at the bottom of the screen. A pop-up will appear to select all series which are relevant. 
      5. Select all which are relevant (if you’re importing CTs, de-select the Dose Info, Dose Report and the Patient Protocol series, as they contain burnt-in patient data!). 
      6. Click ‘Import’. 
   2. CSV: you can upload a correctly-formatted CSV to perform a bulk search. This is described <a href=" https://wiki.xnat.org/xnat-tools/dicom-query-retrieve-plugin/using-dqr-bulk-querying-and-importing-via-CSV-file">here</a>. The CSV file should contain either your Accession Numbers (which uniquely identify a scan) or a Patient ID and a study date. If you're using the latter method, pay special attention to the formatting of the dates which should be YYYYMMDD to match the date formatting in PACS. 
      1. To do the search click on ‘import CSV’ at the top of the page. Choose your CSV file. Click on ‘upload’. The query will begin – it may take a while. If an error occurs, test your CSV file by reducing it to only one query and see if that comes up with what you expect. 
      2. Once you can query all you want at once without issue, you’ll have to select which scans to import. 
      3. NB: XNAT can only handle about 20-30 import queries at once, else it will get stuck on retrieving series information screen. If you’re importing CTs, de-select the Dose Info, Dose Report and the Patient Protocol series, as those contain burnt-in images of dates and names. Click on ‘Import Selected’. 
      4. Wait until you get a notification that the query had been sent to PACS. 
      5. Then click on ‘Close’. 
      6. You will need to upload the CSV again to select the next batch for import.
      
6. The imported data will appear in the pre-archive (Upload -> Go to prearchive). Click ‘Refresh’ if your data isn’t there, or check the Import Queue (Upload ->  Import Queue/History) – the data takes a while to transfer.
7. In the pre-archive, you can review the details of your import, such as files and DICOM tags. Once you’ve confirmed you’re happy with the data, select it in the pre-archive (tick the left-hand side checkbox) and select ‘Change projects’ on the right-hand side. Select your project. This will assign the data to your project. You can then ‘Archive’ it, which will move the data from the pre-archive into your project folder.
8. You can now view, amend and interact with the data in the project (Browse -> My Projects -> your folder). You can check the DICOM tags of each data session (click on the Subject then hover over the scan details until 3 icons appear – the first is View Details, select this to view tags), you can view the session (click on ‘View Session’ on the right-hand side). You can also delete or download the images here or in the project details.

## Scripts
Several scripts have been created to help with the data curation process and their development is ongoing. They can be grouped by the following categories representing steps in the overall process.

### Anonymisation
Patient age, size, weight, ethnic group, smoking status and pregnancy status are retained. Manufacturer private tags are removed by this script.  The manipulation of the DICOM data follows the [DICOM Standards Supplement 142](https://www.dicomstandard.org/News-dir/ftsup/docs/sups/sup142.pdf), which specifies which tags should be removed, replaced, or manipulated to ensure traceability to individual from the data shared is not possible. Some UIDs which do not contain any time of date data are also retained.

* [Site-wide anonymisation script](assets/XNAT_anonymisation/Site-wide anon script.txt)

* [Project-level anonymisation script](assets/XNAT_anonymisation/Project-specific anon script.txt)



### Resources
* [XNAT](https://www.xnat.org/)
* [DICOM Standards Supplements](https://www.dicomstandard.org/supplements)

<!-- ROADMAP -->
## Roadmap
See the [open issues](https://github.com/XNAT/MLOps/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing
<!-- CONTACT -->
## Contact

* [Dika Vilic](mailto:Dijana.Vilic@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Haleema Al Jazzaf](mailto:Haleema.AlJazzaf@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))

Project Link: [https://github.com/GSTT-CSC/XNAT](https://github.com/GSTT-CSC/XNAT)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [README template by othneildrew](https://github.com/othneildrew/Best-README-Template)
* [Neuroinformatics Research Group at Washington University](https://www.mir.wustl.edu/research/research-centers/computational-imaging-research-center-circ/labs/marcus-lab)