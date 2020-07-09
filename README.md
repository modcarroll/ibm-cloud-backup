![PyPI pyversions](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue)

# IBM Cloud Backup Tool

A Python script to backup data from specific IBM Cloud services. If you are interested in having functionality for another service, please create a pull request.

This tool includes the ability to backup data from the following services:
- Watson Assistant :green_heart: (skills, logs)
- Discovery :green_heart: (documents from all collections, training data) >> Please note, this section may take quite some time depending on how many documents and collections you have.
- Cloud Object Storage :green_heart: (contents in every bucket)
- DB2 (Coming soon!)


## Setup

### Dependencies:
- [Python 3.5 or greater](https://www.python.org/downloads/)
- [IBM COS Python SDK](https://github.com/IBM/ibm-cos-sdk-python)
- [Watson Developer Cloud Python SDK](https://pypi.org/project/ibm-watson/)


### To Run:
1.) Install prerequisites (Python packages listed above)

2.) Add your service credentials to the top of the IBM_Cloud_Backups.py file in the specified variables. (For Cloud Object Storage, you can find your `cos_endpoint` here depending on your region: https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints)

4.) Run `python3 IBM_Cloud_Backups.py`


## Important notes:

The skills for Watson Assistant are downloaded in a format that allows you to upload them back into Watson Assistant as-is if needed.

If you want to run this tool only for a subset of the listed services, delete the credential block(s) for the service(s) that you do not want to backup. Detailed instructions are written as comments in the code.

Quite a few python packages are used in this application. While all of them may not be listed here, if you try and run the program but get a `ModuleNotFound` error, simply install the package it specifies. I recommend using pip3, which is already installed with Python3.

## License

[GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.en.html)
