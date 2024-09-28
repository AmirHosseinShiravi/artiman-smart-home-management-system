import base64
import json
import os
import secrets
import string
import urllib.request
from typing import Any
import requests
from dotenv import load_dotenv
import dashboard.models as dashboard_models

from .mqtt_manager import initialize_mqtt, subscribe_to_topic, publish_message, unsubscribe_from_topic


load_dotenv()  # take environment variables from .env.

def initialize_mqtt_connection():
    initialize_mqtt()

def generate_random_id(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    username = ''.join(secrets.choice(characters) for _ in range(length))
    return username


def generate_random_username(length=8):
    characters = string.ascii_letters + string.digits
    username = ''.join(secrets.choice(characters) for _ in range(length))
    return username


def generate_random_password(length=12):
    if length < 4:
        raise ValueError("Password length should be at least 4 characters to ensure complexity")

    characters = string.ascii_letters + string.digits #+ string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password





def get_mqtt_cluster_statistics():
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    mqtt_broker_status_url = base_url + f"/api/v5/stats?aggregate=true"

    auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
    header = {'Content-Type': 'application/json',
                'Authorization': auth_header
                }
    try:
        response = requests.get(mqtt_broker_status_url, headers=header, timeout=10)
        if response.status_code == 200:
            print("successfully get mqtt broker statistics.")
            data = json.loads(response.content.decode())
            return data
        else:
            print("get error while getting mqtt broker statistics. error:: " + response.content.decode())
            return False
    except Exception as e:
        print("get error while getting mqtt broker statistics. error:: " + response.content.decode())
        print(e)
        return {}

    
def get_mqtt_cluster_status():
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    mqtt_broker_status_url = base_url + f"/api/v5/status?format=json"

    auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
    header = {'Content-Type': 'application/json',
                'Authorization': auth_header
                }
    try:
        response = requests.get(mqtt_broker_status_url, headers=header, timeout=10)
        if response.status_code == 200:
            print("successfully get mqtt broker status.")
            data = json.loads(response.content.decode())
            return data
        else:
            print("get error while getting mqtt broker status. error:: " + response.content.decode())
            return False
    except Exception as e:
        print("get error while getting mqtt broker status. error:: " + response.content.decode())
        print(e)
        return {}

    




import os
import tempfile
import subprocess

def generate_controller_credentials(controller_id, key_length=2048, cert_lifespan=365):
    # Generate a unique key and certificate for the controller, using the common CA
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate controller private key
        controller_key_path = os.path.join(temp_dir, "controller.key")
        subprocess.run(["openssl", "genrsa", "-out", controller_key_path, str(key_length)], check=True)

        # Generate controller certificate signing request (CSR)
        controller_csr_path = os.path.join(temp_dir, "controller.csr")
        subprocess.run([
            "openssl", "req", "-new",
            "-key", controller_key_path,
            "-out", controller_csr_path,
            "-subj", f"/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=controller-{controller_id}"
        ], check=True)

        # Sign the controller CSR with the common CA (assuming CA files are stored securely)
        ca_key_path = "/path/to/common/ca.key"  # Update this path
        ca_cert_path = "/path/to/common/ca.crt"  # Update this path
        controller_cert_path = os.path.join(temp_dir, "controller.crt")
        subprocess.run([
            "openssl", "x509", "-req",
            "-in", controller_csr_path,
            "-CA", ca_cert_path,
            "-CAkey", ca_key_path,
            "-CAcreateserial",
            "-out", controller_cert_path,
            "-days", str(cert_lifespan),
            "-sha256"
        ], check=True)

        # Convert key and cert to PEM format
        controller_key_pem_path = os.path.join(temp_dir, "controller_key.pem")
        controller_cert_pem_path = os.path.join(temp_dir, "controller_cert.pem")

        subprocess.run([
            "openssl", "rsa",
            "-in", controller_key_path,
            "-out", controller_key_pem_path,
            "-outform", "PEM"
        ], check=True)

        subprocess.run([
            "openssl", "x509",
            "-in", controller_cert_path,
            "-out", controller_cert_pem_path,
            "-outform", "PEM"
        ], check=True)

        # Read the generated PEM files
        with open(controller_key_pem_path, 'r') as f:
            controller_key_pem = f.read()
        with open(controller_cert_pem_path, 'r') as f:
            controller_cert_pem = f.read()

    return {
        'controller_key': controller_key_pem,
        'controller_cert': controller_cert_pem
    }

# Example usage:
# credentials = generate_controller_credentials(
#     controller_id="unique-controller-id-001",
#     key_length=4096,
#     cert_lifespan=730
# )



# write a function to subscribe to controllers status topic
def subscribe_to_controllers_status_topic(controller_uuid: str):
    subscribe_to_topic(f"v1/controllers/{controller_uuid}/status", handle_controller_status_message)
    print(f"subscribed to Controller status topic: v1/controllers/{controller_uuid}/status")

# unsubscribe from controllers status topic
def unsubscribe_from_controllers_status_topic(controller_uuid: str):
    unsubscribe_from_topic(f"v1/controllers/{controller_uuid}/status", handle_controller_status_message)
    print(f"unsubscribed from Controller status topic: v1/controllers/{controller_uuid}/status")

# write handler call back function to handle the message. it based on topic message, write to controller model status field
def handle_controller_status_message(topic: str, payload: Any):
    print(f"Received message on {topic}: {payload}")
    controller_uuid = topic.split("/")[-2]
    if controller_uuid:
        # check if controller is exist
        if dashboard_models.Controller.objects.filter(uuid=controller_uuid).exists():
            controller = dashboard_models.Controller.objects.get(uuid=controller_uuid)
            # check payload is online or offline
            if payload == dashboard_models.Controller.ControllerStatusChoices.ENABLE:
                controller.status = dashboard_models.Controller.ControllerStatusChoices.ENABLE
                controller.save()
            elif payload == dashboard_models.Controller.ControllerStatusChoices.DISABLE:
                controller.status = dashboard_models.Controller.ControllerStatusChoices.DISABLE
                controller.save()
            elif payload == dashboard_models.Controller.ControllerStatusChoices.ERROR:
                controller.status = dashboard_models.Controller.ControllerStatusChoices.ERROR
                controller.save()
        else:
            print(f"Controller with uuid {controller_uuid} does not exist")
    else:
        print("Controller uuid is None")





def add_user_to_emqx_password_based_built_in_database_authentication_backend(mqtt_username=None, mqtt_password=None):
    base_url = os.environ.get('emqx_base_url')
    url = base_url + '/api/v5/authentication/password_based:built_in_database/users'

    # load_dotenv()  # take environment variables from .env.
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    req = urllib.request.Request(url, data=json.dumps({"password": str(mqtt_password), "user_id": str(mqtt_username)}).encode('utf-8'), method='POST')
    req.add_header('Content-Type', 'application/json')

    auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
    req.add_header('Authorization', auth_header)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        print(data)
        return True

    except Exception as e:
        print(e)
        return False


def delete_user_from_emqx_password_based_built_in_database_authentication_backend(mqtt_username=None):

    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    delete_user_url = base_url + f"/api/v5/authentication/password_based:built_in_database/users/{mqtt_username}"

    auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
    header = {'Content-Type': 'application/json',
              'Authorization': auth_header
              }
    try:
        response = requests.delete(delete_user_url, headers=header)
        if response.status_code == 204:
            print(f"successfully delete user from password_based:built_in_database authentication engine.\n mqtt username:: {mqtt_username}\n")
            return True
        else:
            print("get error while deleting user from password_based:built_in_database authentication engine. error:: " + response.content.decode())
    except Exception as e:
        print(f"mqtt user deletion was unsuccessfully. Reason:: {e}")


def set_controller_client_rule_to_emqx_built_in_database_authorization_backend(project_uuid=None, home_uuid=None, controller_uuid=None):
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')
    url = base_url + '/api/v5/authorization/sources/built_in_database/rules/clients'

    controller = dashboard_models.Controller.objects.filter(parent_project__uuid=project_uuid,
                                                            parent_home__uuid=home_uuid,
                                                            uuid=controller_uuid).get()
    if controller:
        controller_mqtt_client_id = controller.mqtt_client_id

        get_client_rule_url = base_url + f'/api/v5/authorization/sources/built_in_database/rules/clients/{controller_mqtt_client_id}'
        auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.get(get_client_rule_url, headers=header)
            if response.status_code == 200:
                print('controller client authorization rules were exist. start update procedure.')
                put_client_rule_url = base_url + f'/api/v5/authorization/sources/built_in_database/rules/clients/{controller_mqtt_client_id}'

                controller_uuid = controller.uuid
                controller_device_ids = controller.controller_devices.values_list('id', flat=True)
                all_related_datapoint_functions = dashboard_models.DataPointFunction.objects.filter(device_base__id__in=controller_device_ids).all()

                client_rules_message = {
                                            "rules": list(),
                                            "clientid": str(controller_mqtt_client_id)
                                       }

                # add controller specific topic to list except controllers device
                for data_point in all_related_datapoint_functions:
                    device_uuid = data_point.device_base.uuid
                    data_point_function_name = data_point.function_name
                    client_rules_message["rules"].append({
                                                            "action": "subscribe",
                                                            "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/set",
                                                            "permission": "allow",
                                                            "retain": "false"
                                                        })
                    client_rules_message["rules"].append({
                                                            "action": "publish",
                                                            "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get",
                                                            "permission": "allow",
                                                            "retain": "all"
                                                        })

                # will message
                client_rules_message["rules"].append({
                                                            "action": "all",
                                                            "topic": f"v1/controllers/{controller_uuid}/status",
                                                            "permission": "allow",
                                                    })

                # because we have list and with list append method, each new item added to the end of list, we can just add
                # this rule to the end of rules list and sure this rule is last rule was checked by emqx authorizer, so
                # all rules that set to allow were permitted and any unwanted topic was not permitted.
                client_rules_message["rules"].append({
                                                            "action": "all",
                                                            "topic": "#",
                                                            "permission": "deny",
                                                    })

                print(client_rules_message)

                req = urllib.request.Request(put_client_rule_url, data=json.dumps(client_rules_message).encode('utf-8'), method='PUT')
                req.add_header('Content-Type', 'application/json')

                auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
                req.add_header('Authorization', auth_header)
                try:
                    with urllib.request.urlopen(req) as put_response:
                        print(put_response.status)
                        if put_response.status == 204:
                            data = 'successfully update controller client authorization rules.'
                            subscribe_to_controllers_status_topic(controller_uuid)
                        else:
                            data = json.loads(put_response.read().decode())
                    print(data)
                    return True

                except Exception as e:
                    print(e)
                    return False
            elif response.status_code == 404:
                print('controller client authorization rules were not exist. start create new rules procedure.')
                post_client_rule_url = base_url + '/api/v5/authorization/sources/built_in_database/rules/clients'
                controller_uuid = controller.uuid
                controller_device_ids = controller.controller_devices.values_list('id', flat=True)
                all_related_datapoint_functions = dashboard_models.DataPointFunction.objects.filter(
                    device_base__id__in=controller_device_ids).all()

                client_rules_message = [{
                                            "rules": list(),
                                            "clientid": str(controller_mqtt_client_id)
                                        }]

                # add controller specific topic to list except controllers device
                for data_point in all_related_datapoint_functions:
                    device_uuid = data_point.device_base.uuid
                    data_point_function_name = data_point.function_name
                    client_rules_message[0]["rules"].append({
                        "action": "subscribe",
                        "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/set",
                        "permission": "allow",
                        "retain": "false"
                    })
                    client_rules_message[0]["rules"].append({
                        "action": "publish",
                        "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get",
                        "permission": "allow",
                        "retain": "all"
                    })

                # will message
                client_rules_message[0]["rules"].append({
                    "action": "all",
                    "topic": f"v1/controllers/{controller_uuid}/status",
                    "permission": "allow",
                })

                # because we have list and with list append method, each new item added to the end of list, we can just add
                # this rule to the end of rules list and sure this rule is last rule was checked by emqx authorizer, so
                # all rules that set to allow were permitted and any unwanted topic was not permitted.
                client_rules_message[0]["rules"].append({
                    "action": "all",
                    "topic": "#",
                    "permission": "deny",
                })

                print(client_rules_message)

                req = urllib.request.Request(post_client_rule_url, data=json.dumps(client_rules_message).encode('utf-8'),
                                             method='POST')
                req.add_header('Content-Type', 'application/json')

                auth_header = "Basic " + base64.b64encode(
                    (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
                req.add_header('Authorization', auth_header)
                try:
                    with urllib.request.urlopen(req) as post_response:
                        print(post_response.status)
                        if post_response.status == 204:
                            data = 'successfully create controller client authorization rules.'
                            subscribe_to_controllers_status_topic(controller_uuid)
                        else:
                            data = json.loads(post_response.read().decode())
                    print(data)
                    return True

                except Exception as e:
                    print(e)
                    return False

        except Exception as e:
            print(e)

    else:
        return False


def delete_all_controller_client_authorization_rules(controller_uuid=None):
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    controller = dashboard_models.Controller.objects.filter(uuid=controller_uuid).get()
    if controller:
        controller_mqtt_client_id = controller.mqtt_client_id
        delete_client_rules_url = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{controller_mqtt_client_id}"

        auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.delete(delete_client_rules_url, headers=header)
            if response.status_code == 204:
                print(f"successfully delete controller client authorization rules.\n controller client ID:: {controller_mqtt_client_id}\n controller UUID:: {controller_uuid}")
                unsubscribe_from_controllers_status_topic(controller_uuid)
                return True
            else:
                print("get error while deleting client authorization rules. error:: " + response.content.decode() )
        except:
            print("controller mqtt client authorization rules deletion was unsuccessfully. Reason:: controller UUID not found.")


def set_web_app_client_rule_to_emqx_built_in_database_authorization_backend(home_user_uuid=None):
    # add permission to subscribe controllers will topics
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    home_user = dashboard_models.HomeUser.objects.get(uuid=home_user_uuid)

    if home_user:
        home_user_mqtt_client_id = home_user.mqtt_client_id
        get_client_rule_url = base_url + f'/api/v5/authorization/sources/built_in_database/rules/clients/{home_user_mqtt_client_id}'

        auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.get(get_client_rule_url, headers=header)
            if response.status_code == 200:
                print('web app client authorization rules were exist. start update procedure.')
                put_client_rule_url = base_url + f'/api/v5/authorization/sources/built_in_database/rules/clients/{home_user_mqtt_client_id}'
                controllers = dashboard_models.Controller.objects.filter(
                    parent_project__uuid=home_user.parent_project.uuid,
                    parent_home__uuid=home_user.parent_home.uuid).all()

                if controllers:
                    client_rules_message = {
                        "rules": list(),
                        "clientid": str(home_user_mqtt_client_id)
                    }

                    for controller in controllers:
                        controller_uuid = controller.uuid
                        controller_device_ids = controller.controller_devices.values_list('id', flat=True)
                        all_related_datapoint_functions = dashboard_models.DataPointFunction.objects.filter(
                            device_base__id__in=controller_device_ids).all()

                        # add controller specific topic to list except controllers device
                        for data_point in all_related_datapoint_functions:
                            device_uuid = data_point.device_base.uuid
                            data_point_function_name = data_point.function_name
                            client_rules_message["rules"].append({
                                "action": "publish",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/set",
                                "permission": "allow",
                                "retain": "false"
                            })
                            client_rules_message["rules"].append({
                                "action": "subscribe",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get",
                                "permission": "allow",
                                "retain": "all"
                            })

                        # controller will message
                        client_rules_message["rules"].append({
                            "action": "subscribe",
                            "topic": f"v1/controllers/{controller_uuid}/status",
                            "permission": "allow",
                        })

                    # client will message
                    client_rules_message["rules"].append({
                        "action": "all",
                        "topic": f"v1/users/home_users/{home_user_mqtt_client_id}/status",
                        "permission": "allow",
                    })

                    client_rules_message["rules"].append({
                        "action": "all",
                        "topic": f"v1/projects/{home_user.parent_project.uuid}/homes/{home_user.parent_home.uuid}/linkage-rules/+/actions/create-new-rule-event",
                        "permission": "allow",
                    })
                    # because we have list and with list append method, each new item added to the end of list,
                    # we can just add this rule to the end of rules list and sure this rule is last rule was
                    # checked by emqx authorizer, so all rules that set to allow were permitted and any unwanted
                    # topic was not permitted.
                    client_rules_message["rules"].append({
                        "action": "all",
                        "topic": "#",
                        "permission": "deny",
                    })

                    print(client_rules_message)

                    req = urllib.request.Request(put_client_rule_url,
                                                 data=json.dumps(client_rules_message).encode('utf-8'),
                                                 method='PUT')
                    req.add_header('Content-Type', 'application/json')

                    auth_header = "Basic " + base64.b64encode(
                        (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
                    req.add_header('Authorization', auth_header)
                    try:
                        with urllib.request.urlopen(req) as put_response:
                            print(put_response.status)
                            if put_response.status == 204:
                                data = 'successfully update web app client authorization rules.'
                            else:
                                data = json.loads(put_response.read().decode())
                        print(data)
                        return True

                    except Exception as e:
                        print(e)
                        return False

                else:
                    pass

            elif response.status_code == 404:
                print('web app client authorization rules were not exist. start create new rules procedure.')
                post_client_rule_url = base_url + '/api/v5/authorization/sources/built_in_database/rules/clients'
                controllers = dashboard_models.Controller.objects.filter(
                    parent_project__uuid=home_user.parent_project.uuid,
                    parent_home__uuid=home_user.parent_home.uuid).all()

                if controllers:

                    client_rules_message = [
                        {
                            "rules": list(),
                            "clientid": str(home_user_mqtt_client_id)
                        }
                    ]
                    for controller in controllers:
                        controller_uuid = controller.uuid
                        controller_device_ids = controller.controller_devices.values_list('id', flat=True)
                        all_related_datapoint_functions = dashboard_models.DataPointFunction.objects.filter(
                            device_base__id__in=controller_device_ids).all()

                        # add controller specific topic to list except controllers device
                        for data_point in all_related_datapoint_functions:
                            device_uuid = data_point.device_base.uuid
                            data_point_function_name = data_point.function_name
                            client_rules_message[0]["rules"].append({
                                "action": "all",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/set",
                                "permission": "allow",
                                "retain": "false"
                            })
                            client_rules_message[0]["rules"].append({
                                "action": "all",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get",
                                "permission": "allow",
                                "retain": "all"
                            })

                        # will message
                        client_rules_message[0]["rules"].append({
                            "action": "all",
                            "topic": f"v1/controllers/{controller_uuid}/status",
                            "permission": "allow",
                        })

                    # will message
                    client_rules_message[0]["rules"].append({
                        "action": "all",
                        "topic": f"v1/users/home_users/{home_user_mqtt_client_id}/status",
                        "permission": "allow",
                    })

                    client_rules_message[0]["rules"].append({
                        "action": "all",
                        "topic": f"v1/projects/{home_user.parent_project.uuid}/homes/{home_user.parent_home.uuid}/linkage-rules/+/actions/create-new-rule-event",
                        "permission": "allow",
                    })

                    # because we have list and with list append method, each new item added to the end of list,
                    # we can just add this rule to the end of rules list and sure this rule is last rule was
                    # checked by emqx authorizer, so all rules that set to allow were permitted and any unwanted
                    # topic was not permitted.
                    client_rules_message[0]["rules"].append({
                        "action": "all",
                        "topic": "#",
                        "permission": "deny",
                    })

                    print(client_rules_message)

                    req = urllib.request.Request(post_client_rule_url,
                                                 data=json.dumps(client_rules_message).encode('utf-8'),
                                                 method='POST')

                    req.add_header('Content-Type', 'application/json')

                    auth_header = "Basic " + base64.b64encode(
                        (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
                    req.add_header('Authorization', auth_header)
                    try:
                        with urllib.request.urlopen(req) as post_response:
                            if post_response.status == 204:
                                data = 'successfully create web app client authorization rules.'
                            else:
                                data = json.loads(post_response.read().decode())
                        print(data)
                        return True

                    except Exception as e:
                        print(e)
                        return False

                else:
                    pass

            return True

        except Exception as e:
            print(e)
            return False


def delete_web_app_client_authorization_rules(home_user_uuid=None):
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    home_user = dashboard_models.HomeUser.objects.get(uuid=home_user_uuid)

    if home_user:
        home_user_mqtt_client_id = home_user.mqtt_client_id
        get_client_rules_url = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user_mqtt_client_id}"

        auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.get(get_client_rules_url, headers=header)
            if response.status_code == 200:
                current_rules = response.json()['rules']
                
                # Filter out rules added by set_web_app_client_rule_to_emqx_built_in_database_authorization_backend
                updated_rules = [rule for rule in current_rules if not (
                    rule['topic'].startswith('v1/controllers/') or
                    rule['topic'].startswith(f'v1/users/home_users/{home_user_mqtt_client_id}/status') or
                    rule['topic'] == '#'
                )]

                # Update rules
                put_client_rules_url = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user_mqtt_client_id}"
                update_payload = {"rules": updated_rules, "clientid": home_user_mqtt_client_id}
                update_response = requests.put(put_client_rules_url, json=update_payload, headers=header)

                if update_response.status_code == 204:
                    print("Successfully deleted web app client authorization rules.")
                    return True
                else:
                    print("Error while updating web app client authorization rules. Error:", update_response.content.decode())
                    return False
            else:
                print("Error while getting web app client authorization rules. Error:", response.content.decode())
                return False
        except Exception as e:
            print("Home user web app, mqtt client authorization rules deletion was unsuccessful. Reason:", str(e))
            return False
    else:
        print("Home user not found.")
        return False


def completely_delete_all_web_app_client_authorization_rules(home_user_uuid=None):
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    home_user = dashboard_models.HomeUser.objects.get(uuid=home_user_uuid)

    if home_user:
        home_user_mqtt_client_id = home_user.mqtt_client_id
        delete_client_rules_url = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user_mqtt_client_id}"

        auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.delete(delete_client_rules_url, headers=header)
            if response.status_code == 204:
                print("successfully delete web app client authorization rules.")
                return True
            else:
                print("get error while deleting web app client authorization rules. error:: " + response.content.decode())
                return False
        except Exception as e:
            print("home user web app, mqtt client authorization rules deletion was unsuccessfully. Reason:: home user not found.")
            print(e)
            return False
    else:
        print("Home user not found.")
        return False
    

def set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend(tablet_user_uuid=None):
    # add permission to subscribe controllers will topics
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    tablet_user = dashboard_models.HomeUser.objects.get(uuid=tablet_user_uuid)

    if tablet_user:
        tablet_user_mqtt_client_id = tablet_user.mqtt_client_id
        get_client_rule_url = base_url + f'/api/v5/authorization/sources/built_in_database/rules/clients/{tablet_user_mqtt_client_id}'

        auth_header = "Basic " + base64.b64encode(
            (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.get(get_client_rule_url, headers=header)
            if response.status_code == 200:
                print('tablet client authorization rules were exist. start update procedure.')
                put_client_rule_url = base_url + f'/api/v5/authorization/sources/built_in_database/rules/clients/{tablet_user_mqtt_client_id}'
                controllers = dashboard_models.Controller.objects.filter(
                    parent_project__uuid=tablet_user.parent_project.uuid,
                    parent_home__uuid=tablet_user.parent_home.uuid).all()

                if controllers:
                    client_rules_message = {
                        "rules": list(),
                        "clientid": str(tablet_user_mqtt_client_id)
                    }

                    for controller in controllers:
                        controller_uuid = controller.uuid
                        controller_device_ids = controller.controller_devices.values_list('id', flat=True)
                        all_related_datapoint_functions = dashboard_models.DataPointFunction.objects.filter(
                            device_base__id__in=controller_device_ids).all()

                        # add controller specific topic to list except controllers device
                        for data_point in all_related_datapoint_functions:
                            device_uuid = data_point.device_base.uuid
                            data_point_function_name = data_point.function_name
                            client_rules_message["rules"].append({
                                "action": "publish",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/set",
                                "permission": "allow",
                                "retain": "false"
                            })
                            client_rules_message["rules"].append({
                                "action": "subscribe",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get",
                                "permission": "allow",
                                "retain": "all"
                            })

                        # will message
                        client_rules_message["rules"].append({
                            "action": "subscribe",
                            "topic": f"v1/controllers/{controller_uuid}/status",
                            "permission": "allow",
                        })

                    # will message
                    client_rules_message["rules"].append({
                        "action": "all",
                        "topic": f"v1/users/tablet_user/{tablet_user_mqtt_client_id}/status",
                        "permission": "allow",
                    })

                    client_rules_message["rules"].append({
                        "action": "all",
                        "topic": f"v1/projects/{tablet_user.parent_project.uuid}/homes/{tablet_user.parent_home.uuid}/linkage-rules/+/actions/create-new-rule-event",
                        "permission": "allow",
                    })

                    # because we have list and with list append method, each new item added to the end of list,
                    # we can just add this rule to the end of rules list and sure this rule is last rule was
                    # checked by emqx authorizer, so all rules that set to allow were permitted and any unwanted
                    # topic was not permitted.
                    client_rules_message["rules"].append({
                        "action": "all",
                        "topic": "#",
                        "permission": "deny",
                    })

                    print(client_rules_message)

                    req = urllib.request.Request(put_client_rule_url,
                                                 data=json.dumps(client_rules_message).encode('utf-8'),
                                                 method='PUT')
                    req.add_header('Content-Type', 'application/json')

                    auth_header = "Basic " + base64.b64encode(
                        (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
                    req.add_header('Authorization', auth_header)
                    try:
                        with urllib.request.urlopen(req) as put_response:
                            print(put_response.status)
                            if put_response.status == 204:
                                data = 'successfully update tablet client authorization rules.'
                            else:
                                data = json.loads(put_response.read().decode())
                        print(data)
                        return True

                    except Exception as e:
                        print(e)
                        return False

                else:
                    pass

            elif response.status_code == 404:
                print('tablet client authorization rules were not exist. start create new rules procedure.')
                post_client_rule_url = base_url + '/api/v5/authorization/sources/built_in_database/rules/clients'
                controllers = dashboard_models.Controller.objects.filter(
                    parent_project__uuid=tablet_user.parent_project.uuid,
                    parent_home__uuid=tablet_user.parent_home.uuid).all()

                if controllers:

                    client_rules_message = [
                        {
                            "rules": list(),
                            "clientid": str(tablet_user_mqtt_client_id)
                        }
                    ]
                    for controller in controllers:
                        controller_uuid = controller.uuid
                        controller_device_ids = controller.controller_devices.values_list('id', flat=True)
                        all_related_datapoint_functions = dashboard_models.DataPointFunction.objects.filter(
                            device_base__id__in=controller_device_ids).all()

                        # add controller specific topic to list except controllers device
                        for data_point in all_related_datapoint_functions:
                            device_uuid = data_point.device_base.uuid
                            data_point_function_name = data_point.function_name
                            client_rules_message[0]["rules"].append({
                                "action": "all",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/set",
                                "permission": "allow",
                                "retain": "false"
                            })
                            client_rules_message[0]["rules"].append({
                                "action": "all",
                                "topic": f"v1/controllers/{controller_uuid}/devices/{device_uuid}/functions/{data_point_function_name}/get",
                                "permission": "allow",
                                "retain": "all"
                            })

                        # will message
                        client_rules_message[0]["rules"].append({
                            "action": "all",
                            "topic": f"v1/controllers/{controller_uuid}/status",
                            "permission": "allow",
                        })

                    # will message
                    client_rules_message[0]["rules"].append({
                        "action": "all",
                        "topic": f"v1/users/tablet_user/{tablet_user_mqtt_client_id}/status",
                        "permission": "allow",
                    })

                    client_rules_message[0]["rules"].append({
                        "action": "all",
                        "topic": f"v1/projects/{tablet_user.parent_project.uuid}/homes/{tablet_user.parent_home.uuid}/linkage-rules/+/actions/create-new-rule-event",
                        "permission": "allow",
                    })
                    # because we have list and with list append method, each new item added to the end of list,
                    # we can just add this rule to the end of rules list and sure this rule is last rule was
                    # checked by emqx authorizer, so all rules that set to allow were permitted and any unwanted
                    # topic was not permitted.
                    client_rules_message[0]["rules"].append({
                        "action": "all",
                        "topic": "#",
                        "permission": "deny",
                    })

                    print(client_rules_message)

                    req = urllib.request.Request(post_client_rule_url,
                                                 data=json.dumps(client_rules_message).encode('utf-8'),
                                                 method='POST')

                    req.add_header('Content-Type', 'application/json')

                    auth_header = "Basic " + base64.b64encode(
                        (str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
                    req.add_header('Authorization', auth_header)
                    try:
                        with urllib.request.urlopen(req) as post_response:
                            if post_response.status == 204:
                                data = 'successfully create tablet client authorization rules.'
                            else:
                                data = json.loads(post_response.read().decode())
                        print(data)
                        return True

                    except Exception as e:
                        print(e)
                        return False

                else:
                    pass

            return True

        except Exception as e:
            print(e)
            return False


def delete_tablet_client_authorization_rules(tablet_user_uuid=None):
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    tablet_user = dashboard_models.HomeUser.objects.get(uuid=tablet_user_uuid)

    if tablet_user:
        tablet_user_mqtt_client_id = tablet_user.mqtt_client_id
        get_client_rules_url = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{tablet_user_mqtt_client_id}"

        auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.get(get_client_rules_url, headers=header)
            if response.status_code == 200:
                current_rules = response.json()['rules']
                
                # Filter out rules added by set_tablet_client_client_rule_to_emqx_built_in_database_authorization_backend
                updated_rules = [rule for rule in current_rules if not (
                    rule['topic'].startswith('v1/controllers/') or
                    rule['topic'].startswith(f'v1/users/tablet_user/{tablet_user_mqtt_client_id}/status') or
                    rule['topic'] == '#'
                )]

                # Update rules
                put_client_rules_url = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{tablet_user_mqtt_client_id}"
                update_payload = {"rules": updated_rules, "clientid": tablet_user_mqtt_client_id}
                update_response = requests.put(put_client_rules_url, json=update_payload, headers=header)

                if update_response.status_code == 204:
                    print("Successfully deleted tablet client authorization rules.")
                    return True
                else:
                    print("Error while updating tablet client authorization rules. Error:", update_response.content.decode())
                    return False
            else:
                print("Error while getting tablet client authorization rules. Error:", response.content.decode())
                return False
        except Exception as e:
            print("Tablet user mqtt client authorization rules deletion was unsuccessful. Reason:", str(e))
            return False
    else:
        print("Tablet user not found.")
        return False



def completely_delete_all_tablet_client_authorization_rules(tablet_user_uuid=None):
    base_url = os.environ.get('emqx_base_url')
    emqx_api_username = os.environ.get('emqx_api_username')
    emqx_api_password = os.environ.get('emqx_api_password')

    home_user = dashboard_models.HomeUser.objects.get(uuid=tablet_user_uuid)

    if home_user:
        home_user_mqtt_client_id = home_user.mqtt_client_id
        delete_client_rules_url = base_url + f"/api/v5/authorization/sources/built_in_database/rules/clients/{home_user_mqtt_client_id}"

        auth_header = "Basic " + base64.b64encode((str(emqx_api_username) + ":" + str(emqx_api_password)).encode()).decode()
        header = {'Content-Type': 'application/json',
                  'Authorization': auth_header
                  }
        try:
            response = requests.delete(delete_client_rules_url, headers=header)
            if response.status_code == 204:
                print("successfully delete tablet client authorization rules.")
                return True
            else:
                print("get error while deleting tablet client authorization rules. error:: " + response.content.decode() )
                return False
        except Exception as e:
            print("tablet mqtt client authorization rules deletion was unsuccessfully. Reason:: tablet user not found.")
            print(e)
            return False


# Update all user and controller of all project rules and rewrite them to mqtt broker backend when web service start to work
# to sure all parts are authorized in broker.

# Update all user and controller of all project mqtt users and rewrite them to mqtt broker backend when web service start to work
# # to sure all parts are authenticated in broker.

