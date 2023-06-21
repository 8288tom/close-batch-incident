import requests
import creds
from batches_and_incidents import get_batches, get_open_batch_incidents
from time import sleep


pd_token = creds.pd_cred.get("Authorization")


def match_incident_to_batch():
    # Fetch the list of open incidents and batches
    list_of_incidents = get_open_batch_incidents()
    print(f"List of open incidents: {list_of_incidents}")
    list_of_batches = get_batches()
    print(f"List of unarchived batches: {list_of_batches}")
    sleep(5)

    for incident in list_of_incidents:
        incident_id = incident["id"]
        file_name = incident["file_name"]
        incident_resolved = incident["status"] == "resolved"
        print("This is the incident inside the loop: ", incident)

        if incident_resolved:
            # Skip resolved incidents
            print("Incident already resolved: ", incident_id, file_name)
            continue

        batch_matched = False
        batch_id = ""  # Default value for batch ID

        for batch in list_of_batches:
            print("This is the batch inside the loop: ", batch)
            if incident["file_name"] == batch["file_name"]:
                # Match found, close the incident and write resolution note
                batch_id = batch["batch_id"]
                close_incident(incident_id, file_name)
                write_resolution_note(incident_id, str(batch_id), file_name)
                batch_matched = True
                break

        if not batch_matched:
            # No match found for the incident
            print(f"No match found for incident: Batch_ID:{batch_id} , PD_Incident:{incident_id} , File:{incident['file_name']}")

def write_resolution_note(incident_id, batch_id, file_name):
    # Send resolution note for the incident
    incident_url = f"https://api.pagerduty.com/incidents/{incident_id}/notes"
    headers = {"Authorization": pd_token, "From": creds.email}
    body = {
        "note": {
            "content": "batch_id:" + batch_id
        }
    }

    response = requests.post(incident_url, headers=headers, json=body)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Successfully sent resolution note for:{file_name} batch:{batch_id}")
    else:
        print("Error occurred while retrieving incidents:")
        print("Status Code: ", response.status_code)
        print("Error Message: ", response.text)

def close_incident(incident_id, file_name):
    # Close the PagerDuty incident
    incident_url = f"https://api.pagerduty.com/incidents/{incident_id}"
    headers = {"Authorization": pd_token, "From": creds.email}
    body = {
        "incident": {
            "type": "incident",
            "status": "resolved"
        }
    }

    response = requests.put(incident_url, headers=headers, json=body)

    if response.status_code == 200 or response.status_code == 201:
        print("Successfully closed incident for File: ", file_name)
    else:
        print("Error occurred while retrieving incidents:")
        print("Status Code: ", response.status_code)
        print("Error Message: ", response.text)
