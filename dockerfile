# Use an official Python runtime as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY close_batches_venv/requirements.txt .

# Create and activate the Python virtual environment
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate"

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files to the working directory
COPY close_batches_venv/app.py app.py
COPY close_batches_venv/close_incident.py close_incident.py
COPY close_batches_venv/batches_and_incidents.py batches_and_incidents.py
COPY close_batches_venv/creds.py creds.py

# Set environment variables
ENV API_USERNAME="API_USERNAME"
ENV API_PASSWORD="API_PASSWORD"
ENV EMAIL="EMAIL"

# Expose the port your Flask application is running on
EXPOSE 5004

# Set the entry point command for the container
CMD ["python", "app.py"]
