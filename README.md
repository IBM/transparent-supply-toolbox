# transparent-supply-toolbox
Transparent Supply ToolBox

This tool box is provided by IBM to make the API interaction with Blockchain Transparent Supply
simpler.  One can see examples data_input.py and data_analytics.py to get a quick understanding of 
how to use the API wrappers.

*Environment Setup*

Python Virtual Environment:

1) Create a virtual environment using python3, and activate it.

$ python3 -m venv venv
$ source venv/bin/activate

2) Install all the dependencies:
$ pip -r requirements.txt

3) export BTS_TOOLBOX_BASE_PATH_DIR to the folder where you installed BTSToolBox directory.
e.g.: 
$ export BTS_TOOLBOX_BASE_PATH_DIR="/<your_home_directory>/git_repositories/transparent-supply-toolbox/python/"

*Running the Data Input Utility*

$ python data_input.py -I -o eprov -e btseprov -ixls data/eprovenance_a1_v4.xlsx -of config/myorgs_all.json -ip -dbg 1

*Running the Data Output Utility*

$ python data_analytics.py -o eprov -e btseprov -O -if config/myorgs_all.json -dbg 0
