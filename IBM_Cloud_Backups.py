import json
import ibm_watson
from ibm_watson import ApiException
from dotenv import load_dotenv
import os
from datetime import date
import shutil
import threading

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

today = date.today()

#################################
# Functions needed to assist
#################################
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
    """
    Return a list of all of the document ids found in a
    Watson Discovery collection.

    The arguments to this function are:
    discovery      - an instance of DiscoveryV1
    environment_id - an environment id found in your Discovery instance
    collection_id  - a collection id found in the environment above
    """
    doc_ids = []
    alphabet = "0123456789abcdef"   # Hexadecimal digits, lowercase
    chunk_size = 10000

    def maybe_some_ids(prefix):
        """
        A helper function that does the query and returns either:
        1) A list of document ids
        2) The `prefix` that needs to be subdivided into more focused queries
        """
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

#################################
# Watson Assistant backup
#################################
print("Starting Watson Assistant backup...")

assistant_service=ibm_watson.AssistantV1(
    version = wa_version,
    iam_apikey = wa_apikey,
    url = wa_url
)

assistant_path = "./assistant"
# os.mkdir(assistant_path)

if os.path.exists(assistant_path):
    shutil.rmtree(assistant_path)
os.mkdir(assistant_path)

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

# In each workspace save workspace files, intents, and entities
for id in all_wrkspc_ids:
    try:
        workspace_response = assistant_service.get_workspace(
            workspace_id = id,
            export='true'
        ).get_result()
        completePath = os.path.join(assistant_path, "wa_workspace_" + id + str(today) + ".json")
        workspace_file = open(completePath, "w")
        workspace_file.write(json.dumps(workspace_response))
        workspace_file.close()

        intents_response = assistant_service.list_intents(
            workspace_id = id
        ).get_result()
        completePath = os.path.join(assistant_path, "wa_intents" + id + str(today) + ".json")
        intents_file = open(completePath, "w")
        intents_file.write(json.dumps(intents_response))
        intents_file.close()

        entities_response = assistant_service.list_entities(
            workspace_id = id
        ).get_result()
        completePath = os.path.join(assistant_path, "wa_entities_" + id + str(today) + ".json")
        entities_file = open(completePath, "w")
        entities_file.write(json.dumps(entities_response))
        entities_file.close()

        print("Workspace " + id + " done.")
    except ApiException as ex:
        print("Method failed with status code " + str(ex.code) + ": " + ex.message)

print("Completed Watson Assistant backup.")
######## End Watson Assistant Backup ########

#################################
# Discovery Backup
#################################
# This script will loop through every collection in the given instance and save each document. If you only want a specific collection to be backed up, remove the outer loop.

print("Beginning Discovery backup...")

discovery_service = ibm_watson.DiscoveryV1(
    version=disc_version,
    iam_apikey=disc_apikey,
    url=disc_url
)

environments = discovery_service.list_environments().get_result()
environmentId = environments["environments"][1]["environment_id"]

# get all collection IDs, then loop through
# allDocIds = all_document_ids(discovery_service, environmentId, collectionId)



# Create a new folder for each collection
# environments = discovery_service.list_environments().get_result()

######## End Discovery Backup ########
