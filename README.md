# planet-tools
A set of scripts and tools for acquiring and processing data from PlanetScope CubeSats.


## Other resources
Have a look at [Shields et al. (2025)](https://www.sciencedirect.com/science/article/pii/S2666017225001208) for an overview of PlanetScope data and pre-processing methods.

Other resources:
- [PlanetLabs github](https://github.com/planetlabs/notebooks/tree/master/jupyter-notebooks)
  
  Planet's own tutorials for using its APIs to find, process, and acquire data
- [Time Series normalization](https://github.com/latmperkmol/ts-norm/tree/master)

  Python implementation of the workflow by [Leach et al. (2019)](https://www.sciencedirect.com/science/article/pii/S0168169919301243) (ex IRSS member) for normalizing time series of PlanetScope data

- [Normalization for mosaics](https://github.com/swegmueller)

  Python implementation of the workflows by [Wegmueller et al. (2021)](https://www.sciencedirect.com/science/article/pii/S0303243420309338) to normalize adjacent PlanetScope scenes for mosaicing

- [Cloud and shadow masking](https://github.com/Global-ecology-and-remote-sensing/PlanetScope-cloud-detection)

  Matlab implementation of the STI-ACSS algorithm by [Wang et al. (2021)](https://www.sciencedirect.com/science/article/abs/pii/S0034425721003242?via%3Dihub) for extremely accurate cloud and shadow masking.

- [Gap filling](https://github.com/Global-ecology-and-remote-sensing/PlanetScope-gap-filling)

  Matlab implementation of the workflow by [Wang et al. (2022)](https://www.sciencedirect.com/science/article/abs/pii/S0034425722002504?via%3Dihub) for filling gaps in PlanetScope time series.


## To access Planet data
Planet offers licenses to access its data for free for non-commercial use. If you are a student or faculty member at the University of British Columbia, then fill out [this](https://researchcommons.library.ubc.ca/planet-imagery/) form to gain access and log on to [planet.com](https://www.planet.com/) to search for data or find your API key.
