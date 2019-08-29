# IBM Cloud Backup Tool

A Python script to backup data from specific IBM Cloud services. If you are interested in having functionality for another service, please create a pull request.

:heart: -> To do

:yellow_heart: -> In progress

:green_heart: -> Complete

This tool is a work-in-progress. When the first iteration is complete, it will include the ability to backup data from the following services:
- Watson Assistant :green_heart: (workspaces, entities, intents)
- Discovery :green_heart: (documents from all collections, training data) >> Please note, this section may take quite some time depending on how many documents and collections you have.
- Cloud Object Storage :green_heart: (contents in every bucket)
- App ID :yellow_heart:
- Databases for PostgreSQL :heart:
- Databases for MongoDB :heart:

## Setup

### Dependencies:
- [Python3](https://www.python.org/downloads/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [ibm-cos-sdk](https://github.com/IBM/ibm-cos-sdk-python)
- [pymongo](https://api.mongodb.com/python/current/)


### To Run:
1.) Install prerequisites (Python packages)

2.) Rename `example.env` to `.env`

3.) Add your service credentials to the .env file.

4.) Run `python3 IBM_Cloud_Backups.py`


## Important notes:

Please keep in mind that with Data and AI services, training data is not saved.

The entities, intents, and workspace files for Watson Assistant are downloaded in a format that allows you to upload them back into Watson Assistant as-is if needed.

If you want to run this tool only for a subset of the listed services, simply leave the credentials for all the other services BLANK.

If you get a timeout error for MongoDB, you may need to add your IP address to the Whitelist on the settings tab of the Databses for MongoDB service.

Issues will arise if you don't use pymongo version 3.4.0. To install, `pip install pymongo==3.4.0` or `pip3 install pymongo==3.4.0`

Quite a few python packages are used in this application. While all of them may not be listed here, if you try and run the program but get a `ModuleNotFound` error, simply install the package it specifies. I recommend using pip3, which is already installed with Python3.

------

## License

[GNU General Public License] (https://www.gnu.org/licenses/gpl-3.0.en.html)
