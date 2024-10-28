import os
from xml.etree import ElementTree as ET
import logging
import shutil


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_xml_file_corrupted(xml_file_path):
    try:
        # Attempt to parse the XML file
        ET.parse(xml_file_path)
        return False  # File is not corrupted
    except ET.ParseError:
        logging.error(f"Parse error: {xml_file_path} is corrupted.")
        return True
    except OSError as e:
        logging.error(f"OSError: {xml_file_path} is corrupted or inaccessible. Error: {e}")
        return True
    except Exception as e:
        logging.error(f"Unexpected error: {xml_file_path} might be corrupted. Error: {e}")
        return True


def extract_text_from_xml(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        logging.error(f"Failed to parse {xml_file_path}: {e}")
        return ""

    namespaces = {'alto': 'http://www.loc.gov/standards/alto/ns-v2#'}
    text_lines = root.findall('.//alto:TextLine', namespaces)

    extracted_text = []
    for line in text_lines:
        strings = line.findall('.//alto:String', namespaces)
        line_text = ' '.join([string.get('CONTENT') for string in strings])
        extracted_text.append(line_text)

    return '\n'.join(extracted_text) 

def process_xml_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.xml'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_name = filename.replace('.xml', '.txt')
            output_file_path = os.path.join(output_folder, output_file_name)

            if os.path.getsize(input_file_path) == 0:
                logging.info(f'Skipping empty file: {filename}')
                continue

            # Check if the file is corrupted
            if is_xml_file_corrupted(input_file_path):
                logging.info(f'Deleting corrupted file: {filename}')
                os.remove(input_file_path)
                continue

            logging.info(f'Processing file: {filename}')

            if not os.path.exists(output_file_path):
                extracted_text = extract_text_from_xml(input_file_path)
                if extracted_text:  # Only write if there is content
                    with open(output_file_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(extracted_text)
                    logging.info(f'Created TXT file: {output_file_name}')
                else:
                    logging.info(f'No text extracted from: {filename}')
            else:
                logging.info(f'TXT file already exists: {output_file_name}')



def merge_txt_files_by_prefix(input_folder, output_folder,  prefix_length=11):

    content_by_prefix = {}


    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            prefix = filename[:prefix_length]
            file_path = os.path.join(input_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if prefix in content_by_prefix:
                    content_by_prefix[prefix] += '\n\n' + content
                else:
                    content_by_prefix[prefix] = content

   
    for prefix, content in content_by_prefix.items():
        merged_file_name = f"{prefix}_merged.txt"
        merged_file_path = os.path.join(output_folder, merged_file_name)


        if not os.path.exists(merged_file_path):
            with open(merged_file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            logging.info(f'Created merged TXT file: {merged_file_name}')
        else:
            logging.info(f'Merged TXT file already exists: {merged_file_name}')

# the function was necessary because the previous one saved the merged files in the input rather than in a new folder by mistake
def move_merged_files(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through the files in the input folder
    for filename in os.listdir(input_folder):
        if "_merged" in filename and filename.endswith('.txt'):
            # Construct full file paths
            source_path = os.path.join(input_folder, filename)
            destination_path = os.path.join(output_folder, filename)

            # Move the file to the output folder
            shutil.move(source_path, destination_path)
            logging.info(f'Moved file: {filename} to {output_folder}')




input_folder = 'E:/aze_txt'  
output_folder =  'E:/aze_merged'  

#process_xml_files(input_folder, output_folder)
merge_txt_files_by_prefix(input_folder, output_folder)
#move_merged_files(input_folder, output_folder)