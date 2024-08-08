import urllib.request
import json
import base64

username = 'ee26b0dd4af7e749'
password = 'RLSdhQGpxR0QXWt8qZThPu2hF1TiyuptRzqFwU8GD5O'

# url = 'http://localhost:18083/api/v5/authentication/password_based:built_in_database/users'
#
# req = urllib.request.Request(url, data=json.dumps({"password": "4545454","user_id": "user1"}).encode('utf-8'))
# req.add_header('Content-Type', 'application/json')
#
# auth_header = "Basic " + base64.b64encode((username + ":" + password).encode()).decode()
# req.add_header('Authorization', auth_header)
#
# with urllib.request.urlopen(req) as response:
#     data = json.loads(response.read().decode())
#
# print(data)



url = 'http://localhost:18083/api/v5/authorization/sources/built_in_database/rules/users/user1/'

req = urllib.request.Request(url, method='PUT', data=json.dumps({
  "rules": [
    {
      "action": "publish",
      "topic": "test/topic/1",
      "permission": "allow"
    },
    {
      "action": "subscribe",
      "topic": "test/topic/2",
      "permission": "allow"
    },
    {
      "action": "all",
      "topic": "test/#",
      "permission": "deny"
    },
    {
      "action": "publish",
      "retain": "true",
      "topic": "test/topic/3",
      "qos": [
        "1"
      ],
      "permission": "allow"
    },
    {
      "action": "publish",
      "retain": "all",
      "topic": "test/topic/4",
      "qos": [
        "0",
        "1",
        "2"
      ],
      "permission": "allow"
    }
  ],
  "username": "user1"
}).encode('utf-8'))
req.add_header('Content-Type', 'application/json')

auth_header = "Basic " + base64.b64encode((username + ":" + password).encode()).decode()
req.add_header('Authorization', auth_header)

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())

print(data)













# username = 'ee26b0dd4af7e749'
# password = 'RLSdhQGpxR0QXWt8qZThPu2hF1TiyuptRzqFwU8GD5O'
#
# url = 'http://localhost:18083/api/v5/authentication'
#
# req = urllib.request.Request(url)
# req.add_header('Content-Type', 'application/json')
#
# auth_header = "Basic " + base64.b64encode((username + ":" + password).encode()).decode()
# req.add_header('Authorization', auth_header)
#
# with urllib.request.urlopen(req) as response:
#     data = json.loads(response.read().decode())
#
# print(data)