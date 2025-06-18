from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from datetime import datetime, timezone
from src.modules import Modules
from src.jsonParser import jsonParser
import datetime

def generate_x_signature(private_key, client_id):
    try:
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
        x_timestamp = now.strftime('%Y-%m-%dT%H:%M:%S+07:00')
        string_to_sign = f"{client_id}|{x_timestamp}"
        output = Modules.SHA256WithRSA(string_to_sign, private_key)
        return [string_to_sign, output]
    except (ValueError) as e:
                print(str(e))

def signature_service(client_secret, HTTPMethod, EndpointUrl, AccessToken, requestbody):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    x_timestamp = now.strftime('%Y-%m-%dT%H:%M:%S+07:00')
    minifyreqbody = jsonParser.jsonParserMinify(requestbody)
    hashed = Modules.HashSHA256(minifyreqbody)
    string_to_sign = f"{HTTPMethod}:{EndpointUrl}:{AccessToken}:{hashed}:{x_timestamp}"
    output = Modules.HashSHA512(string_to_sign, client_secret)
    return [string_to_sign, output]
