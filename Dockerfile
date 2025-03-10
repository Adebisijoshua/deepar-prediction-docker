# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the script into the container
COPY deepar_prediction.py .

# Install dependencies
RUN pip install boto3 pandas schedule

# Run the script when the container starts
CMD ["python", "deepar_prediction.py"]

