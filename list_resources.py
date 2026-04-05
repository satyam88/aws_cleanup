import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

REGION = "ap-south-1"

def print_header(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ClientError as e:
        print(f"[ERROR] {e}")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

# ---------------------------
# EC2 INSTANCES
# ---------------------------
def check_ec2_instances():
    print_header("RUNNING / STOPPED EC2 INSTANCES")
    ec2 = boto3.client("ec2", region_name=REGION)
    response = safe_call(ec2.describe_instances)
    found = False

    if response:
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                state = instance.get("State", {}).get("Name")
                if state in ["running", "stopped"]:
                    found = True
                    print({
                        "ResourceType": "EC2",
                        "InstanceId": instance.get("InstanceId"),
                        "State": state,
                        "InstanceType": instance.get("InstanceType"),
                        "LaunchTime": str(instance.get("LaunchTime")),
                        "Warning": "Running EC2 costs money. Stopped EC2 may still incur EBS charges."
                    })
    if not found:
        print("No EC2 instances found.")

# ---------------------------
# EBS VOLUMES
# ---------------------------
def check_unattached_ebs():
    print_header("UNATTACHED EBS VOLUMES")
    ec2 = boto3.client("ec2", region_name=REGION)
    response = safe_call(ec2.describe_volumes)
    found = False

    if response:
        for vol in response.get("Volumes", []):
            if len(vol.get("Attachments", [])) == 0:
                found = True
                print({
                    "ResourceType": "EBS",
                    "VolumeId": vol.get("VolumeId"),
                    "SizeGB": vol.get("Size"),
                    "Type": vol.get("VolumeType"),
                    "State": vol.get("State"),
                    "AZ": vol.get("AvailabilityZone"),
                    "Warning": "Unattached EBS volume still costs money."
                })
    if not found:
        print("No unattached EBS volumes found.")

# ---------------------------
# ELASTIC IPs
# ---------------------------
def check_unused_eips():
    print_header("UNUSED ELASTIC IPS")
    ec2 = boto3.client("ec2", region_name=REGION)
    response = safe_call(ec2.describe_addresses)
    found = False

    if response:
        for eip in response.get("Addresses", []):
            if "InstanceId" not in eip and "NetworkInterfaceId" not in eip:
                found = True
                print({
                    "ResourceType": "ElasticIP",
                    "PublicIp": eip.get("PublicIp"),
                    "AllocationId": eip.get("AllocationId"),
                    "Warning": "Unused Elastic IP may incur charges."
                })
    if not found:
        print("No unused Elastic IPs found.")

# ---------------------------
# LOAD BALANCERS
# ---------------------------
def check_load_balancers():
    print_header("LOAD BALANCERS")
    found = False

    elb = boto3.client("elb", region_name=REGION)
    response = safe_call(elb.describe_load_balancers)
    if response:
        for lb in response.get("LoadBalancerDescriptions", []):
            found = True
            print({
                "ResourceType": "Classic ELB",
                "Name": lb.get("LoadBalancerName"),
                "DNSName": lb.get("DNSName"),
                "Warning": "Load Balancer incurs hourly cost."
            })

    elbv2 = boto3.client("elbv2", region_name=REGION)
    response = safe_call(elbv2.describe_load_balancers)
    if response:
        for lb in response.get("LoadBalancers", []):
            found = True
            print({
                "ResourceType": lb.get("Type", "ALB/NLB"),
                "Name": lb.get("LoadBalancerName"),
                "State": lb.get("State", {}).get("Code"),
                "DNSName": lb.get("DNSName"),
                "Warning": "ALB/NLB incurs hourly cost."
            })

    if not found:
        print("No Load Balancers found.")

# ---------------------------
# NAT GATEWAYS
# ---------------------------
def check_nat_gateways():
    print_header("NAT GATEWAYS")
    ec2 = boto3.client("ec2", region_name=REGION)
    response = safe_call(ec2.describe_nat_gateways)
    found = False

    if response:
        for nat in response.get("NatGateways", []):
            state = nat.get("State")
            if state in ["available", "pending"]:
                found = True
                print({
                    "ResourceType": "NAT Gateway",
                    "NatGatewayId": nat.get("NatGatewayId"),
                    "State": state,
                    "SubnetId": nat.get("SubnetId"),
                    "Warning": "NAT Gateway is one of the most expensive forgotten lab resources."
                })
    if not found:
        print("No active NAT Gateways found.")

# ---------------------------
# RDS
# ---------------------------
def check_rds():
    print_header("RDS INSTANCES")
    rds = boto3.client("rds", region_name=REGION)
    response = safe_call(rds.describe_db_instances)
    found = False

    if response:
        for db in response.get("DBInstances", []):
            found = True
            print({
                "ResourceType": "RDS",
                "DBIdentifier": db.get("DBInstanceIdentifier"),
                "Engine": db.get("Engine"),
                "Status": db.get("DBInstanceStatus"),
                "Class": db.get("DBInstanceClass"),
                "Warning": "RDS instance incurs hourly cost."
            })
    if not found:
        print("No RDS instances found.")

# ---------------------------
# EKS
# ---------------------------
def check_eks():
    print_header("EKS CLUSTERS")
    eks = boto3.client("eks", region_name=REGION)
    response = safe_call(eks.list_clusters)
    found = False

    if response:
        for cluster in response.get("clusters", []):
            found = True
            print({
                "ResourceType": "EKS",
                "ClusterName": cluster,
                "Warning": "EKS control plane + worker nodes may incur significant cost."
            })
    if not found:
        print("No EKS clusters found.")

# ---------------------------
# ECS
# ---------------------------
def check_ecs():
    print_header("ECS CLUSTERS")
    ecs = boto3.client("ecs", region_name=REGION)
    response = safe_call(ecs.list_clusters)
    found = False

    if response:
        for cluster in response.get("clusterArns", []):
            found = True
            print({
                "ResourceType": "ECS",
                "ClusterArn": cluster,
                "Warning": "Check ECS tasks/services/EC2 backing resources."
            })
    if not found:
        print("No ECS clusters found.")

# ---------------------------
# ECR
# ---------------------------
def check_ecr():
    print_header("ECR REPOSITORIES")
    ecr = boto3.client("ecr", region_name=REGION)
    response = safe_call(ecr.describe_repositories)
    found = False

    if response:
        for repo in response.get("repositories", []):
            found = True
            print({
                "ResourceType": "ECR",
                "RepositoryName": repo.get("repositoryName"),
                "RepositoryUri": repo.get("repositoryUri"),
                "Warning": "Stored images consume storage and may cost money."
            })
    if not found:
        print("No ECR repositories found.")

# ---------------------------
# CLOUDWATCH LOG GROUPS
# ---------------------------
def check_log_groups():
    print_header("CLOUDWATCH LOG GROUPS")
    logs = boto3.client("logs", region_name=REGION)
    paginator = logs.get_paginator("describe_log_groups")
    found = False

    for page in paginator.paginate():
        for lg in page.get("logGroups", []):
            stored = lg.get("storedBytes", 0)
            if stored > 0:
                found = True
                print({
                    "ResourceType": "CloudWatchLogs",
                    "LogGroupName": lg.get("logGroupName"),
                    "StoredBytes": stored,
                    "Warning": "CloudWatch logs can slowly accumulate cost."
                })

    if not found:
        print("No billable CloudWatch Log Groups found.")

# ---------------------------
# SNAPSHOTS
# ---------------------------
def check_snapshots():
    print_header("EBS SNAPSHOTS (OWNED BY YOU)")
    ec2 = boto3.client("ec2", region_name=REGION)
    response = safe_call(ec2.describe_snapshots, OwnerIds=['self'])
    found = False

    if response:
        for snap in response.get("Snapshots", []):
            found = True
            print({
                "ResourceType": "Snapshot",
                "SnapshotId": snap.get("SnapshotId"),
                "VolumeSize": snap.get("VolumeSize"),
                "StartTime": str(snap.get("StartTime")),
                "Warning": "Old snapshots continue to cost storage."
            })
    if not found:
        print("No snapshots found.")

# ---------------------------
# AMIs
# ---------------------------
def check_amis():
    print_header("CUSTOM AMIs (OWNED BY YOU)")
    ec2 = boto3.client("ec2", region_name=REGION)
    response = safe_call(ec2.describe_images, Owners=['self'])
    found = False

    if response:
        for image in response.get("Images", []):
            found = True
            print({
                "ResourceType": "AMI",
                "ImageId": image.get("ImageId"),
                "Name": image.get("Name"),
                "CreationDate": image.get("CreationDate"),
                "Warning": "AMI snapshots/storage may cost money."
            })
    if not found:
        print("No custom AMIs found.")

def main():
    try:
        print(f"\nScanning leftover costly AWS resources in region: {REGION}\n")

        check_ec2_instances()
        check_unattached_ebs()
        check_unused_eips()
        check_load_balancers()
        check_nat_gateways()
        check_rds()
        check_eks()
        check_ecs()
        check_ecr()
        check_log_groups()
        check_snapshots()
        check_amis()

        print("\n" + "=" * 100)
        print("SCAN COMPLETE")
        print("=" * 100)
        print("Review above resources and delete what is no longer needed.")

    except (NoCredentialsError, PartialCredentialsError):
        print("AWS credentials not configured properly.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
