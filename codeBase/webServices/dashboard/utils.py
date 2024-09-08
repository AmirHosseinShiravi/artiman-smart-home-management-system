import base64
import json
import os
import secrets
import string
import urllib.request

import requests
from dotenv import load_dotenv
import dashboard.models as dashboard_models


load_dotenv()  # take environment variables from .env.


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


def generate_controller_credentials():
    pass


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


def delete_all_web_app_client_authorization_rules(home_user_uuid=None):
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


def delete_all_tablet_client_authorization_rules(tablet_user_uuid=None):
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

