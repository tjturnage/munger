# munger

scripts that leverage Daryl Herzmann l2munger files for DRT simulations
https://github.com/akrherz/l2munger



    This takes Nexrad Archive 2 files and applies l2munger so that times are updated to near the current time and the data are remapped to a new radar location. The "munged" files can then be used for Displaced Real-Time (DRT) simulations with GR2Analyst can be performed. Playback speed can be set so that radar files are made available slower than, faster than, or equal to the actual time elapsed between the radar files.