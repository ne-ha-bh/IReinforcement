
import os
import stat
import time
import uuid
import zipfile
import re
import shutil
import csv
import os
import pandas as pd
import json
from IreinforcementLRP.create_nugget import create_nugget
from .create_quiz_new import create_quiz
from .create_learning_bite import create_learning_bite
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@require_POST
@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        zip_file = request.FILES['file']
        file_extension = os.path.splitext(zip_file.name)[1]

        if file_extension == '.zip':
            # Generate a unique id
            unique_id = str(uuid.uuid4())
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id)

            # Create the directory if it doesn't exist
            os.makedirs(upload_path, exist_ok=True)

            # Save the uploaded zip file
            zip_path = os.path.join(upload_path, zip_file.name)
            with open(zip_path, 'wb') as f:
                for chunk in zip_file.chunks():
                    f.write(chunk)

            # Unzip the file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(upload_path)

            # Call get_scorm_data to process the extracted files
            extracted_path = os.path.join(upload_path, 'html5', 'data')
            get_scorm_data(unique_id, extracted_path)  

            # Assuming story.html is present in the extracted files
            story_path = os.path.join(upload_path, 'story.html')

            # Generate the preview URL
            preview_url = f"http://localhost:8000/{unique_id}/story.html"
            return JsonResponse({
                'id': unique_id,
                'preview_url': preview_url
            })
        else:
            return JsonResponse({'error': 'Invalid file format'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)
def preview_story(request, unique_id):
    story_html_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id, 'story.html')
    if not os.path.exists(story_html_path):
        return HttpResponse("File not found")

    with open(story_html_path, 'r') as file:
        html_content = file.read()

    return HttpResponse(html_content, content_type='text/html')


def get_scorm_data(request, unique_id):
   
    upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id)
    extracted_path = os.path.join(upload_path, 'html5', 'data')
    if not os.path.exists(extracted_path):
        return JsonResponse({'error': 'UUID folder not found'}, status=400) 
    print("Extracted Path:", extracted_path)  
    js_dir = os.path.join(extracted_path, 'js')
    main_dir = os.path.join(js_dir, 'main')
    # Print the main_dir path to check if it is correct
    print("Main Directory Path:", main_dir)
    os.makedirs(main_dir, exist_ok=True)

    js_files = [
        file for file in os.listdir(os.path.join(extracted_path, 'js'))
        if file.endswith('.js') and re.match(r'^\d', file)
    ]
    for js_file in js_files:
        src_path = os.path.join(extracted_path, 'js', js_file)
        dest_path = os.path.join(main_dir, js_file)
        shutil.move(src_path, dest_path)

    csv_file_path = os.path.join(main_dir, 'output.csv')

    # Process the extracted files and save the text as a CSV file
    header = ["slide_number", "title", "ost"]
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)

    table_data = []
    for filename in os.listdir(main_dir):
        filepath = os.path.join(main_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            data = file.read()

        title_match = re.search(r'"title":"([^"]+)"', data)
        title = title_match.group(1) if title_match else ""

        slide_number_match = re.search(r'"slideNumberInScene":(\d+)', data)
        slide_number = int(slide_number_match.group(1)) if slide_number_match else 0

        texts = re.findall(r'"text":"([^"]+)"', data)
        concatenated_text = ' '.join(texts)
        concatenated_text = concatenated_text.replace('â€', '').replace('\\n', '').replace(' \ ', '').replace('\\', '')

        row = {
            'slide_number': slide_number,
            'title': title,
            'ost': concatenated_text
        }
        table_data.append(row)

        with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([slide_number, title, concatenated_text])

    # Sort the rows based on slide number
    table_data = sorted(table_data, key=lambda row: row['slide_number'])
    table_data = [row for row in table_data if row['slide_number'] != 0]
    
    process_300_chunks(unique_id, 'output.csv')
    return JsonResponse({
        'id': unique_id,
        'table_data': table_data
    })
    

def update_scorm_data(request, unique_id):
    if request.method == 'PATCH':
        # Include the CSRF token in the response headers
        csrf_token = csrf.get_token(request)
        response = JsonResponse({'message': 'Table data updated successfully.'})
        response['X-CSRFToken'] = csrf_token

        updated_data = json.loads(request.body.decode('utf-8')).get('data', None)
        if updated_data is None:
            return JsonResponse({'error': 'Invalid request payload.'}, status=400)

        # Process the updated data
        update_output_csv(unique_id, updated_data)

        return response

    return JsonResponse({'error': 'Invalid request method.'}, status=405)
def prepare_request_body(complete_ost_list, title_list, nugget_id):
    print("\nInside prepare_request_body")
    total_word_count = sum(len(i.split(" ")) for i in complete_ost_list)
    print("\nTotal Initial Word Count in final OST list: ", total_word_count)
    complete_ost_string = ""
    if total_word_count < 301:
        print("Word Count is very low for Creating Quiz")
        return "Word Count is very low for Creating Quiz"
    else:
        start_index = 0
        for index in range(0, len(complete_ost_list)):
            if complete_ost_string:
                complete_ost_string = complete_ost_string + \
                    " " + complete_ost_list[index]
            else:
                complete_ost_string = complete_ost_list[index]
            total_chars = len(complete_ost_string.split(" "))
            if total_chars > 301:
                learning_bite_title = "This is a Learning Bite"
                if title_list:
                    for title in title_list[start_index:index]:
                        if type(title) == type("dummy"):
                            learning_bite_title = title
                            break
                start_index = index
                generate_mcq_and_summary(
                    complete_ost_string, nugget_id, learning_bite_title)
                total_chars = 0
                complete_ost_string = ""
        return "Successfully Created Learning Bite"


def generate_mcq_and_summary(request_body, nugget_id, learning_bite_title):
    print("\nCalling generate_json for MCQ and Summary")
    print("\nRequest Body : ", request_body)
    with open("output.txt", "a") as f:
        f.write(request_body)
        f.write("\n\n")
    learning_bite_id = create_learning_bite(
        nugget_id, learning_bite_title, request_body)
        
    create_quiz(request_body, learning_bite_id)


def process_csv(filename,unique_id):
    upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id)
    main_dir = os.path.join(upload_path, 'html5', 'data', 'js', 'main')
    csv_file_path = os.path.join(main_dir, filename)
    cwd = os.getcwd()
    df = pd.read_csv(os.path.join(cwd, csv_file_path))
    complete_ost_list, title_list = [], []
    df = df[[ "title", "ost"]].values
    for title, ost_value in df:
        if type(ost_value) == type("dummy"):
            complete_ost_list.append(ost_value)
            title_list.append(title)
    return complete_ost_list, title_list

def process_300_chunks(unique_id, filename):
    #time.sleep(3)
    upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id)
    main_dir = os.path.join(upload_path, 'html5', 'data', 'js', 'main')
    csv_file_path = os.path.join(main_dir, filename)
    os.chmod(csv_file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

    nugget_id =create_nugget("LRPUITEST")
    if nugget_id != "":
        complete_ost_list, title_list = process_csv(filename, unique_id)
        status = prepare_request_body(complete_ost_list, title_list, nugget_id)
        print("\n~~~~~~~~~~~~~~~~  Final Status of the process is => {}  ~~~~~~~~~~~~~~~~~".format(status))
def update_output_csv(unique_id, updated_data):
    upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id)
    main_dir = os.path.join(upload_path, 'html5', 'data', 'js', 'main')
    csv_file_path = os.path.join(main_dir, 'output.csv')

    # Read the existing data from the CSV file
    table_data = []
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            table_data.append(row)

    # Update the table data with the new values
    for updated_row in updated_data:
        row_index = int(updated_row.get('row_index', -1))
        if row_index >= 0 and row_index < len(table_data):
            table_data[row_index]['slide_number'] = updated_row.get('slide_number', '')
            table_data[row_index]['title'] = updated_row.get('title', '')
            table_data[row_index]['ost'] = updated_row.get('ost', '')

    # Write the updated data back
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ["slide_number", "title", "ost"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table_data)

    # Call process_300_chunks with the updated CSV file
    process_300_chunks(unique_id, 'output.csv')
def get_csrf_token(request):
    csrf_middleware = csrf.get_token_middleware()
    return csrf_middleware.process_view(request, None, (), {})
