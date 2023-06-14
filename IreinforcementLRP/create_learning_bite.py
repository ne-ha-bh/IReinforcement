import requests
import json
from requests.structures import CaseInsensitiveDict
import openai
# import process_300_words_chunks_with_new_model


def format_pages_text(text_summary):

    openai.api_key = "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"
    content = text_summary
    # content = "A bank is defined by Merriam-Webster as an establishment for the custody, loan, exchange, or issue of money, for the extension of credit, and for facilitating the transmission of funds. Banking can be defined as the business of banking, a vibrant business that continually evolves to meet the latest financial needs and economic conditions. To understand how banking evolves, it is important to gain a broad understanding of financial concepts, fundamental banking functions, and the banking business in a technology driven world. A bank is a regulated and lawful financial institution that includes deposit services, keep a check of safety, and provide withdrawals when required. The investors can deposit their surplus to receive interest in return and withdraw it when needed whereas the firms looking for loans or funds for immediate needs can gain it from banks by paying interest rates. As a result, it creates liquidity for money which helps in economic development. However, when a group of financial institutions or banks provides services to the public it is termed a banking system. Types Of Banks Savings Bank - Most of the commercial bank carries the function of providing savings bank. This type of bank helps customers with saving habit. Its suites to low-income groups and salaried people. As a result, the amount that the bank collects from people invests in securities, bonds etc. The postal department also plays a function of the savings bank. Industrial Banks - The Development banks or industrial banks collect cash by issuing debentures and shares or provide long term loans to the industry. The major objective of industrial banks is to provide loans to businesses for modernization and expansion. Commercial Banks - The main purpose of these banks is to help businesspeople or businessmen. The banks take deposits from the public and aid the businessperson with short term loans via overdrafts, cash credits, etc. Also, the commercial banks perform various functions such as bill of exchange, collecting cheques, remittance money from place to place."
    prompt = "create Summary from the content"
    # prompt_question = "create Short question answers for this content"

    completion1 = openai.ChatCompletion.create(

        #model="gpt-3.5-turbo",
        model = "gpt-4",

        messages=[
            {"role": "assistant", "content": content},
            {"role": "user", "content": prompt}
            # {"role": "user", "content": prompt_question}

        ]

    )
    content = completion1['choices'][0]['message']['content']

    text_summary = content
    print("-----------------", text_summary)

    final_page = {"text": "", "image": "", "isHtml": True,
                  "isVideo": False, "url": "", "isImageUrl": False, "imageUrl": ""}
    pages_content = []
    if len(text_summary) > 1000:
        # chunk it
        summary_list = text_summary.split(".")
        temp_summary = ""
        for index, summary in enumerate(summary_list):
            if index == len(summary_list) - 1:
                temp_summary = temp_summary + summary
                temp_summary = "<p>" + temp_summary + '</p>'
                temp = {"text": temp_summary, "image": "", "isHtml": True,
                        "isVideo": False, "url": "", "isImageUrl": False, "imageUrl": ""}
                pages_content.append(temp)
                break
            elif len(temp_summary) < 1000:
                temp_summary = temp_summary + summary
            else:
                temp_summary = "<p>" + temp_summary + '</p>'
                temp = {"text": temp_summary, "image": "", "isHtml": True,
                        "isVideo": False, "url": "", "isImageUrl": False, "imageUrl": ""}
                pages_content.append(temp)
                temp_summary = ""
        pages_content.append(final_page)
    else:
        temp = {"text": text_summary, "image": "", "isHtml": True,
                "isVideo": False, "url": "", "isImageUrl": False, "imageUrl": ""}
        pages_content.append(temp)
        pages_content.append(final_page)
    return pages_content


def prepare_learning_bite_json(nugget_id, learning_bite_name, text_summary):
    page_content = format_pages_text(text_summary=text_summary)
    json_template = {
        "actionName": "Add Learning bite",
        "title": learning_bite_name,
        "description": "This is learning bite",
        "skill_id": nugget_id,
        "image": "",
        "author": "",
        "enableFromDate": "",
        "pages": page_content,
        "themeId": "0",
        "disableFontColor": False,
        "backgroundImageId": "",
        "tooltipOpen": False,
        "pageContentLimit": 1000,
        "loading": True,
        "isPublished": False,
        "imageSizeLimit": 500,
        "imageSizeConvert": 0.000976562,
        "lessonFontColor": "#000000",
        "lessonToggleFlag": False,
        "lessonToggleName": "Show Learning bites",
        "modalOpen": False,
        "colorModalOpen": False,
        "themeImgPreview": "",
        "themePreviewOpen": False,
        "isPPT": False,
        "selectedPPTFile": "",
        "pptFileSizeLimit": 153315,
        "pptloader": False,
        "files": [],
        "pptTooltipOpen": False,
        "checkFile": False,
        "checkUpload": False,
        "fileInputKey": 1673943034296,
        "visible": False,
        "deleteReason": "",
        "lessonId": "",
                    "errors": {"actionNameError": "", "titleError": "", "descriptionError": "", "imageError": "", "skillListError": "", "lessonImageError": "", "themeListError": "", "lessonFontColorError": "", "backgroundImageError": "", "pptImportError": ""},
                    "pagesParamsError": [{"textError": ""}]
    }
    return json_template


def create_learning_bite(nugget_id, learning_bite_name, text_summary):
    print("\nInside create_learning_bite")
    url = "https://testplato.harbingergroup.com/api/lessons/createLesson"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NDIyOGIwY2MzN2E3NmMwYTlmMzYxNTQiLCJyb2xlIjoiQXV0aG9yIiwib3JnYW5pemF0aW9uSWQiOiI1ZThkYWZjN2EwYzRjZjQ1OTdlZjQ4MjciLCJwbGFuIjoiNWVkMGE4ZWYzYzk1YTY5MTY0ODJkZTM5IiwidXNlcm5hbWUiOiJuZWhhLmJoYXJ0aUBoYXJiaW5nZXJncm91cC5jb20iLCJmaXJzdE5hbWUiOiJOZWhhIiwibGFzdE5hbWUiOiJCaGFydGkiLCJpYXQiOjE2ODY2NzQ0ODQsImV4cCI6MTY4NjcxNzY4NH0.PhSRBGyhDrXttmYHdc-UjETYW-3P9NriqYnuQC1McAk"
    headers["Content-Type"] = "application/json"
    headers["Username"] = "neha.bharti@harbingergroup.com"

    payload = prepare_learning_bite_json(
        nugget_id, learning_bite_name, text_summary)
    res = requests.post(url, headers=headers,
                        data=json.dumps(payload), verify=False)
    print("\nLearning Bite Response is :", res.content)
    if res.status_code == 200:
        learning_id = json.loads(res.content.decode("utf-8"))["data"]["_id"]
        print("\nLearning Bite created successfully with id {}!!".format(learning_id))
        return learning_id
    else:
        return ""
