# planet-tools
A set of scripts and tools for acquiring and processing data from PlanetScope CubeSats.

##Contents

**planet_scenes_acquisition.py**

Script for finding and downloading large volumes of Planet data using Planet's Data and Orders APIs. Users will need to copy and edit this script to use it (e.g., by inserting their own API key, defining their area of interest, defining the time range for the data, and choosing other filters or pre-processing tools as necessary). For small amounts of data, it may be more practical to use Planet Explorer, or the Planet plugins for QGIS and ArcGIS. To learn more about using Planet's APIs, check out Planet's github rep (linked below).

**helper_functions.R**

A set of functions implemented in R which make it easier to use and pre-process PlanetScope data. Can be loaded with 
`source('https://raw.githubusercontent.com/Spencer-Shields/planet-tools/refs/heads/main/helper_functions.R')`


## Other resources

- [Planet Labs' github](https://github.com/planetlabs/notebooks/tree/master/jupyter-notebooks)
  
  Planet's own tutorials for using its APIs to find, process, and acquire data. Walkthrough videos for the different notebooks can be found at [Planet University](https://university.planet.com/).
- [Time Series normalization](https://github.com/latmperkmol/ts-norm/tree/master)

  Python implementation of the workflow by [Leach et al. (2019)](https://www.sciencedirect.com/science/article/pii/S0168169919301243) (ex IRSS member) for normalizing time series of PlanetScope data.

- [Normalization for mosaics](https://github.com/swegmueller)

  Python implementation of the workflows by [Wegmueller et al. (2021)](https://www.sciencedirect.com/science/article/pii/S0303243420309338) to normalize adjacent PlanetScope scenes for mosaicing.

- [Cloud and shadow masking](https://github.com/Global-ecology-and-remote-sensing/PlanetScope-cloud-detection)

  Matlab implementation of the STI-ACSS algorithm by [Wang et al. (2021)](https://www.sciencedirect.com/science/article/abs/pii/S0034425721003242?via%3Dihub) for extremely accurate cloud and shadow masking.

- [Gap filling](https://github.com/Global-ecology-and-remote-sensing/PlanetScope-gap-filling)

  Matlab implementation of the workflow by [Wang et al. (2022)](https://www.sciencedirect.com/science/article/abs/pii/S0034425722002504?via%3Dihub) for filling gaps in PlanetScope time series.

Also, have a peek at [Shields et al. (2025)](https://www.sciencedirect.com/science/article/pii/S2666017225001208) for an overview of PlanetScope data and pre-processing methods.

## To access Planet data
Planet offers licenses to access its data for free for non-commercial use. If you are a student or faculty member at the University of British Columbia, then fill out [this](https://researchcommons.library.ubc.ca/planet-imagery/) form to gain access and log on to [planet.com](https://www.planet.com/) to search for data or find your API key.
