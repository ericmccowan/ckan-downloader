import argparse
import csv
import os
import requests
from urllib import parse
import json
import sys

from pathlib import Path
import re

COLOUR = '\033[1;36m' # cyan

def run_interactive_session():
    print('{}CKAN Downloader {}\n'.format(COLOUR, __version__))

    dataset_id_list = list()

    site_ok = False
    while not site_ok:
        in_url = input('{}What is the data portal URL? '.format(COLOUR))
        ckan_url = get_ckan_url(in_url)
        try:
            test_api_url = ckan_url + 'site_read'
            site_ok = requests.get(test_api_url).json().get('result')
            if site_ok:
                print('{}Test connection to {} was successful.'.format(COLOUR, test_api_url))
            else:
                print('{}Test connection to {} was unsuccessful, please check the URL and try again.'.format(COLOUR,
                                                                                                             test_api_url))
        except:
            print('{}There was an issue reading the URL, please check and try again.'.format(COLOUR))

    opt_csv = check_bool(input('{}Do you have a CSV with the dataset IDs to download? (y/n) '.format(COLOUR)))

    if opt_csv:
        csv_path = ''
        while not os.path.exists(path=csv_path):
            csv_path = input('{}What is the CSV file path? '.format(COLOUR))

        opt_header = check_bool(input('{}Does this CSV have a header row? (y/n) '.format(COLOUR)))

        if opt_header:
            with open(csv_path) as csvfile:
                reader = csv.DictReader(csvfile)

                print('{}The name of the field/column containing the dataset IDs is needed. The options are:'.format(
                    COLOUR))
                print('{}    {}'.format(COLOUR, ', '.join(reader.fieldnames)))

                id_field = ''
                while id_field == '' or id_field not in reader.fieldnames:
                    id_field = input('{}Which field has the IDs? '.format(COLOUR))

                for row in reader:
                    dataset_id_list.append(row[id_field])

        else:
            confirmed = False
            field_id = 0
            print('{}The index of the field/column containing the dataset IDs is needed. The first row is:'.format(
                COLOUR))
            with open(csv_path) as csvfile:
                reader = csv.reader(csvfile)
                # print first row
                for row in reader:
                    print('{}    {}'.format(COLOUR, ', '.join(row)))
                    row_length = len(row)
                    break
            while not confirmed:
                field_id = int(input('{}What is the index of the field? (1-{}) '.format(COLOUR, row_length)))

                with open(csv_path) as csvfile:
                    reader = csv.reader(csvfile)

                    for row in reader:
                        print('{}    {}'.format(COLOUR, row[field_id - 1]))
                        break

                confirmed = check_bool(input('{}Is this value correct? (y/n)'.format(COLOUR)))

            with open(csv_path) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    dataset_id_list.append(row[field_id - 1])

    else:
        input_ids_str = input('{}What are the dataset IDs to download? (comma-separated list) '.format(COLOUR))
        dataset_id_list = [x.strip() for x in input_ids_str.split(',')]

    dir_exists = False
    while not dir_exists:
        data_dir = input('{}Which directory should the downloads be saved in? '.format(COLOUR))
        try:
            dir_exists = os.path.exists(data_dir)
            if not dir_exists:
                Path(data_dir).mkdir(parents=True, exist_ok=True)
                dir_exists = os.path.exists(data_dir)
                if not dir_exists:
                    print('{}There was an issue creating the directory, please check and try again.'.format(COLOUR))
        except:
            print('{}There was an issue accessing the directory, please check and try again.'.format(COLOUR))


    return dataset_id_list, ckan_url, data_dir

def check_bool(input):
    if str(input).lower() in ['y', 'yes', 'true', '']:
        return True
    else:
        return False

def get_ckan_url(in_url=None):
    if in_url is None or in_url == '':
        return 'https://geoscience.data.qld.gov.au/api/action/'
    # ensure there is a schema so we can urlparse it
    if not re.search('^http[s]?://', in_url):
        in_url = 'https://' + in_url

    urlp = parse.urlparse(in_url)

    result_url =  parse.urljoin('https://' + urlp.netloc, 'api/action/')
    return result_url


if __name__ == '__main__':
    from _version import __version__
    # dataset_id_list = list()

    # todo add command line option

    dataset_id_list, ckan_url, data_dir = run_interactive_session()
    # print(dataset_id_list)

    # Iterate through rows
    for dataset in dataset_id_list:

        # Get the dataset PID
        print('Starting dataset {}'.format(dataset))

        # Make an API call to the Data Portal for the dataset details
        response = requests.get(ckan_url + 'package_show', dict(id=dataset))
        # print(response.text)

        if response.ok:

            # Transform the response so it contains the details we need
            content = response.json().get('result', {})

            if content.get('num_resources', 0) == 0:
                print('There are no resources available to download.')
                continue

            # Make a folder with the name of the dataset for our downloads
            if not os.path.exists(os.path.join(data_dir, dataset)):
                os.mkdir(os.path.join(data_dir, dataset))

            # This variable will help store names of downloads
            download_metadata = list()

            # Iterate through each resource available
            for resource in content.get('resources', []):
                # print(resource)
                # Determine the filename to use for the download
                filename = ''
                if resource.get('url'):
                    filename = resource['url']
                    while '%2' in filename:
                        filename = parse.unquote_plus(filename)
                    filename = os.path.basename(filename)

                else:
                    filename = resource['name']
                    extension = resource['format'].lower()

                    if not filename.lower().endswith(extension):
                        filename = filename + '.' + extension

                # Determine the download link
                download_link = ''
                if resource.get('download_url'):
                    download_link = resource['download_url']
                elif resource.get('url'):
                    download_link = resource['url']
                else:
                    print('No available download link.')
                    continue

                # Download the resource using the new filename to the data directory
                download_response = requests.get(download_link)

                # todo skip completed downloads

                if download_response.ok:
                    print('Downloading {} ({}) to {}'.format(
                        resource['name'], download_link, os.path.join(data_dir, dataset, filename)))

                    with open(os.path.join(data_dir, dataset, filename), 'wb') as w:
                        w.write(download_response.content)

                    download_metadata.append(
                        {
                            filename: {
                                'name': resource['name'],
                                'description': resource.get('resource:description', resource.get('description', '')),
                                'download_link': download_link
                            }
                        }
                    )

                else:
                    print('There was an issue with the download.')

            if download_metadata:
                with open(os.path.join(data_dir, dataset, '_metadata.json'), 'w') as w:
                    w.write(json.dumps(download_metadata, indent=4))

        else:
            print('There was an issue retrieving the dataset.')

else:
    from ._version import __version__