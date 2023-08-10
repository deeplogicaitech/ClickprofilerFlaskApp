import csv
from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from pathlib import Path
import traceback
import re

app = Flask(__name__)

# Directory to store uploaded files
UPLOADS_DIRECTORY = 'uploads'

# Create the uploads directory if it doesn't exist
Path(UPLOADS_DIRECTORY).mkdir(parents=True, exist_ok=True)

def extract_filename(path):
    # Match the last part of the path that doesn't contain any path separators
    filename_match = re.search(r'[^\\/]+$', path)
    if filename_match:
        return filename_match.group()
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    error = None

    if request.method == 'POST':
        try:
            # Get the uploaded files from the form
            clickprofiler_file = request.files.get('clickprofiler')
            mappings_file = request.files.get('mappings')

            # Save the uploaded files locally
            clickprofiler_filename = save_uploaded_file(clickprofiler_file)
            mappings_filename = save_uploaded_file(mappings_file)

            # # Process the files as needed
            clickprofiler_list = process_clickprofiler_file(clickprofiler_filename)

            header = ['German Desc', 'German Key', 'German Value', 'Used']
            clickprofiler_df = pd.DataFrame(clickprofiler_list, columns = header)

            labels = process_mappings_file(mappings_filename)

            # Map German keys and values to English labels using the mappings data
            mapped_data, mapped_fields = map_keys_and_values(clickprofiler_list, labels)
            total_fields = len(mapped_data)

            # Create a Pandas dataframe from the mapped data and save it to an Excel file
            mapped_data_df = pd.DataFrame(mapped_data, columns = ['Label', 'German Desc', 'German Key', 'German Value'])
            mapped_data_df.to_excel('mapped_clickprofiler.xlsx', index=False)

            return render_template('table.html', table_content=mapped_data, mapped_fields=mapped_fields, total_fields=total_fields, cp_file=extract_filename(clickprofiler_filename), map_file=extract_filename(mappings_filename))

        except Exception as e:
            print(e)
            traceback.print_exc()
            error = "Error processing files. Please check the files and try again."

    return render_template('index.html', message=message, error=error)

def save_uploaded_file(uploaded_file):
    if uploaded_file:
        filename = uploaded_file.filename
        file_path = os.path.join(UPLOADS_DIRECTORY, filename)
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

@app.route('/download_excel')
def download_excel():
    return send_file("mapped_clickprofiler.xlsx", as_attachment=True)

# Handle 404 errors and display the custom 404 page
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port = 5001)