import csv
from flask import Flask, render_template, request, send_file, redirect
import os
import pandas as pd
from pathlib import Path
import traceback
import uuid
import json
from urllib.parse import unquote
from collections import OrderedDict
import timeago, datetime
import shutil
import re

app = Flask(__name__)

# Directory to store uploaded files
UPLOADS_DIRECTORY = 'uploads'
SAVED_DIRECTORY = 'saved'

uuid_key = None

# Create the uploads directory if it doesn't exist
Path(UPLOADS_DIRECTORY).mkdir(parents=True, exist_ok=True)
Path(SAVED_DIRECTORY).mkdir(parents=True, exist_ok=True)

def extract_filename(path):
    # Match the last part of the path that doesn't contain any path separators
    filename_match = re.search(r'[^\\/]+$', path)
    if filename_match:
        return filename_match.group()
    else:
        return None

@app.template_filter('timeago')
def timeago_filter(timestamp):
    stored_timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    if timedelta := datetime.datetime.now() - stored_timestamp:
        if timedelta.days > 0:
            return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
        else:
            return timeago.format(timestamp, datetime.datetime.now())

@app.route('/', methods=['GET', 'POST'])
def index(key = None):
    message = None
    error = None

    saved_mappings = {}

    if request.method == 'POST':
        uuid_key = str(uuid.uuid4().hex)
        try:
            # Get the uploaded files from the form
            clickprofiler_file = request.files.get('clickprofiler')
            mappings_file = request.files.get('mappings')

            # Save the uploaded files locally
            clickprofiler_filepath = save_uploaded_file_2_location(clickprofiler_file, UPLOADS_DIRECTORY)
            mappings_filepath = save_uploaded_file_2_location(mappings_file, UPLOADS_DIRECTORY)

            #################################################################
            if request.form.get('savecheckbox') == 'on':
                # Save the uploaded files to the saved directory
                Path(os.path.join(SAVED_DIRECTORY, uuid_key)).mkdir(parents=True, exist_ok=True)
                cp_loc = save_uploaded_file_2_location(clickprofiler_file, os.path.join(SAVED_DIRECTORY, uuid_key))
                mp_loc = save_uploaded_file_2_location(mappings_file, os.path.join(SAVED_DIRECTORY, uuid_key))

                # cp_loc = f'{SAVED_DIRECTORY}/{uuid_key}/{extract_filename(clickprofiler_filepath)}'
                # mp_loc = f'{SAVED_DIRECTORY}/{uuid_key}/{extract_filename(mappings_filepath)}'

                new_entry = {
                    'cp_filename': extract_filename(clickprofiler_filepath),
                    'mp_filename': extract_filename(mappings_filepath),
                    'timestamp': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                }

                # Check if the file exists and its empty before trying to read it
                if os.path.exists('saved_mappings.json') and os.stat('saved_mappings.json').st_size > 0:
                    with open('saved_mappings.json', 'r') as json_file:
                        saved_mappings = json.load(json_file)

                # Now you have the data loaded into the 'saved_mappings' dictionary
                key = uuid_key
                saved_mappings[key] = new_entry

                # Write the updated data back to the file
                with open('saved_mappings.json', 'w') as json_file:
                    json.dump(saved_mappings, json_file, indent=2)
            #################################################################

            # From hereon, we actually use the saved files
            mapped_data, mapped_fields, total_fields = mapping_function(clickprofiler_filepath, mappings_filepath)

            # Create a Pandas dataframe from the mapped data and save it to an Excel file
            mapped_data_df = pd.DataFrame(mapped_data, columns = ['Label', 'German Desc', 'German Key', 'German Value'])
            mapped_data_df.to_excel('mapped_clickprofiler.xlsx', index=False)

            return render_template('table.html', table_content=mapped_data, mapped_fields=mapped_fields, total_fields=total_fields, cp_file=extract_filename(clickprofiler_filepath), map_file=extract_filename(mappings_filepath))

        except Exception as e:
            print(e)
            traceback.print_exc()
            error = "Error processing files. Please check the files and try again."

    # Check if the file exists and its empty before trying to read it
    if os.path.exists('saved_mappings.json') and os.stat('saved_mappings.json').st_size > 0:
        with open('saved_mappings.json', 'r') as json_file:
            saved_mappings = json.load(json_file)

    ordered_saved_mappings = OrderedDict(saved_mappings)
    return render_template('index.html', message=message, saved_mappings=ordered_saved_mappings, error=error)

def save_uploaded_file_2_location(uploaded_file, location):
    if uploaded_file:
        # print(uploaded_file.read())  # Read and print the content
        uploaded_file.seek(0)  # Reset the file pointer
        filename = uploaded_file.filename
        file_path = os.path.join(location, filename)
        uploaded_file.save(file_path)
        return file_path
    return None

def process_clickprofiler_file(clickprofiler_file):
    with open(clickprofiler_file, encoding = 'utf-8') as fd:
        reader=csv.reader(fd)
        desc_index=[]
        for idx, row in enumerate(reader):
            if idx == 0:
                first_row = row
                for key in range(26, len(row), 2):
                        desc_index.append(first_row[key].partition('(')[0].strip())
            if idx == 1:
                second_row = row

    clickprofiler_list = []
    for idx in range(26, len(first_row), 2):
        clickprofiler_list += [[first_row[idx].partition('(')[0].strip(), second_row[idx], second_row[idx+1], False]]

    return clickprofiler_list

def process_mappings_file(mappings_file):
    with open(mappings_file, encoding = 'utf-8') as fd:
        reader=csv.reader(fd)
        next(reader)
        labels = []
        # 1: English Label, 2: German Desc
        for idx, row in enumerate(reader):
            kv = {
                    'lbl': row[1].strip(),
                    'desc': row[2].strip(),
                    'used': False
                }
            labels.append(kv)
    return labels

def map_keys_and_values(clickprofiler_list, mappings_data):
    mapped_data = []
    total_mapped_fields = 0

    for labelkv in mappings_data:
        for item in clickprofiler_list:
            if item[0] in labelkv['desc'] and not labelkv['used'] and not item[3]:
                templ = [labelkv['lbl'], item[0], item[1], item[2]]
                mapped_data.append(templ)
                total_mapped_fields += 1
                labelkv['used'] = True
                item[3] = True
                break

        if not labelkv['used']:
            temp = [labelkv['lbl'], labelkv['desc'], '-', '-']
            labelkv['used'] = True
            mapped_data.append(temp)

    return mapped_data, total_mapped_fields

def mapping_function(clickprofiler_filepath, mappings_filepath):
    # Process the files as needed
    clickprofiler_list = process_clickprofiler_file(clickprofiler_filepath)
    labels = process_mappings_file(mappings_filepath)

    # Map German keys and values to English labels using the mappings data
    mapped_data, mapped_fields = map_keys_and_values(clickprofiler_list, labels)
    total_fields = len(mapped_data)

    return mapped_data, mapped_fields, total_fields

# Call this route when a saved mapping card is clicked from the index page
@app.route('/saved-mappings/<string:key>', methods=['GET'])
def perform_mapping(key):
    if request.method == 'GET':
        cp_filename = request.args.get('cp')
        mp_filename = request.args.get('mp')

        # Read cp and mp files from the saved folder
        cp_filepath = os.path.join(SAVED_DIRECTORY, key, cp_filename)
        mp_filepath = os.path.join(SAVED_DIRECTORY, key, mp_filename)

        if not (os.path.exists(cp_filepath) and os.path.exists(mp_filepath)):
            if os.path.exists('saved_mappings.json') and os.stat('saved_mappings.json').st_size > 0:
                with open('saved_mappings.json', 'r') as json_file:
                    saved_mappings = json.load(json_file)

                # Now you have the data loaded into the 'saved_mappings' dictionary
                saved_mappings.pop(key, None)

                # Write the updated data back to the file
                with open('saved_mappings.json', 'w') as json_file:
                    json.dump(saved_mappings, json_file, indent=2)

            return render_template('index.html', error='Files not found')

        # From hereon, we actually use the saved files
        mapped_data, mapped_fields, total_fields = mapping_function(cp_filepath, mp_filepath)

        # Create a Pandas dataframe from the mapped data and save it to an Excel file
        mapped_data_df = pd.DataFrame(mapped_data, columns = ['Label', 'German Desc', 'German Key', 'German Value'])
        mapped_data_df.to_excel('mapped_clickprofiler.xlsx', index=False)

        return render_template('table.html', table_content=mapped_data, mapped_fields=mapped_fields, total_fields=total_fields, cp_file=cp_filename, map_file=mp_filename)

@app.route('/delete-mapping/<string:key>', methods=['GET'])
def delete_mapping(key):
    if request.method == 'GET':
        cp_filename = request.args.get('cp')
        mp_filename = request.args.get('mp')

        # Read cp and mp files from the saved folder
        cp_filepath = os.path.join(SAVED_DIRECTORY, key, cp_filename)
        mp_filepath = os.path.join(SAVED_DIRECTORY, key, mp_filename)

        # Delete the files
        if os.path.exists(cp_filepath):
            os.remove(cp_filepath)
        if os.path.exists(mp_filepath):
            os.remove(mp_filepath)

        # Delete the folder
        if os.path.exists(os.path.join(SAVED_DIRECTORY, key)):
            os.rmdir(os.path.join(SAVED_DIRECTORY, key))

        # Delete the entry from the saved_mappings.json file
        if os.path.exists('saved_mappings.json') and os.stat('saved_mappings.json').st_size > 0:
            with open('saved_mappings.json', 'r') as json_file:
                saved_mappings = json.load(json_file)

            # Now you have the data loaded into the 'saved_mappings' dictionary
            saved_mappings.pop(key, None)

            # Write the updated data back to the file
            with open('saved_mappings.json', 'w') as json_file:
                json.dump(saved_mappings, json_file, indent=2)

        return redirect('/')

@app.route('/delete-all-mappings', methods=['GET'])
def delete_all_mappings():
    if request.method == 'GET':
        # Delete the files
        if os.path.exists('saved_mappings.json'):
            os.remove('saved_mappings.json')

        # Delete the folder
        if os.path.exists(SAVED_DIRECTORY):
            shutil.rmtree(SAVED_DIRECTORY, True)

        return redirect('/')

@app.route('/download_excel')
def download_excel():
    return send_file("mapped_clickprofiler.xlsx", as_attachment=True)

# Handle 404 errors and display the custom 404 page
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port = 5001)