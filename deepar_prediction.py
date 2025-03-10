# Paste your entire Python script here
import boto3
import json
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta

# Define AWS resources
s3 = boto3.client('s3')
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Configuration
S3_BUCKET = 'training90210'  # Update with your bucket
S3_KEY = 'openaq_location_352507_2measurments.csv'
ENDPOINT_NAME = 'forecasting-deepar-2025-02-13-14-05-03-380'  # Update with your endpoint name
OUTPUT_S3_KEY = 'predictions/deepar_predictions.json'


def get_latest_data():
    """Fetch the last 76 hours of data from S3."""
    obj = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
    df = pd.read_csv(obj['Body'])

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    if 'datetimelocal' not in df.columns:
        raise KeyError(f"Column 'datetimelocal' not found. Available columns: {df.columns}")

    # Convert 'datetimelocal' to pandas datetime
    df['datetimelocal'] = pd.to_datetime(df['datetimelocal'], utc=True)

    # Use the last available timestamp instead of the current time
    latest_time = df['datetimelocal'].max()
    cutoff_time = latest_time - timedelta(hours=76)

    # Debugging
    print(f"Latest available timestamp: {latest_time}")
    print(f"Adjusted Cutoff Time: {cutoff_time}")

    # Filter for the last 76 hours based on dataset timeframe
    df = df[df['datetimelocal'] >= cutoff_time]
    df = df.sort_values(by='datetimelocal')

    if df.empty:
        raise ValueError("No data available for prediction after filtering.")

    return df[['datetimelocal', 'value']]


def prepare_payload(df):
    """Format data as required by DeepAR."""
    if df.empty:
        raise ValueError("No data available for prediction.")

    # Ensure correct column name is used
    data = {
        "instances": [{
            "start": df['datetimelocal'].min().strftime("%Y-%m-%dT%H:%M:%S"),
            "target": df['value'].tolist()
        }]
    }
    return json.dumps(data)


def invoke_deepar(payload):
    """Invoke the deployed DeepAR model."""
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='application/json',
        Body=payload
    )
    result = json.loads(response['Body'].read().decode())
    return result


def store_predictions(predictions):
    """Save predictions to S3."""
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=OUTPUT_S3_KEY,
        Body=json.dumps(predictions)
    )
    print("Predictions stored in S3.")


def job():
    """Run the prediction pipeline."""
    print("Running scheduled DeepAR prediction...")
    df = get_latest_data()
    payload = prepare_payload(df)
    predictions = invoke_deepar(payload)
    store_predictions(predictions)
    print("DeepAR prediction completed.")


# Schedule the job every hour
schedule.every().hour.do(job)

# Run the job once immediately when executing the script
if __name__ == "__main__":
    job()  # Run immediately
    while True:
        schedule.run_pending()
        time.sleep(60)  # Wait for a minute before checking again
