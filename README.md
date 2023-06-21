# close_batch_incident
Script to run on docker container using Flask to close Pager Duty Incidents if a batch was uploaded

This script was written in order to automate mundane task of closing Pager Duty incidents as part of our monitoring process.
When a file is uploaded to an SFTP, an incident is triggered on Pager Duty and we have to make sure the file was processed.
This script checks if the file was processed, if it did it will close the incident with the id of the file.

Can't elaborate more since the rest is confidential to the company I work at.
