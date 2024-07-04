import requests
import concurrent.futures
import creds
import time
import requests as r
import os
batch_username = creds.idomoo_api_cred.get("username")
batch_pwd = creds.idomoo_api_cred.get("pwd")
pd_token = creds.pd_cred.get("Authorization")

def refresh_token():
    auth = (batch_username, batch_pwd)
    response = r.post("https://usa-api.idomoo.com/api/v3/oauth/token", auth=auth)
    token_data = response.json()
    print("Token generated:", token_data)
    
    expires_at=int(time.time())+ token_data['expires_in']
    os.environ['API_TOKEN']=token_data['access_token']
    os.environ['TOKEN_EXPIRATION_TIME']=str(expires_at)
    return token_data    

def is_token_expired(expiration_time):
    current_time = time.time()
    print("Current time:", current_time)
    stored_expiration_time = int(os.getenv('TOKEN_EXPIRATION_TIME', 0))
    print("Token expiration time:", stored_expiration_time)
    return current_time > stored_expiration_time

def get_api_token():
    if os.getenv('API_TOKEN') and not is_token_expired(os.getenv('TOKEN_EXPIRATION_TIME')):
        return os.getenv('API_TOKEN')
    else:
        token_data = refresh_token()
        return token_data['access_token']


def get_batches():
    token = get_api_token()      
    open_batches = []
    batch_urls = [
        "http://internal-api-eu.idmadm.com:8080/api/v3",
        "http://internal-api-us.idmadm.com:8080/api/v3"
    ]
    headers = {"x-idomoo-api-mode": "support","Authorization": f"Bearer {token}"}
    params = {"limit":50}

    for url in batch_urls:
        try:
            response = r.get(url,headers=headers,params=params, verify=False)
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

get_batches()


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

            # Process incident

            for incident in incidents_list:
                incident_title = incident["title"]
                incident_id = incident["id"]
                incident_status = incident["status"]
                if incident_title.startswith("File"):
                    file_name = incident_title.split('File ')[1].split(' from')[0]
                    if file_name.lower().endswith(".csv"):
                        base_name = os.path.splitext(file_name)[0]  # Remove the .csv extension
                        file_name = base_name + ".csv"  # Add .csv extension back
                    else:
                        file_name = file_name

                    valid_extensions = {".zip", ".gpg", ".pgp", ".txt"}  # Set of valid extensions
                    while '.' in file_name:
                        base_name, extension = os.path.splitext(file_name)  # Split base name and extension
                        if extension.lower() not in valid_extensions:
                            break
                        file_name = base_name

                    open_incidents.append({"id": incident_id, "file_name": file_name, "status": incident_status})
                else:
                    continue
        else:
            print("Error occurred while retrieving incidents:")
            print(f"Status Code: {response.status_code}")
            print(f"Error Message: {response.text}")

    return open_incidents