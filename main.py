import os
import csv
import xml.etree.ElementTree as ET
from pyproj import Transformer

def parse_0_txt(file_path):
    """
    Parses the 0.txt file, extracts data from <projection> element,
    and converts projection_x and projection_y to latitude and longitude.
    Returns a dictionary with the extracted data.
    """
    record = {}
    with open(file_path, 'r', encoding='iso-8859-1') as f:
        xml_content = f.read()
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"Error parsing XML in {file_path}: {e}")
            return None

        # Extract data from <projection>
        projection_elem = root.find('projection')
        if projection_elem is not None:
            proj_x = projection_elem.get('x', '')
            proj_y = projection_elem.get('y', '')

            record['projection_x'] = proj_x
            record['projection_y'] = proj_y

            # Convert projection_x and projection_y to latitude and longitude
            try:
                # Convert strings to floats
                easting = float(proj_x)
                northing = float(proj_y)

                # Create a transformer from EPSG:29903 to EPSG:4326
                transformer = Transformer.from_crs("EPSG:29903", "EPSG:4326", always_xy=True)

                # Transform the coordinates
                longitude, latitude = transformer.transform(easting, northing)

                record['latitude'] = latitude
                record['longitude'] = longitude
            except ValueError as ve:
                print(f"Invalid projection coordinates in {file_path}: {ve}")
                record['latitude'] = ''
                record['longitude'] = ''
            except Exception as ex:
                print(f"Error converting coordinates in {file_path}: {ex}")
                record['latitude'] = ''
                record['longitude'] = ''
        else:
            print(f"No <projection> element in {file_path}")
            record['projection_x'] = ''
            record['projection_y'] = ''
            record['latitude'] = ''
            record['longitude'] = ''
    return record

def parse_8_txt(file_path):
    """
    Parses the 8.txt file and extracts data from specified elements.
    Returns a dictionary with the extracted data.
    """
    record = {}
    with open(file_path, 'r', encoding='iso-8859-1') as f:
        xml_content = f.read()
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"Error parsing XML in {file_path}: {e}")
            return None

        # Extract data from specified elements
        elements = [
            ('name', 'name', 'htmlText'),
            ('translation', 'translation', 'htmlText'),
            ('explanation', 'description', 'htmlText'),
        ]
        for elem_name, key_name, attr_name in elements:
            elem = root.find(elem_name)
            if elem is not None:
                record[key_name] = elem.get(attr_name, '')
            else:
                print(f"No <{elem_name}> element in {file_path}")
                record[key_name] = ''
    return record

def process_directory(dirpath):
    """
    Processes a single directory, parses 0.txt and 8.txt, and returns a combined record.
    """
    # Paths to the .txt files
    file_0_txt = os.path.join(dirpath, '0.txt')
    file_8_txt = os.path.join(dirpath, '8.txt')

    # Check if both files exist
    if not os.path.exists(file_0_txt) or not os.path.exists(file_8_txt):
        print(f"Skipping directory {dirpath}: missing 0.txt or 8.txt")
        return None

    # Parse the files
    record_0 = parse_0_txt(file_0_txt)
    record_8 = parse_8_txt(file_8_txt)

    if record_0 is None or record_8 is None:
        print(f"Skipping directory {dirpath}: error parsing files")
        return None

    # Combine the records
    record = {**record_0, **record_8}

    return record

def write_csv(data_list, csv_file, csv_columns):
    """
    Writes the data_list to a CSV file with specified columns.
    """
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in data_list:
                # Write only the specified columns
                filtered_data = {key: data.get(key, '') for key in csv_columns}
                writer.writerow(filtered_data)
        print(f"Data successfully written to {csv_file}")
    except IOError as e:
        print(f"I/O error while writing to {csv_file}: {e}")

def main():
    # Set the root directory where all the folders are located
    root_dir = ''
    # List to store the data
    data_list = []

    # List all immediate subdirectories in root_dir
    for dir_name in os.listdir(root_dir):
        dir_path = os.path.join(root_dir, dir_name)
        if os.path.isdir(dir_path):
            menu_tab_path = os.path.join(dir_path, 'menuTabs')
            if os.path.isdir(menu_tab_path):
                record = process_directory(menu_tab_path)
                if record:
                    data_list.append(record)
            else:
                print(f"Skipping directory {dir_path}: 'menuTab' subdirectory not found")
        else:
            print(f"Skipping {dir_path}: Not a directory")

    csv_columns = [
        'projection_x', 'projection_y',
        'latitude', 'longitude',
        'name', 'translation', 'description'
    ]

    csv_file = 'output.csv'
    write_csv(data_list, csv_file, csv_columns)

if __name__ == '__main__':
    main()
