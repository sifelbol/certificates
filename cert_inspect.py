import logging
import sys
import datetime
import certstream
import requests
import os
 
SLACK = os.getenv('SLACK')

# print(f'slack directory is {SLACK}')

TARGET = "buda.com"
LAST_PRINTED_DOMAIN = ""

def phishing_candidate(target, domain, other_domains):
    if target in domain:
        return True

    for domain in other_domains:
        if target in domain:
            return True
    
    return False

def send_warning_to_slack(domains):
    # data to be sent to api
    domains_data = '{"text":"'+domains+'"}'
    print('domains_data: ' + domains_data)
    api_endpoint = SLACK
    # sending post request and saving response as response object
    r = requests.post(url = api_endpoint, data = domains_data)
    
    # extracting response text 
    pastebin_url = r.text
    print("The pastebin URL is:%s"%pastebin_url)


def print_callback(message, context):
    logging.debug("Message -> {}".format(message))

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        if len(all_domains) == 0:
            domain = "NULL"
        else:
            domain = all_domains[0]
        other_domains = message['data']['leaf_cert']['all_domains'][1:]

        if phishing_candidate(TARGET, domain, other_domains):
            global LAST_PRINTED_DOMAIN
            timestampt = u"[{}]".format(datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'))
            candidate_domains = u"{} (SAN: {})\n".format(domain, ", ".join(other_domains))
            if candidate_domains != LAST_PRINTED_DOMAIN:
                send_warning_to_slack("{} {}".format(timestampt, candidate_domains))
                LAST_PRINTED_DOMAIN = candidate_domains
                sys.stdout.write("{} {}".format(timestampt, candidate_domains))
                sys.stdout.flush()
            # else:
            #     print("REPETIDO: " + LAST_PRINTED_DOMAIN)
            
if SLACK:
    print('searching...')
    logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)
    certstream.listen_for_events(print_callback, url='wss://certstream.calidog.io/')
else:
    print('ENV VARS not found')