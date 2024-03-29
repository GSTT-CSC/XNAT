[![image](https://github.com/GSTT-CSC/XNAT/blob/main/assets/CSC-logo-trans-sm.png?raw=true)](https://github.com/GSTT-CSC/XNAT)

# Data Checking

This SOP describes how to check data to ensure adequate anonymisation has taken place before images can be used for research
and service improvement and evaluation processes.

[View Repo](https://github.com/GSTT-CSC/XNAT) . [Report Error](https://github.com/GSTT-CSC/XNAT/issues) . [Request Feature](https://github.com/GSTT-CSC/XNAT/issues) . [Request Document](https://github.com/GSTT-CSC/XNAT/issues)

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#data-checking">Data Checking</a>
      <ul>
        <li><a href="#PII">PII</a></li>
      </ul>
    </li>
    <li><a href="#DICOM-tags">DICOM Tags</a>
    <li>
      <a href="#Burnt-in-data">Burnt-in data</a>
      <ul>
        <li><a href="#Ultrasounds">Ultrasounds</a></li>
        <li><a href="#Patient-Protocols-and-Dose-Reports">Patient Protocols and Dose Reports</a></li>
        <li><a href="#Screenshots">Screenshots</a></li>
        <li><a href="#Annotations">Annotations</a></li>
        <li><a href="#Miscellaneous">Miscellaneous</a></li>
      </ul>
    </li>
    <li><a href="#high-definition-faces">High definition faces</a></li>
    <li>
        <a href="#project-management-tools">Project management tools</a>
        <ul>
            <li><a href="#project-contents">Project contents</a></li>
            <li><a href="#accession-number-trace">Accession number trace</a></li>
            <li><a href="#ingestion-statuses">Ingestion statuses</a></li>
        </ul>
    </li>
    <li><a href="#project-contents">Helpers</a></li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
   <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- DATA CHECKING -->
## Data Checking


<!-- PII -->
### PII

Personal identifiable information (PII) is any information that can directly or indirectly identify an individual from
their data. Examples of directly identifiable data are first and last name, date of birth, or a home address. Examples of 
indirectly identifiable data are date of scan, diagnosis, first half of postcode. 

All PII from medical images must be removed before the images can be used for research. This protects the identity of the individuals 
imaged and it is our legal and moral duty to our service users not to divulge their personal data nor abuse our access to it.
The anonymisation must therefore be sufficient to achieve the goal of separating the individual from their data in a manner which ensures
no link can be re-established between the two. 

National Data Opt Out (NDOO) further ensures that service users have a right to withdraw their consent to any of their medical data being
used for research or service development, i.e. secondary purposes. If they do have a recorded opt-out status, their data must therefore be excluded.

Within Guy's and St Thomas' NHS Foundation Trust (GSTT), the currently most straightforward way to check the opt-out statuses is to do so via the [NDOO Check Service](https://optout.gstt.nhs.uk/#/login) web application. This can only be accessed by staff with valid GSTT email addresses and whilst on the Trust VPN. 

Users can either manually input one or more NHS numbers on the website itself, or they can submit a CSV file containing up to 100,000 NHS numbers per request. If users are unable to identify the NHS numbers of one or more patients within their cohort, the general recommendation from the Information Governance (IG) team is to exclude them.

Based on their submissions, users will then receive a response file (to the email address provided in the original submission) containing the NHS numbers of patients who have **not** opted out and whose data may be included.

> :warning: **Users should not be maintaining a record of the patients who have opted out!** Please take care in only using the response file for the purpose of complying the NDOO policy and adhering to the data retention policy as outlined in the project's Data Protection Impact Assessment (DPIA).

We recommend users reach out to the IG team for their further advice if they believe there are:
- Project-specific patient opt-in processes that should take precedence over the NDOO policy 
- Patients who should still be included in their project despite not having identified their NHS numbers and therefore their NDOO opt-out statuses

For more details on the NDOO Check Service or ongoing work to directly query NHS Digital's NDOO database via their API, please reach out to [Haleema](mailto:Haleema.AlJazzaf@gstt.nhs.uk) or [Dika](mailto:mailto:Dijana.Vilic@gstt.nhs.uk). 

<!-- DICOM TAGS -->
## DICOM Tags

DICOM is a data format and a networking protocol used in medical imaging. Each DICOM file holds information on the person in the image (PII) and
information about the scan itself (e.g. equipment, imaging protocol, time and date of scan), and the information which forms the image (a set of pixel
data and a decoder of the pixel data). The data are contained in DICOM tags. Each tag is labelled (e.g. (0008,0010)) by what data it represents. This
allows for integration across systems and ensures data can be filtered, found, and communicated between hospitals. 

The DICOM tags contain direct and indirect PII and therefore must be manipulated to achieve our goal of separating the individual from the data. In XNAT
we do this using a script, written in DicomEdit, which outlines all DICOM tags which need to be removed (e.g. patient name) or changed to mask the true data (e.g. 
dates are shifted by a fixed number of days). However, manufacturers frequently add additional data in some tags (called Private Tags) and not all modalities 
use the same tags (for example: a nuclear medicine DICOM file will contain information on the radiopharmaceutical used and the activity injected, which an X-ray will not,
and similarly a CT scan will have details on radiation beam used to acquire the image while an MRI will hold data on pulse sequence used). This means that 
for some data the script we use is not optimised. Because of this, DICOM tags must be checked on a representative subset of data before the total set is ingested.

To do this, first ingest a few scans (I recommend around 3 per modality) into XNAT and check the DICOM tags. To do this, open the project to 
which you archive the data, then open the subject, then open the experiment you wish to check. Hover your mouse just right of the scan number (middle of the page where
all scans are listed in a numbered order). 3 icons will appear, select the 'view details', then 'view DICOM headers. A window will open 
and you'll see all the DICOM tags pertaining to that scan. Look through them and pay careful attention to presence of dates, names, postcodes, accession numbers and patient IDs.
The dates should be delayed by a few days from what the scan was originally but they should be consistent across the whole header. There should be no names, no postcodes, and no accession numbers
remaining in the header.

Once you have confirmed that the anonyisation script was adequate for your project, you can ingest the rest of the data. If you find errors, you need to amend
the script and try again. If you need help with this, please speak to [Dika](mailto:mailto:Dijana.Vilic@gstt.nhs.uk) or [Haleema](mailto:Haleema.AlJazzaf@gstt.nhs.uk).

<!-- BURNT-IN DATA -->
## Burnt-in data

Burnt-in data are PII data which are part of the actual image. They are especially common in ultrasounds, but also in CT's patient protocols and dose reports.
Annotations are also common and may also constitute PII. 


<!-- ULTRASOUNDS -->
### Ultrasounds

All ultrasounds data have burnt-in data which needs to be removed. If you have only static images, you can use pixelcleaning.py script for banner removal.
If you have cine images as well (which is usually the case), you'll need to decompress them first, then run the python script, then recompress. Please follow the SOP-iFIND!

<!-- Patient Protocols and Dose Reports -->
### Patient Protocols and Dose Reports

Patient protocols and dose reports should not be ingested or should not be forwarded externally. You can filter them out at ingestion into XNAT or at 
the downloading stage. If you do need them, for removal of burnt-in data, you will need to use pixelcleaning.py 
script and deid pydicom package. This is described in SOP-iFIND and should work on all burnt-in data but as always - check first!

<!-- SCREENSHOTS -->
### Screenshots

Screenshots and screengrabs frequently contain PHI, especially in modalities such as PET and nuclear medicine. Check whether these are actually needed 
for your project and if not filter them out in the same way you filter out dose reports and patient protocols. If you do need them, you can either
manually remove the PHI using any image processor or a Python script to crop the PHI out of the shot.

<!-- Annotations -->
### Annotations

Annotations may also contain PHI - but not always. If your dataset is annotated, please speak to the project owner and whoever annotated the images
to find out if the data is or is not PHI. Annotations are frequently added as overlays and may be 'turned off', but if they are merged with the DICOM, the removal
task may be more complex. In cases where the annotations are merged with DICOM, annotation-free DICOMs should also exist: ensure you only ingest or download those. 

<!-- Miscellaneous -->
### Miscellaneous

Sometimes other data may also be found - pdfs, PACS fragments you can't open, occasional note named after the patient, and the DICOM tags may
sometimes (rarely) contain entire clinical reports. It's important to spot check for these in your dataset, but it is not realistic to check each scan 
individually. If you see anything that doesn't look like it belongs in the imaging session, delete it; and pay attention when downloading data where the series
names are listed and ensure you don't download anything that contains PHI.

<!-- HIGH DEFINITION FACES -->
## High-definition Faces

Only head MRIs are considered to have sufficient resolution for face rendering (and what's more identifiable than a face?), so you don't 
have to worry about head CTs. All high definition face images must be post-processed with facemasking. To learn how to do this, please 
have a look at the Facemasking SOP.

<!-- PROJECT MANAGEMENT TOOLS -->
## Project Management Tools
The following sections cover various methods to help track a projects subjects, traced accession numbers based on patient IDs and study dates, and ingestion statuses.

<!-- PROJECT CONTENTS -->
### Project Contents
There are two ways to check the contents of your project, depending on what you need: 

- To count the sessions:
  - Open your project in XNAT
  - In the right-hand corner of the section, click on 'Subjects'
  - There will be two buttons, i.e. 'Reload' and 'Options' 
  - Click 'Options' 
  - Select 'Spreadsheet'
    - This will download a spreadsheet with a list of all subjects and the number of sessions held for each subject. 
- To get a list of all session names contained in the project:
  - Write the following into your browser:`https://sp-pr-flipml01.gstt.local/REST/projects/<INSERT YOUR XNAT PROJECT ID HERE>/experiments`
    - You can find your XNAT project ID on the project landing page in the Details section under ID 
  - This will open an HTML site of all experiments contained in the project
  - Copy the contents into a text file
  - Save it
  - Open the file in Excel
  - Select 'Delimited' in the Text Import Wizard pop-up
  - Click Next
  - Ensure the Tab checkbox is ticked
  - Click Finish
    - You should have an easy-to-use spreadsheet of sessions contained, the date of each session and the upload date.

<!-- ACCESSION NUMBER TRACE -->
### Accession number trace
You can use the `report.py` script [here](https://github.com/GSTT-CSC/XNAT/blob/46a68b5e47756ec6026bd9b5ee37dbc92235abcb/xnat-csc/scripts/report.py) to map the original CSV file(s) submitted to XNAT's Swagger UI to trace accession numbers based on patient ID and study date(s).

> :warning: Please ensure you are using Python >= 3.0 and have installed the required packages beforehand.
> To install the required packages, run `pip install -r requirements.txt`.

> :warning: The current version of the script assumes that the CSV file(s) is in the format Swagger/XNAT's REST API accepts for `/dqr/query/batch`, and requires the CSV files to contain **Patient ID** and **Study Date** columns.
> The values in the **Study Date** column should be entered as **YYYYMMDD**.

To run the script:
- Place the CSV file(s) and Swagger response JSON file(s) in a single folder
- Run `python report.py <DIRECTORY PATH> accession-trace <STUDY DESCRIPTION FILTER> <OUTPUT FILENAME>`
  - If you would like to **not** filter the JSON response results based on a certain study description, i.e. return all results, insert "All".

For help, run `python report.py <DIRECTORY PATH> ingestion-status -h `


<!-- INGESTION STATUSES -->
### Ingestion statuses
> :warning: Please ensure you are using Python >= 3.0 and have installed the required packages beforehand.
> To install the required packages, run `pip install -r requirements.txt`.

You can also use the `report.py` script [here](https://github.com/GSTT-CSC/XNAT/blob/46a68b5e47756ec6026bd9b5ee37dbc92235abcb/xnat-csc/scripts/report.py) to assign an ingestion status based on:
- An XNAT project's [spreadsheet](#project-contents), i.e. which contains a list of all subjects and the number of sessions held for each subject
- XNAT's Swagger UI response JSON file(s) based on CSV file(s) submitted for subjects that were not successfully ingested

To run the script:
- Place the project's spreadsheet CSV file and Swagger response JSON file(s) in a single folder
- Run `python report.py <DIRECTORY PATH> ingestion-status <OUTPUT FILENAME>`

For help, run `python report.py <DIRECTORY PATH> ingestion-status -h `

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

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [README template by othneildrew](https://github.com/othneildrew/Best-README-Template)
* [Neuroinformatics Research Group at Washington University](https://www.mir.wustl.edu/research/research-centers/computational-imaging-research-center-circ/labs/marcus-lab)
