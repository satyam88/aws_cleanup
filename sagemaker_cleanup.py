import boto3
import time
from botocore.exceptions import ClientError

REGION = "ap-south-1"   # change if needed
DRY_RUN = False          # True = only show what will be deleted, False = actually delete

sm = boto3.client("sagemaker", region_name=REGION)


# -----------------------------
# Helper
# -----------------------------
def log(msg):
    print(f"[INFO] {msg}")


def safe_call(func, **kwargs):
    try:
        return func(**kwargs)
    except ClientError as e:
        print(f"[ERROR] {func.__name__}: {e}")
        return None


# -----------------------------
# 1) PROCESSING JOBS
# -----------------------------
def cleanup_processing_jobs():
    log("Checking Processing Jobs...")
    statuses = ["InProgress", "Completed", "Failed", "Stopped", "Stopping"]

    for status in statuses:
        next_token = None
        while True:
            params = {
                "StatusEquals": status,
                "MaxResults": 100,
                "SortBy": "CreationTime",
                "SortOrder": "Descending"
            }
            if next_token:
                params["NextToken"] = next_token

            resp = safe_call(sm.list_processing_jobs, **params)
            if not resp:
                break

            jobs = resp.get("ProcessingJobSummaries", [])
            for job in jobs:
                name = job["ProcessingJobName"]
                state = job["ProcessingJobStatus"]

                print(f"ProcessingJob: {name} | Status: {state}")

                if state == "InProgress":
                    if DRY_RUN:
                        print(f"  -> Would STOP processing job: {name}")
                    else:
                        safe_call(sm.stop_processing_job, ProcessingJobName=name)

                elif state in ["Completed", "Failed", "Stopped"]:
                    if DRY_RUN:
                        print(f"  -> Would DELETE processing job: {name}")
                    else:
                        safe_call(sm.delete_processing_job, ProcessingJobName=name)

            next_token = resp.get("NextToken")
            if not next_token:
                break


# -----------------------------
# 2) TRAINING JOBS
# -----------------------------
def cleanup_training_jobs():
    log("Checking Training Jobs...")
    statuses = ["InProgress", "Completed", "Failed", "Stopped", "Stopping"]

    for status in statuses:
        next_token = None
        while True:
            params = {
                "StatusEquals": status,
                "MaxResults": 100,
                "SortBy": "CreationTime",
                "SortOrder": "Descending"
            }
            if next_token:
                params["NextToken"] = next_token

            resp = safe_call(sm.list_training_jobs, **params)
            if not resp:
                break

            jobs = resp.get("TrainingJobSummaries", [])
            for job in jobs:
                name = job["TrainingJobName"]
                state = job["TrainingJobStatus"]

                print(f"TrainingJob: {name} | Status: {state}")

                if state == "InProgress":
                    if DRY_RUN:
                        print(f"  -> Would STOP training job: {name}")
                    else:
                        safe_call(sm.stop_training_job, TrainingJobName=name)

                elif state in ["Completed", "Failed", "Stopped"]:
                    if DRY_RUN:
                        print(f"  -> Would DELETE training job: {name}")
                    else:
                        safe_call(sm.delete_training_job, TrainingJobName=name)

            next_token = resp.get("NextToken")
            if not next_token:
                break


# -----------------------------
# 3) ENDPOINTS
# -----------------------------
def cleanup_endpoints():
    log("Checking Endpoints...")
    next_token = None

    while True:
        params = {"MaxResults": 100}
        if next_token:
            params["NextToken"] = next_token

        resp = safe_call(sm.list_endpoints, **params)
        if not resp:
            break

        endpoints = resp.get("Endpoints", [])
        for ep in endpoints:
            name = ep["EndpointName"]
            status = ep["EndpointStatus"]

            print(f"Endpoint: {name} | Status: {status}")

            if DRY_RUN:
                print(f"  -> Would DELETE endpoint: {name}")
            else:
                safe_call(sm.delete_endpoint, EndpointName=name)

        next_token = resp.get("NextToken")
        if not next_token:
            break


# -----------------------------
# 4) ENDPOINT CONFIGS
# -----------------------------
def cleanup_endpoint_configs():
    log("Checking Endpoint Configs...")
    next_token = None

    while True:
        params = {"MaxResults": 100}
        if next_token:
            params["NextToken"] = next_token

        resp = safe_call(sm.list_endpoint_configs, **params)
        if not resp:
            break

        cfgs = resp.get("EndpointConfigs", [])
        for cfg in cfgs:
            name = cfg["EndpointConfigName"]
            print(f"EndpointConfig: {name}")

            if DRY_RUN:
                print(f"  -> Would DELETE endpoint config: {name}")
            else:
                safe_call(sm.delete_endpoint_config, EndpointConfigName=name)

        next_token = resp.get("NextToken")
        if not next_token:
            break


# -----------------------------
# 5) MODELS
# -----------------------------
def cleanup_models():
    log("Checking Models...")
    next_token = None

    while True:
        params = {"MaxResults": 100}
        if next_token:
            params["NextToken"] = next_token

        resp = safe_call(sm.list_models, **params)
        if not resp:
            break

        models = resp.get("Models", [])
        for model in models:
            name = model["ModelName"]
            print(f"Model: {name}")

            if DRY_RUN:
                print(f"  -> Would DELETE model: {name}")
            else:
                safe_call(sm.delete_model, ModelName=name)

        next_token = resp.get("NextToken")
        if not next_token:
            break


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    cleanup_processing_jobs()
    print("-" * 80)

    cleanup_training_jobs()
    print("-" * 80)

    cleanup_endpoints()
    print("-" * 80)

    cleanup_endpoint_configs()
    print("-" * 80)

    cleanup_models()
    print("-" * 80)

    log("Cleanup scan completed.")
    if DRY_RUN:
        log("DRY_RUN=True, nothing deleted. Change DRY_RUN=False to actually delete.")
