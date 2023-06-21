import requests
import concurrent.futures
import creds
import requests as r


batch_username = creds.idomoo_api_cred.get("username")
batch_pwd = creds.idomoo_api_cred.get("pwd")
pd_token = creds.pd_cred.get("Authorization")



def get_batches():
    open_batches = []
    batch_urls = [
        "https://eur-api.idomoo.com/api/v2/batches/support/all",
        "https://usa-api.idomoo.com/api/v2/batches/support/all"
    ]
    auth = (batch_username, batch_pwd)
    headers = {"x-idomoo-api-mode": "support"}
    params = {"limit":50}

    for url in batch_urls:
        try:
            response = r.get(url, auth=auth, headers=headers,params=params, verify=False)
            response.raise_for_status()  # Raise an exception if the response status is not 2xx
            batches = response.json().get("batches", [])
            for batch in batches:
                batch_id = batch["batch_id"]
                batch_file_name = batch["batch_file_name"]
                open_batches.append({"batch_id": batch_id, "file_name": batch_file_name})

        except requests.exceptions.RequestException as e:
            print(f"Error occurred while accessing URL: {url}")
            print(str(e))
        except Exception as e:
            print("An error occurred:")
            print(str(e))
    print(f"Collected batches from Metadata API call: {open_batches}")
    return open_batches

def get_open_batch_incidents():
    open_incidents = []

    # Define incident URL and headers
    incident_url = "https://api.pagerduty.com/incidents?statuses%5B%5D=triggered&statuses%5B%5D=acknowledged"
    headers = {"Authorization": pd_token}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit incident request
        print("Sending API call to get Open Incidents from PD")
        incident_response = executor.submit(requests.get, incident_url, headers=headers)

        # Wait for incident response and process it
        response = incident_response.result()

        if response.status_code == 200:  # Successful response
            incidents_list = response.json().get("incidents", [])

            # Process incidents
            for incident in incidents_list:
                incident_title = incident["title"]
                incident_id = incident["id"]
                incident_status = incident["status"]
                if incident_title.startswith("File"):
                    file_name = incident_title.split('File ')[1].split(' from')[0]
                    if file_name.endswith((".zip", ".ZIP", ".gpg", ".GPG")):
                        file_name = file_name[:-4]  # Remove the last 4 characters
                    open_incidents.append({"id": incident_id, "file_name": file_name, "status": incident_status})
                else:
                    continue

        else:
            print("Error occurred while retrieving incidents:")
            print(f"Status Code: {response.status_code}")
            print(f"Error Message: {response.text}")

    return open_incidents
