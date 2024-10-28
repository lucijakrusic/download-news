import os
import xml.etree.ElementTree as ET
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_text_from_page_xml(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Identify the namespace (if it exists)
    namespaces = {'ns': ''}
    ns_uri = root.tag.split("}")[0].strip("{")
    if ns_uri:
        namespaces['ns'] = ns_uri

    # Extract text from the last Unicode element in each TextRegion
    extracted_text = []
    for text_region in root.findall('.//ns:TextRegion', namespaces):
        unicode_elements = text_region.findall('.//ns:TextEquiv/ns:Unicode', namespaces)
        if unicode_elements:
            # Extract text only from the last Unicode element and strip whitespace
            last_text = unicode_elements[-1].text.strip() if unicode_elements[-1].text else ''
            if last_text:  # Ensure text is not empty
                extracted_text.append(last_text)

    return '\n'.join(extracted_text)  # Single newline to separate regions

def process_page_xml_files(input_folder, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each PAGE XML file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.xml'):
            input_file_path = os.path.join(input_folder, filename)
            output_file_name = filename.replace('.xml', '.txt')
            output_file_path = os.path.join(output_folder, output_file_name)

            # Check if XML file is empty
            if os.path.getsize(input_file_path) == 0:
                logging.info(f'Skipping empty file: {filename}')
                continue

            logging.info(f'Processing file: {filename}')

            # Check if output file already exists
            if not os.path.exists(output_file_path):
                extracted_text = extract_text_from_page_xml(input_file_path)
                if extracted_text:
                    with open(output_file_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(extracted_text)
                    logging.info(f'Created TXT file: {output_file_name}')
                else:
                    logging.info(f'No text extracted from: {filename}')
            else:
                logging.info(f'TXT file already exists: {output_file_name}')



# Usage
input_folder = ''  # Replace with your actual input folder path
output_folder = ''  # Replace with your desired output folder path


process_page_xml_files(input_folder, output_folder)

