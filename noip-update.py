#! /bin/python3

import base64
import logging
import logging.handlers
import socket
import sys
import urllib.request

PUBLIC_IP_API_ENDPOINT = 'https://api.ipify.org'

# NO-IP
NOIP_USERNAME = ''
NOIP_PASSWORD = ''
NOIP_REQUEST_URL_TEMPLATE = 'http://dynupdate.no-ip.com/nic/update?hostname={domain_name}&myip={ip}'
NOIP_SERVER_DOMAIN_NAME = ''

# Mailjet
MAILJET_API_URL = 'https://api.mailjet.com/v3.1/send'
MAILJET_API_KEY = ''
MAILJET_SECRET_KEY = ''
MAILJET_FROM_EMAIL = ''
MAILJET_TO_EMAIL = ''

# Send mail
def send_mail(content):
    payload = """
    {
        "Messages":[{
            "From":{
                "Email":"{from_email}",
                "Name":"NoIP-Update Script"
            },
            "To":[{
                "Email":"{to_email}"
                }],
            "Subject":"NoIP-Update Notification",
            "TextPart":"{content}"
        }]
    }""".format(content=content, from_mail=MAILJET_FROM_EMAIL, to_email=MAILJET_TO_EMAIL)

    request = urllib.request.Request(MAILJET_API_URL, data=payload.encode())
    request.add_header('Content-Type', 'application/json')
    request.add_header("Authorization", "Basic %s" % base64_encode_username_password(MAILJET_API_KEY, MAILJET_SECRET_KEY))
    response = urllib.request.urlopen(request).read().decode('utf8')
    return response

# Get IP of server domain
def resolve_ip_of_domain(domain_name):
    return socket.gethostbyname(domain_name)

# Get public IP of current host
def get_public_ip_of_host():
    return urllib.request.urlopen(PUBLIC_IP_API_ENDPOINT).read().decode()

# Update NOIP server
def update_noip(username, password, domain_name, ip):
    url = NOIP_REQUEST_URL_TEMPLATE.format(domain_name=domain_name, ip=ip)
    request = urllib.request.Request(url)
    base64string = base64_encode_username_password(username, password)
    request.add_header("Authorization", "Basic %s" % base64string)  
    response = urllib.request.urlopen(request).read().decode()
    return response

# Encode username and password with base64 encoding
def base64_encode_username_password(username, password):
    username_password_in_byte = ('%s:%s' % (username, password)).encode()
    base64string = base64.b64encode(username_password_in_byte).decode()
    return base64string

def logger_setup(logger_file_path):
    """
    Setup logger
    :param logger_file_path: logger file path
    :return: logger
    """
    log_formatter = logging.Formatter('%(asctime)s  %(message)s')
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(logger_file_path, maxBytes=1000, backupCount=2)
    handler.setFormatter(log_formatter)
    logger.addHandler(handler)
    return logger

def main():
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or a more recent version is required.")

    if len(sys.argv) < 2:
        print("Usage: noip-update.py LOG_FILE_PATH")
        exit(1)

    logger = logger_setup(sys.argv[1])
    logger.info("==========================================")
    logger.info("========== Start of script ==========")

    domain_ip = resolve_ip_of_domain(NOIP_SERVER_DOMAIN_NAME)
    logger.info("Domain's IP is: " + domain_ip)
    public_ip = get_public_ip_of_host()
    logger.info("Host's public IP is: " + public_ip)

    if domain_ip == public_ip:
        logger.info('No change in IP detected. Exiting now...')
    else:
        logger.info('Detected IP change. Updating NOIP querey now...')
        response = update_noip(NOIP_USERNAME, NOIP_PASSWORD, NOIP_SERVER_DOMAIN_NAME, public_ip)
        send_mail(response)

    logger.info("========== End of script ==========")
    logger.info("==========================================\n")


if __name__ == '__main__':
    main()
