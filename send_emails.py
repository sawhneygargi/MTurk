try:
    import boto3
except Exception as e:
    print("boto3 not installed. Please install using 'pip3 install boto3' command line on terminal")
    exit(1)

import csv
import sys
import time

print("Enter access ID: ")
ACCESS_ID = input()

print("Secret key: ")
SECRET_KEY = input()

print("Enter email subject: ")
SUBJECT = input()

print("Enter email message: ")
MESSAGE = input()

def read_worker_ids_from_file(filepath):
    try:
        worker_list = []
        with open(filepath, 'r') as f:
            for line in f.readlines():
                worker_id = line.strip()
                worker_list.append(worker_id)
        return worker_list
    except Exception as e:
        print("Failed to read worker IDs from file " + filepath + ":" + str(e))
        return None

def connect_to_aws():
    global ACCESS_ID
    global SECRET_KEY
    try:
        client = boto3.client('mturk',
            region_name='us-east-1',
            aws_access_key_id=ACCESS_ID,
            aws_secret_access_key=SECRET_KEY
        )
        return client
    except Exception as e:
        print("Failed to connect to AWS: " + str(e))
        return None

def send_email_to_workers(client, worker_list):
    if not client:
        print("FAILED: No client found. Connect to AWS first")
        return None
    if not worker_list or not len(worker_list):
        print("FAILED: No workers found in the list")
        return None
    try:
        response = client.notify_workers(
            Subject=SUBJECT,
            MessageText=MESSAGE,
            WorkerIds=worker_list
        )
        return len(worker_list)
    except Exception as e:
        print("Failed to send emails: " + str(e))
        return 0

def send_emails(client, worker_list):
    # now send emails
    num_emails_sent = send_email_to_workers(client, worker_list)
    if num_emails_sent:
        print("Successfully sent " + str(num_emails_sent) + " emails")
    else:
        print("FAILED: no emails were sent")

if __name__ == "__main__":

    # validate program
    if len(sys.argv) != 2:
        print("Usage: python3 %s <path-to-csv-file-containing-worker-ids-per-row>" % (sys.argv[0]))
        exit(1)

    # read worker IDs from input file
    worker_list = read_worker_ids_from_file(sys.argv[1])
    if not worker_list:
        exit(1)

    # connect to AWS
    client = connect_to_aws()
    if not client:
        exit(1)

    # send emails
    send_emails(client, worker_list)
