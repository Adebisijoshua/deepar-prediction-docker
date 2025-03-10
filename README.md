# 📦 DeepAR Prediction Docker

This project packages a DeepAR time-series forecasting script into a Docker container.  
It fetches data from AWS S3, processes it, sends it to an AWS SageMaker DeepAR model, and stores the predictions back in S3.

---

## 🚀 How I Built the Docker Image
I built the Docker image, by navigating to the project folder and run:

```sh
docker build -t deepar-prediction .


# Dependencies I Installed in the Image

The Dockerfile installs the following dependencies inside the container:

    boto3 → AWS SDK for Python (used to connect to S3 & SageMaker)

    pandas → For handling time-series data

    schedule → To run the script on an hourly schedule


# I installed the dependencies using :

RUN pip install boto3 pandas schedule


# Now that the image has been built the container can be ran using ::::

docker run -v ~/.aws:/root/.aws deepar-prediction.



## If you want to use the pre-built image instead of building it, pull it from Docker Hub using :::

  .......docker pull adebisi8/deepar-prediction:latest

Then run it using  
........docker run -v ~/.aws:/root/.aws adebisi8/deepar-prediction

