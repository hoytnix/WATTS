import requests
import random
import logging
from typing import List, Optional
from tqdm import tqdm
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_hpxml_form(root: ET.Element) -> str:
	logging.info('Starting HPXML form generation')
	
	def format_label(name: str) -> str:
		"""Convert camelCase/PascalCase to space-separated words."""
		formatted = ''
		for char in name:
			if char.isupper() and formatted:
				formatted += ' '
			formatted += char
		return formatted

	def generate_data_type_input(element_name: str, type_info: ET.Element) -> str:
		logging.debug(f'Generating data type input for {element_name}')
		html = '<div class="data-type-group">'
		html += f'<div class="data-type-header">{format_label(element_name)}</div>'

		# Handle enumerations
		enums = type_info.findall('.//xs:enumeration', {'xs': 'http://www.w3.org/2001/XMLSchema'})
		if enums:
			html += f'<select id="{element_name}" name="{element_name}">'
			for enum in enums:
				val = enum.get('value')
				html += f'<option value="{val}">{format_label(val)}</option>'
			html += '</select>'
		else:
			# Handle other data types
			input_type = "text"
			if 'integer' in type_info.get('name', '') or 'double' in type_info.get('name', ''):
				input_type = "number"
			html += f'<input type="{input_type}" id="{element_name}" name="{element_name}" />'

		html += '</div>'
		return html

	def generate_complex_type(type_name: str, complex_type: ET.Element) -> str:
		logging.debug(f'Generating complex type for {type_name}')
		html = '<div class="complex-type-group">'
		html += f'<div class="complex-type-header">{format_label(type_name)}</div>'

		# Process sequence elements
		sequence = complex_type.find('.//xs:sequence', {'xs': 'http://www.w3.org/2001/XMLSchema'})
		if sequence is not None:
			for element in sequence.findall('.//xs:element', {'xs': 'http://www.w3.org/2001/XMLSchema'}):
				element_name = element.get('name')
				element_type = element.get('type')
				
				if element_name and element_type:
					# Find the type definition
					type_def = root.find(f".//xs:simpleType[@name='{element_type}']", 
									   {'xs': 'http://www.w3.org/2001/XMLSchema'})
					if type_def is not None:
						html += generate_data_type_input(element_name, type_def)
					else:
						# Default to text input if type not found
						html += '<div class="form-group">'
						html += f'<label for="{element_name}">{format_label(element_name)}</label>'
						html += f'<input type="text" id="{element_name}" name="{element_name}" />'
						html += '</div>'

		html += '</div>'
		return html

	# Main form generation
	html_output = '<form id="hpxml-form">'

	# Process complex types
	complex_types = root.findall('.//xs:complexType', {'xs': 'http://www.w3.org/2001/XMLSchema'})
	for complex_type in tqdm(complex_types, desc='Processing complex types'):
		type_name = complex_type.get('name')
		if type_name:
			html_output += generate_complex_type(type_name, complex_type)

	html_output += '</form>'
	logging.info('HPXML form generation completed')
	return html_output

if __name__ == '__main__':
	logging.info('Starting HPXML form generation script')
	
	try:
		# Parse the XSD file
		logging.info('Parsing HPXMLMerged.xsd')
		tree = ET.parse('HPXMLMerged.xsd')
		root = tree.getroot()
		
		# Generate the HTML form
		html_form = generate_hpxml_form(root)
		
		# Write to file
		logging.info('Writing output to hpxml_form.html')
		with open('hpxml_form.html', 'w') as f:
			f.write(html_form)
		
		logging.info('Script completed successfully')
		
	except Exception as e:
		logging.error(f'An error occurred: {str(e)}')
		raise
