import boto3

REGION = "ap-south-1"
DRY_RUN = False   # change to False to actually delete

glue = boto3.client("glue", region_name=REGION)


def log(msg):
    print(f"[INFO] {msg}")


# -----------------------------
# 1) Glue Jobs
# -----------------------------
def cleanup_jobs():
    log("Checking Glue Jobs...")
    jobs = glue.get_jobs().get("Jobs", [])

    for job in jobs:
        name = job["Name"]
        print(f"Job: {name}")

        if DRY_RUN:
            print(f"  -> Would DELETE job: {name}")
        else:
            glue.delete_job(JobName=name)


# -----------------------------
# 2) Crawlers
# -----------------------------
def cleanup_crawlers():
    log("Checking Crawlers...")
    crawlers = glue.get_crawlers().get("Crawlers", [])

    for crawler in crawlers:
        name = crawler["Name"]
        state = crawler["State"]

        print(f"Crawler: {name} | State: {state}")

        if state == "RUNNING":
            if DRY_RUN:
                print(f"  -> Would STOP crawler: {name}")
            else:
                glue.stop_crawler(Name=name)

        if DRY_RUN:
            print(f"  -> Would DELETE crawler: {name}")
        else:
            glue.delete_crawler(Name=name)


# -----------------------------
# 3) Databases + Tables
# -----------------------------
def cleanup_databases():
    log("Checking Databases...")
    dbs = glue.get_databases().get("DatabaseList", [])

    for db in dbs:
        name = db["Name"]

        if name == "default":
            continue  # skip default DB

        print(f"Database: {name}")

        tables = glue.get_tables(DatabaseName=name).get("TableList", [])

        for table in tables:
            tname = table["Name"]
            print(f"  Table: {tname}")

            if DRY_RUN:
                print(f"    -> Would DELETE table: {tname}")
            else:
                glue.delete_table(DatabaseName=name, Name=tname)

        if DRY_RUN:
            print(f"  -> Would DELETE database: {name}")
        else:
            glue.delete_database(Name=name)


# -----------------------------
# 4) Workflows
# -----------------------------
def cleanup_workflows():
    log("Checking Workflows...")
    workflows = glue.list_workflows().get("Workflows", [])

    for wf in workflows:
        print(f"Workflow: {wf}")

        if DRY_RUN:
            print(f"  -> Would DELETE workflow: {wf}")
        else:
            glue.delete_workflow(Name=wf)


# -----------------------------
# 5) Triggers
# -----------------------------
def cleanup_triggers():
    log("Checking Triggers...")
    triggers = glue.get_triggers().get("Triggers", [])

    for trg in triggers:
        name = trg["Name"]
        print(f"Trigger: {name}")

        if DRY_RUN:
            print(f"  -> Would DELETE trigger: {name}")
        else:
            glue.delete_trigger(Name=name)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    cleanup_jobs()
    print("-" * 50)

    cleanup_crawlers()
    print("-" * 50)

    cleanup_databases()
    print("-" * 50)

    cleanup_workflows()
    print("-" * 50)

    cleanup_triggers()
    print("-" * 50)

    log("Glue cleanup scan completed.")
    if DRY_RUN:
        log("DRY_RUN=True → nothing deleted.")
