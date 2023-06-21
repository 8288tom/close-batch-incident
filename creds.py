import os

# Alternatively you can add the API username/Password
idomoo_api_cred = {
    "username": os.getenv("API_USERNAME"),
    "pwd":os.getenv("API_PASSWORD")
}

# Add Pager Duty API Key
pd_cred={
    "Authorization":"PD Token"
}

# Add Pager Duty User's email that the incidents will be closed by
email = os.getenv("EMAIL")

