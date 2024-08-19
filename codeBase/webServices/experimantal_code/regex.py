import re

action_status_topic = "v1/projects/{self.project_uuid}/homes/{self.home_uuid}/linkage-rules/{self.rule_uuid}" + "/actions/actions-status/14545400"
match = re.search(r'actions-status/(\d+)', action_status_topic)

if match:
    action_code = match.group(1)
    print(action_code)
else:
    print("Can't find action code")