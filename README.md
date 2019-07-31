# IBM Cloud Backup Tool

A Python script to backup data from specific IBM Cloud services. If you are interested in having functionality for another service, please create a pull request.

:heart: -> To do

:yellow_heart: -> In progress

:green_heart: -> Complete

This tool is a work-in-progress. When the first iteration is complete, it will include the ability to backup data from the following services:
- Kubernetes Clusters :heart:
- App ID :heart:
- Databases for PostgreSQL :heart:
- Discovery :green_heart: (documents from all collections, training data) >> Please note, this section may take quite some time depending on how many documents and collections you have.
- MongoDB :heart:
- Watson Assistant :green_heart: (workspaces, entities, intents)
- Cloud Object Storage :heart:

Please keep in mind that with Data and AI services, training data is not saved.

### Prerequisites
[IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cloud-cli-getting-started) (>= 0.18.0)

[Python3](https://www.python.org/downloads/)

[python-dotenv](https://pypi.org/project/python-dotenv/)


### To Run
1.) Rename `example.env` to `.env`

2.) Add your service credentials to the .env file.

3.) Run `python3 IBM_Cloud_Backups.py`
