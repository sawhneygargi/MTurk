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

def datetime_now():
    from time import gmtime, strftime
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def record_sent(uniq_str, worker_id, assignment_id, response):
    try:
        f = open(uniq_str + '.csv', 'a')
        f.writelines("%s,%s,%s" % (worker_id, assignment_id, response))
        f.close()
    except Exception as e:
        print("Failed to log response for workerID %s assignmentID %s response %s to file %s: %s" % \
            (worker_id, assignment_id, response, uniq_str, str(e)))

def send_bonuses_to_workers(client, worker_list, amount, assignment_id_list, reason):
    if not client:
        print("FAILED: No client found. Connect to AWS first")
        return None
    if not worker_list or not len(worker_list):
        print("FAILED: No workers found in the list")
        return None
    if not assignment_id_list or not len(assignment_id_list):
        print("FAILED: No assignment ids found in the list")
        return None
    if len(worker_list) != len(assignment_id_list):
        print("FAILED: Number of workers is not the same as number of assignment IDs")
        return None
    res = list(zip(worker_list, assignment_id_list))
    rec_file=datetime_now()
    for item in res:
        try:
            worker_id, assignment_id = item
            uniq_str=datetime_now()
            print("Sending bonus of $%s to worker %s with assignment id %s" %
                    (amount, worker_id, assignment_id))
            response = client.send_bonus(WorkerId=worker_id,
                                 BonusAmount=amount,
                                 AssignmentId=assignment_id,
                                 Reason=reason,
                                 UniqueRequestToken=uniq_str)
            record_sent(rec_file, worker_id, assignment_id, response)
            time.sleep(1)
        except Exception as e:
            print("Failed to send bonus to worker " + worker_id + " : " + str(e))
            break

def send_bonuses(client, worker_list, assignment_id_list):

    # Amount
    print("Enter amount: ")
    amount = input()
    print("Amount you entered was %s" % (amount))
    print("Continue (Y/N)")
    cont = input()
    if cont == "n" or cont == "N":
        print("Exiting")
        exit(1)

    # Bonus reason
    print("Enter reason: ")
    reason = input()
    print("The reason you entered was %s" % (reason))
    print("Continue (Y/N)")
    cont = input()
    if cont == "n" or cont == "N":
        print("Exiting")
        exit(1)

    send_bonuses_to_workers(client, worker_list, amount, assignment_id_list, reason)

if __name__ == "__main__":

    # validate program
    if len(sys.argv) != 3:
        print("Usage: python3 %s <path-to-csv-file-containing-worker-ids-per-row> " \
            "<path-to-csv-file-containing-assignment-ids-per-row>" % (sys.argv[0]))
        exit(1)

    # read worker IDs from input file
    worker_list = read_worker_ids_from_file(sys.argv[1])
    if not worker_list:
        exit(1)

    # read worker IDs from input file
    assignment_id_list = read_worker_ids_from_file(sys.argv[2])
    if not assignment_id_list:
        exit(1)

    # connect to AWS
    client = connect_to_aws()
    if not client:
        exit(1)

    # send bonuses
    send_bonuses(client, worker_list, assignment_id_list)
