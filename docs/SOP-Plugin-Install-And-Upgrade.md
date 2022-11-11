[![image](https://github.com/GSTT-CSC/XNAT/blob/main/assets/CSC-logo-trans-sm.png?raw=true)](https://github.com/GSTT-CSC/XNAT)

# Plugin Upgrade and Install

This SOP describes how to upgrade and install XNAT plugins.

[View Repo](https://github.com/GSTT-CSC/XNAT) . [Report Error](https://github.com/GSTT-CSC/XNAT/issues) . [Request Feature](https://github.com/GSTT-CSC/XNAT/issues) . [Request Document](https://github.com/GSTT-CSC/XNAT/issues)

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#data-checking">Upgrading/Installing</a>
      <ul>
        <li><a href="#PII">SOP</a></li>
      </ul>
    </li>
    <li><a href="#resources">Resources</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
   <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- UPGRADING OR INSTALLING A PLUGIN IN XNAT -->
## Upgrading or installing a plugin in XNAT

XNAT has a number of plugins available, for example the OHIF viewer, forms, batch processing; even the DQR functionality 
is a plugin. This allows a high level of customisation and works in a modular way - you can take out and add plugins
as desired. 

To upgrade or install a new plugin for XNAT you'll need to restart it, so make sure this
action will not interfere with anyone's work (restarting XNAT will erase everything in the pre-archive).
You can check if any users are active online by going into Administer -> Users. If other users are logged in,
contact them before taking XNAT offline.

<!-- SOP -->
### SOP
1. First you must find the plugin you desire in the form of a .jar file. You can find a list of 
plugins [here](https://marketplace.xnat.org/plugins/), or you can [here](https://wiki.xnat.org/xnat-tools) or you can make your own
with some handy instructions on xnat website. Whatever it is, please make sure you're downloading the latest version.
2. Once you have your .jar file, you'll need to copy it onto the head node using WinSCP or the wget command. Copy the .jar file into 
``/home/hnadmin/xnat-setup/plugins``.
3. Now delete the old version of the plugin if you're upgrading by finding and deleting it from 
``/home/hnadmin/xnat-data/xnat/scripts/plugins``
4. Restart XNAT by navigating into 
``/home/hnadmin/xnat-setup/Linux`` and running 
``sudo ./restart.sh``
5. This will shut down the XNAT service and bring it back up. You can check whether the service is back up with 
``sudo docker ps``. 3 XNAT services should be running - tomcat, postgres and XNAT:latest.
6. XNAT takes approximately 2-3 minutes to load once the services are restarted. Wait, then access the website and log in again.
If XNAT doesn't come back on, it means there has been a problem with the upgrade or installation. If you run into any problems, please speak to Haleema or Dika.

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
