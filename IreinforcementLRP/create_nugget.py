import requests
import json
from requests.structures import CaseInsensitiveDict


def prepare_nugget_json(nugget_name):
    json_template = {
        "isGeneralSkill": False,
        "skill_id": "",
        "name": nugget_name,
        "description": "This is test nugget",
        "image": "",
        "skillImage": "",
        "icon": "",
        "tags": ["test2"],
        "actionName": "Add Nugget",
        "skillsToggleFlag": False,
        "skillToggleName": "Show Nuggets",
        "iconPreviewUrl": "",
        "tooltipOpen": False,
        "imageSizeLimit": 500,
        "imageSizeConvert": 0.000976562,
        "searchText": "",
        "loading": True,
        "perPageCount": 10,
        "page": 1,
        "visible": False,
        "deleteReason": "",
        "skillId": "",
        "errors": {"nameError": "", "descriptionError": "", "skillImageError": "", "skillIconError": "", "tagsError": "", "tagsArrayError": ""}
    }
    return json_template

def create_nugget(nuggest_name):
    print("Inside create_nugget")
    url = "https://testplato.harbingergroup.com/api/createSkill"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NDIyOGIwY2MzN2E3NmMwYTlmMzYxNTQiLCJyb2xlIjoiQXV0aG9yIiwib3JnYW5pemF0aW9uSWQiOiI1ZThkYWZjN2EwYzRjZjQ1OTdlZjQ4MjciLCJwbGFuIjoiNWVkMGE4ZWYzYzk1YTY5MTY0ODJkZTM5IiwidXNlcm5hbWUiOiJuZWhhLmJoYXJ0aUBoYXJiaW5nZXJncm91cC5jb20iLCJmaXJzdE5hbWUiOiJOZWhhIiwibGFzdE5hbWUiOiJCaGFydGkiLCJpYXQiOjE2ODY2NzQ0ODQsImV4cCI6MTY4NjcxNzY4NH0.PhSRBGyhDrXttmYHdc-UjETYW-3P9NriqYnuQC1McAk"
    headers["Content-Type"] = "application/json"
    headers["Username"] = "neha.bharti@harbingergroup.com"

    payload = prepare_nugget_json(nuggest_name)
    res = requests.post(url, headers=headers,
                        data=json.dumps(payload), verify=False)
    print("Response is :", res.content)
    if res.status_code == 200:
        nugget_id = json.loads(res.content.decode("utf-8"))["data"]["_id"]
        print("Nugget created successfully with id {}!!".format(nugget_id))
        return nugget_id
    else:
        return ""
