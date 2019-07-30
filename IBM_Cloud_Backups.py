import json
import ibm_watson
from dotenv import load_dotenv
import os

load_dotenv()

# Watson Assistant credentials
wa_version = os.getenv("wa_version")
wa_apikey = os.getenv("wa_apikey")
wa_url = os.getenv("wa_url")

# Begin backup
print("Starting Watson Assistant backup...")
assistant_service=ibm_watson.AssistantV1(
    version=wa_version,
    iam_apikey=wa_apikey,
    url=wa_url
)

try:
    list_wrkspc_response=assistant_service.list_workspaces().get_result()['workspaces']
    all_wrkspc_ids = []
except ApiException as ex:
    print("Method failed with status code " + str(ex.code) + ": " + ex.message)

print("Getting workspace IDs...")
for space in list_wrkspc_response:
    print(space['workspace_id'])
    all_wrkspc_ids.append(space['workspace_id'])

for id in all_wrkspc_ids:
    try:
        workspace_response=assistant_service.get_workspace(
            workspace_id=id,
            export='true'
        ).get_result()
        wa_output_file = open("wa_workspace_" + id + ".json","w+")
        wa_output_file.write(json.dumps(workspace_response))
        wa_output_file.close()
    except ApiException as ex:
        print("Method failed with status code " + str(ex.code) + ": " + ex.message)
