import requests
import json
from requests.structures import CaseInsensitiveDict
import openai


def prepare_quizchatgpt(request_body):
    openai.api_key = "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"

    content = request_body
    prompt = '''Create Multiple choice Questions and Answer for the content , only provide JSON response following this format without deviation.
    [{question="",options{option_1="",option_2="",option_3="",option_4=""}answer="option"}]'''

    completion1 = openai.ChatCompletion.create(

        model="gpt-4",

        messages=[
            {"role": "assistant", "content": content},
            {"role": "user", "content": prompt}

        ]

    )
    content = completion1['choices'][0]['message']['content']

    text_summary = content
    print("?????????????????  Quiz chatgpt", text_summary)

    return json.loads(text_summary)


def correct_answer_function(options, answer):
    a = []
    for idx, x in enumerate(options):
        if x == answer:
            a.append(str(idx))
        else:
            a.append("")

    return a


def prepare_quiz_json(chatgpt_response, learning_bite_id):
    json_template_temp = {
        "isDeleted": False,
        "lessons": learning_bite_id,
        "passingScore": 1,
        "correctAssesmentValue": "",
        "correctAssesmentVideoUrl": "",
        "correctAssesmentFilePath": None,
        "quiz": {
            "questions": []}
    }

    message_count = 0
    for s in chatgpt_response:
        correct_answer = correct_answer_function(
            s["options"], s["answer"])

        answer_options = [s["options"]["option_1"],
                          s["options"]["option_2"], s["options"]["option_3"], s["options"]["option_4"]]

        question = {
            "isHtml": True,
            "answerFilePath": [
                "",
                ""
            ],
            "isImageUpload": False,
            "answerOptions": answer_options,
            "correctAnsIndexes": correct_answer,
            "question": "<p>" + s["question"] + "</p>",
            "score": "0",
            "isMultiSelect": False,
            "note": "",
            "questionFilePath": None,
            "correctAnswerFeedbackText": "",
            "correctAnswerVideoUrl": "",
            "correctAnswerFilePath": None
        }

        json_template_temp["quiz"]["questions"].append(question)
        message_count = message_count + 1
        json_template_temp["passingScore"] = message_count
    print("\n\n Final Json template is : ", json_template_temp)
    return json_template_temp


def create_quiz(request_body, learning_bite_id):
    url = "https://testplato.harbingergroup.com/api/quiz/createquiz"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NDIyOGIwY2MzN2E3NmMwYTlmMzYxNTQiLCJyb2xlIjoiQXV0aG9yIiwib3JnYW5pemF0aW9uSWQiOiI1ZThkYWZjN2EwYzRjZjQ1OTdlZjQ4MjciLCJwbGFuIjoiNWVkMGE4ZWYzYzk1YTY5MTY0ODJkZTM5IiwidXNlcm5hbWUiOiJuZWhhLmJoYXJ0aUBoYXJiaW5nZXJncm91cC5jb20iLCJmaXJzdE5hbWUiOiJOZWhhIiwibGFzdE5hbWUiOiJCaGFydGkiLCJpYXQiOjE2ODY2NzQ0ODQsImV4cCI6MTY4NjcxNzY4NH0.PhSRBGyhDrXttmYHdc-UjETYW-3P9NriqYnuQC1McAk"
    headers["Content-Type"] = "application/json"
    headers["Username"] = "neha.bharti@harbingergroup.com"
    chatgptoutput = prepare_quizchatgpt(request_body)
    payload = prepare_quiz_json(chatgptoutput, learning_bite_id)
    res = requests.post(url, headers=headers,
                        data=json.dumps(payload), verify=False)
    print("Response is :", res.content)
    if res.status_code == 200:
        quiz_id = json.loads(res.content.decode("utf-8"))["data"]["_id"]
        print("Quiz created successfully with id {}!!".format(quiz_id))
    else:
        quiz_id = ""
