import requests
import random
from tqdm import tqdm
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# List of reliable free proxies
PROXIES = [
    'http://51.15.242.202:3128',
    'http://51.158.154.173:3128', 
    'http://167.71.5.83:3128',
    'http://51.158.68.133:8811',
    'http://51.158.98.121:8811',
    'http://176.31.69.182:8080',
    'http://51.158.119.88:8811',
    'http://51.158.123.35:8811',
    'http://51.158.172.165:8811',
    'http://51.158.186.242:8811'
]

def get_random_proxy() -> str:
    """Get a random proxy from the proxy list."""
    return random.choice(PROXIES)

def generate_hpxml_form() -> str:
    logging.info('Starting HPXML form generation')
    
    def format_label(name: str) -> str:
        """Convert camelCase/PascalCase to space-separated words."""
        formatted = ''
        for char in name:
            if char.isupper() and formatted:
                formatted += ' '
            formatted += char
        return formatted

    def generate_simple_input(element_name: str, type_info: object) -> str:
        logging.debug(f'Generating simple input for {element_name}')
        if 'enumeration' in str(type_info):
            html = f'<label for="{element_name}">{format_label(element_name)}</label>\n'
            html += f'<select id="{element_name}">\n'
            for value in type_info.findall('.//xs:enumeration', {'xs': 'http://www.w3.org/2001/XMLSchema'}):
                val = value.get('value')
                html += f'\t<option value="{val}">{format_label(val)}</option>\n'
            html += '</select>\n'
            return html
        elif 'integer' in str(type_info) or 'double' in str(type_info):
            return f'<label for="{element_name}">{format_label(element_name)}</label>\n<input type="number" id="{element_name}" />\n'
        else:
            return f'<label for="{element_name}">{format_label(element_name)}</label>\n<input type="text" id="{element_name}" />\n'

    def generate_complex_input(element_name: str, type_info: object, depth: int = 0) -> str:
        logging.debug(f'Generating complex input for {element_name} at depth {depth}')
        html = f'<div class="section-header depth-{depth}">{format_label(element_name)}</div>\n'
        html += f'<div class="form-group">\n'
        
        children = type_info.findall('.//xs:element', {'xs': 'http://www.w3.org/2001/XMLSchema'})
        for i, child in enumerate(tqdm(children, desc=f'Processing {element_name}', leave=False)):
            child_name = child.get('name')
            if child_name:
                if 'type' in child.attrib:
                    child_type = child.get('type')
                    html += generate_simple_input(child_name, child_type)
                else:
                    complex_content = child.find('.//xs:complexContent', {'xs': 'http://www.w3.org/2001/XMLSchema'})
                    if complex_content is not None:
                        html += generate_complex_input(child_name, complex_content, depth + 1)

        html += '</div>\n'
        return html

    logging.info('Processing root elements')
    html_output = ''
    
    root_elements = root.findall('.//xs:element', {'xs': 'http://www.w3.org/2001/XMLSchema'})
    for element in tqdm(root_elements, desc='Processing root elements'):
        element_name = element.get('name')
        if element_name:
            complex_type = element.find('.//xs:complexType', {'xs': 'http://www.w3.org/2001/XMLSchema'})
            if complex_type is not None:
                html_output += generate_complex_input(element_name, complex_type)
            else:
                html_output += generate_simple_input(element_name, element)

    logging.info('HPXML form generation completed')
    return html_output

if __name__ == '__main__':
    import xml.etree.ElementTree as ET
    
    logging.info('Starting HPXML form generation script')
    
    try:
        # Use random proxy for requests
        proxy = get_random_proxy()
        logging.info(f'Using proxy: {proxy}')
        
        # Parse the XSD files
        logging.info('Parsing XSD files')
        base_tree = ET.parse('HPXMLBaseElements.xsd')
        data_tree = ET.parse('HPXMLDataTypes.xsd')
        
        # Combine the roots
        root = base_tree.getroot()
        data_root = data_tree.getroot()
        
        # Generate the HTML form
        html_form = generate_hpxml_form()
        
        # Write to file
        logging.info('Writing output to hpxml_form.html')
        with open('hpxml_form.html', 'w') as f:
            f.write(html_form)
        
        logging.info('Script completed successfully')
        
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        raise
