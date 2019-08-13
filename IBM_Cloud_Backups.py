import json
import ibm_watson
from ibm_watson import ApiException
from dotenv import load_dotenv
import os
from datetime import date
import shutil
import threading
import time
import datetime
from pymongo import MongoClient
import ibm_boto3
from ibm_botocore.client import Config, ClientError

load_dotenv()

# Watson Assistant credentials
wa_version = os.getenv("wa_version")
wa_apikey = os.getenv("wa_apikey")
wa_url = os.getenv("wa_url")
# Discovery credentials
disc_version = os.getenv("disc_version")
disc_apikey = os.getenv("disc_apikey")
disc_url = os.getenv("disc_url")
disc_environment = os.getenv("disc_environment")
# Cloud Object Storage credentials
cos_apikey = os.getenv("cos_apikey")
cos_secret = os.getenv("cos_secret")
cos_endpoint = os.getenv("cos_endpoint")
cos_auth_endpoint = os.getenv("cos_auth_endpoint")
cos_resource_crn = os.getenv("cos_resource_crn")


today = date.today()

base_directory = './backups' + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
os.mkdir(base_directory)

############################################
# This section provides functions needed to
# get all document IDs from a given
# Discovery collection
############################################
def pmap_helper(fn, output_list, input_list, i):
    output_list[i] = fn(input_list[i])

def pmap(fn, input):
    input_list = list(input)
    output_list = [None for _ in range(len(input_list))]
    threads = [threading.Thread(target=pmap_helper,
                                args=(fn, output_list, input_list, i),
                                daemon=True)
               for i in range(len(input_list))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return output_list

def all_document_ids(discovery,
                     environmentId,
                     collectionId):
    doc_ids = []
    alphabet = "0123456789abcdef"
    chunk_size = 10000

    def maybe_some_ids(prefix):
        need_results = True
        while need_results:
            try:
                response = discovery.query(environmentId,
                                           collectionId,
                                           count=chunk_size,
                                           filter="extracted_metadata.sha1::"
                                           + prefix + "*",
                                           return_fields="extracted_metadata.sha1").get_result()
                need_results = False
            except Exception as e:
                print("will retry after error", e)

        if response["matching_results"] > chunk_size:
            return prefix
        else:
            return [item["id"] for item in response["results"]]

    prefixes_to_process = [""]
    while prefixes_to_process:
        prefix = prefixes_to_process.pop(0)
        prefixes = [prefix + letter for letter in alphabet]
        # `pmap` here does the requests to Discovery concurrently to save time.
        results = pmap(maybe_some_ids, prefixes)
        for result in results:
            if isinstance(result, list):
                doc_ids += result
            else:
                prefixes_to_process.append(result)

    return doc_ids
############################################

############################################
# Watson Assistant backup
############################################
if(wa_version == '' or wa_apikey == '' or wa_url == ''):
    print("No or invalid Watson Assistant credentials detected. Skipping.")
else:
    print("Starting Watson Assistant backup...")
    start_time = time.time()

    assistant_service=ibm_watson.AssistantV1(
        version = wa_version,
        iam_apikey = wa_apikey,
        url = wa_url
    )

    # Get all workspace IDs
    try:
        list_wrkspc_response = assistant_service.list_workspaces().get_result()['workspaces']
        all_wrkspc_ids = []
    except ApiException as ex:
        print("Method failed with status code " + str(ex.code) + ": " + ex.message)

    print("Getting workspace IDs...")
    for space in list_wrkspc_response:
        print("Backing up Workspace "+ space['workspace_id'] + "...")
        all_wrkspc_ids.append(space['workspace_id'])

    for id in all_wrkspc_ids:
        assistant_path = base_directory + "/assistant"+ id
        if os.path.exists(assistant_path):
            shutil.rmtree(assistant_path)
        os.mkdir(assistant_path)

        workspace_response = []
        intents_response = []
        entities_response = []

        try:
            workspace_response = assistant_service.get_workspace(
                workspace_id = id,
                export='true'
            ).get_result()

            intents_response = assistant_service.list_intents(
                workspace_id = id
            ).get_result()

            entities_response = assistant_service.list_entities(
                workspace_id = id
            ).get_result()
        except ApiException as ex:
            print("Method failed with status code " + str(ex.code) + ": " + ex.message)

        try:
            completePath = os.path.join(assistant_path, "workspace_" + id + ".json")
            workspace_file = open(completePath, "w")
            workspace_file.write(json.dumps(workspace_response))
            workspace_file.close()

            completePath = os.path.join(assistant_path, "intents_" + id + ".json")
            intents_file = open(completePath, "w")
            intents_file.write(json.dumps(intents_response))
            intents_file.close()

            completePath = os.path.join(assistant_path, "entities_" + id + ".json")
            entities_file = open(completePath, "w")
            entities_file.write(json.dumps(entities_response))
            entities_file.close()

            print("Workspace " + id + " done.")
        except Exception as e:
            print("Exception occured: " + e.message)

    end_time = time.time()
    elapsed = end_time - start_time
    print("Completed Watson Assistant backup in " + str(elapsed) + " seconds.")
######## End Watson Assistant Backup ########

############################################
# Discovery Backup
############################################
# This script will loop through every collection in the given instance and save each document. If you only want a specific collection to be backed up, remove the outer loop.

if(disc_version == '' or disc_apikey == '' or disc_url == ''):
    print("No or invalid Discovery credentials detected. Skipping.")
else:
    print("Beginning Discovery backup...")
    start_time = time.time()

    discovery_service = ibm_watson.DiscoveryV1(
        version=disc_version,
        iam_apikey=disc_apikey,
        url=disc_url
    )

    environments = discovery_service.list_environments().get_result()
    environmentId = environments["environments"][1]["environment_id"]
    allCollections = discovery_service.list_collections(environmentId).get_result()['collections']

    for collection in allCollections:
        collectionId = collection['collection_id']
        print("Backing up collection " + collectionId + "...")
        allDocIds = all_document_ids(discovery_service, environmentId, collectionId)

        discovery_path = base_directory + "/discovery" + "_" + collectionId
        if os.path.exists(discovery_path):
            shutil.rmtree(discovery_path)
        os.mkdir(discovery_path)

        try:
            training_data = discovery_service.list_training_data(environmentId, collectionId).get_result()
        except ApiException as ex:
            print("Discovery query failed with status code " + str(ex.code) + ": " + ex.message)
        try:
            completePath = os.path.join(discovery_path, "_trainingdata.json")
            discovery_file = open(completePath, "w")
            discovery_file.write(json.dumps(training_data))
            discovery_file.close()
            print("Training data for " + collectionId + " successfully saved.")
        except Exception as e:
            print("Exception occured: " + e.message)

        for documentId in allDocIds:
            filterId = '_id:' + documentId
            try:
                discQuery = discovery_service.query(environmentId, collectionId, filter=filterId).get_result()['results'][0]
            except ApiException as ex:
                print("Discovery query failed with status code " + str(ex.code) + ": " + ex.message)
            try:
                completePath = os.path.join(discovery_path, "document" + documentId + ".json")
                discovery_file = open(completePath, "w")
                discovery_file.write(json.dumps(discQuery))
                discovery_file.close()
                print("documentId " + documentId + " successfully saved.")
            except Exception as e:
                print("Exception occured: " + e.message)

        print("Collection " + collectionId + " successfully backed up.")

    end_time = time.time()
    elapsed = end_time - start_time
    print("Completed Discovery backup in " + str(elapsed) + " seconds.")

######## End Discovery Backup ########

############################################
# Cloud Object Storage
############################################
if(cos_apikey == '' or cos_resource_crn == '' or cos_auth_endpoint == '' or cos_endpoint == ''):
    print("No or invalid COS credentials detected. Skipping.")
else:
    cos = ibm_boto3.resource("s3",
        ibm_api_key_id=cos_apikey,
        ibm_service_instance_id=cos_resource_crn,
        ibm_auth_endpoint=cos_auth_endpoint,
        config=Config(signature_version="oauth"),
        endpoint_url=cos_endpoint
    )

    try:
        buckets = cos.buckets.all()
    except Exception as e:
        print("Unable to retrieve buckets: {0}".format(e))

    for bucket in buckets:
        print("Backing up Bucket {0}...".format(bucket.name))
        cos_path = base_directory + "/cos" + "_" + bucket.name
        if os.path.exists(cos_path):
            shutil.rmtree(cos_path)
        os.mkdir(cos_path)
        try:
            files = cos.Bucket(bucket.name).objects.all()
        except Exeception as e:
            print("Unable to get objects in bucket: {0}".format(e))
        for file in files:
            try:
                fileName = file.key.replace("/", "-")
                completePath = os.path.join(cos_path, fileName)
                downloadedFile = cos.meta.client.download_file(bucket.name,  file.key, completePath)
            except Exception as e:
                print("Exception occured: ")
                print(e)
        print("Bucket {0} backup complete.".format(bucket.name))
