[![image](https://github.com/GSTT-CSC/XNAT/blob/main/assets/CSC-logo-trans-sm.png?raw=true)](https://github.com/GSTT-CSC/XNAT)

# XNAT Training

Tracked documentation on mandatory XNAT training for all users.

[View Repo](https://github.com/GSTT-CSC/XNAT) . [Report Error](https://github.com/GSTT-CSC/XNAT/issues) . [Request Feature](https://github.com/GSTT-CSC/XNAT/issues) . [Request Document](https://github.com/GSTT-CSC/XNAT/issues)


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#background">Background</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
      </ul>
    </li>
    <li>
        <a href="#overview">Overview</a>
        <ul>
          <li><a href="#pii">Personally Identifiable Information (PII) and its importance</a></li>
          <li><a href="#dicom">Digital Imaging and Communications in Medicine (DICOM)</a></li>
          <li><a href="#deidentification">De-identification, anonymisation, and pseudo-anonymisation</a></li>
          <li><a href="#roleofxnat">Role of XNAT in Guy's and St Thomas' NHS Foundation Trust (GSTT)</a></li>
          <li><a href="#xnat">XNAT</a></li> 
            <ul>
                <li><a href="#useraccess">User access</a></li>
                <li><a href="#dataimport">Data import</a></li>
                <li><a href="#dataprocessing">Data processing post-import</a></li>
                <li><a href="#dataexport">Data export</a></li>
                <li><a href="#tipsandtricks">Tips and tricks</a></li>
            </ul>
        </ul>
    </li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- BACKGROUND -->
## Background

Before individuals are granted access to XNAT, they are required to undergo a mandatory training session, which is delivered by a member of the Clinical Scientific Computing (CSC) team who has XNAT administrator privileges. These sessions are usually scheduled as and when new user requests are submitted to the CSC team.  

Similar to other GSTT mandatory training, existing XNAT users are also required to periodically retake this training to update their training compliance records (see the CSC Quality Management System (QMS) repository [here](https://github.com/GSTT-CSC/CSC-QMS) for more information).   

### Prerequisites
GSTT XNAT users are required to:
- Have a valid GSTT email address
- Have their Information Governance (IG) training up-to-date
- Access the platform whilst connected to the Trust VPN, i.e. either on a Trust computer on-site or via Citrix

<!-- OVERVIEW -->
## Overview
The training session covers a high-level overview of XNAT, data that can be imported, processed, and exported, data governance, and recommended best practices. The training session is delivered virtually over Microsoft Teams, and usually takes around 30 to 60 minutes to complete a walkthrough of the following concepts.

<!-- PII -->
### Personally Identifiable Information (PII) and its importance
Personally identifiable information (PII) is information personal to an individual and enables the identification (or re-identification) of that individual. In healthcare, patient data includes PII, such as their demographic information collected upon their initial registration with the Trust, administrative information collected when their appointments are scheduled, and clinical information collected throughout their treatment at the Trust.

We recommend referring to NHS Digital's resources [here](https://digital.nhs.uk/services/national-data-opt-out/understanding-the-national-data-opt-out/confidential-patient-information) and [here](https://digital.nhs.uk/services/national-data-opt-out/operational-policy-guidance-document/appendix-6-confidential-patient-information-cpi-definition) for more information, but given the importance of PII and the potential negative impact when inappropriately used, XNAT users are required to bear this in mind and adhere to best practices, e.g. de-identification, data transfer/sharing, etc., throughout their use of the platform.

This is includes:
- Using de-identification, anonymisation, and/or pseudo-anonymisation scripts in XNAT or as part of data processing post-import if required, e.g. as part of project approvals
- Ensuring patients who have opted out of use of their data for secondary purposes, i.e. indirect care such as research, are removed from related projects
- Storing and transferring data exported from XNAT on secure devices and via secure transfer protocols approved by the Trust 

<!-- DICOM -->
### Digital Imaging and Communications in Medicine (DICOM)

<!-- DEIDENTIFICATION -->
### De-identification, anonymisation, and pseudo-anonymisation

<!-- ROLE OF XNAT -->
### Role of XNAT in Guy's and St Thomas' NHS Foundation Trust (GSTT)

<!-- XNAT -->
### XNAT

<!-- USER ACCESS -->
#### User access

<!-- DATA IMPORT -->
#### Data import
There are several methods to import data from a PACS into XNAT, which are detailed [here](https://github.com/GSTT-CSC/XNAT/blob/main/docs/SOP-Data-Import.md) and include:
- Data query retrieve (DQR)
- REST API
- Scripting
- On the XNAT graphical user interface (GUI), i.e. CSV upload
           
<!-- DATA PROCESSING POST-IMPORT -->
#### Data processing post-import
Data processing post-import includes:
- Anonymisation per DICOM tags in XNAT
- Face masking, i.e. obfuscate personally identifiable facial features
- De-identification of ultrasounds, i.e. obfuscate burnt-in data

There are also options available in the XNAT platform itself, such as the [XNAT Open Health Imaging Foundation (OHIF) Viewer](https://wiki.xnat.org/documentation/xnat-ohif-viewer/using-the-xnat-ohif-viewer-122978515.html) and querying structured data.
<!-- DATA EXPORT -->
#### Data export
There are several ways to download from XNAT, such as downloading:
- Directly
- In bulk
- Via the server backend
<!-- TIPS AND TRICKS -->
#### Trips and tricks
Due to the IT security restraints on third-party application installation on Trust environments, there are some DICOM viewers well-suited to view DICOMs exported from XNAT as they do not require installation, e.g. [MicroDICOM](https://www.microdicom.com/) and [ImageJ](https://imagej.net/).
<!-- RESOURCES -->
## Resources
* [XNAT](https://www.xnat.org/)
* [DICOM Standards Supplements](https://www.dicomstandard.org/supplements)

<!-- CONTRIBUTING -->
## Contributing
- Fork or clone the Project
- Create your new feature, bug fix, etc. branch, i.e. `git checkout -b feature/AmazingFeature` or `git checkout -b bug/BugFix`
  - If you are creating a branch to resolve an existing [Issue](https://github.com/GSTT-CSC/XNAT/issues), we recommend creating your branch linked to that issue, i.e. open the Issue on your web browser and select _**Create a branch for this issue or link a pull request**_ under the **Development** section in the right-hand sidebar:
  <br>![img.png](../assets/branch-linked-to-issue.png)
- Commit your changes, i.e. `git commit -m 'Add some AmazingFeature'`
- Push to the remote, i.e. `git push origin feature/AmazingFeature`
- Open a Pull Request (PR) and specify that you want to merge your branch into the `main` branch

<!-- CONTACT -->
## Contact

* [Dika Vilic](mailto:Dijana.Vilic@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [Haleema Al Jazzaf](mailto:Haleema.AlJazzaf@gstt.nhs.uk) ([GSTT-CSC](https://gstt-csc.github.io/))
* [CSC Team](mailto:CSCTeam@gstt.nhs.uk)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [README template by othneildrew](https://github.com/othneildrew/Best-README-Template)
* [Neuroinformatics Research Group at Washington University](https://www.mir.wustl.edu/research/research-centers/computational-imaging-research-center-circ/labs/marcus-lab)
