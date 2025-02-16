def generate_hpxml_form():
	# Function to convert camelCase/PascalCase to space-separated words
	def format_label(name):
		formatted = ''
		for char in name:
			if char.isupper() and formatted:
				formatted += ' '
			formatted += char
		return formatted

	# Function to generate HTML for a simple type
	def generate_simple_input(element_name, type_info):
		if 'enumeration' in str(type_info):
			# Generate select dropdown for enumerated types
			html = f'<label for="{element_name}">{format_label(element_name)}</label>\n'
			html += f'<select id="{element_name}">\n'
			# Add options based on enumeration values
			for value in type_info.findall('.//xs:enumeration', {'xs': 'http://www.w3.org/2001/XMLSchema'}):
				val = value.get('value')
				html += f'\t<option value="{val}">{format_label(val)}</option>\n'
			html += '</select>\n'
			return html
		elif 'integer' in str(type_info) or 'double' in str(type_info):
			# Generate number input for numeric types
			return f'<label for="{element_name}">{format_label(element_name)}</label>\n<input type="number" id="{element_name}" />\n'
		else:
			# Generate text input for other types
			return f'<label for="{element_name}">{format_label(element_name)}</label>\n<input type="text" id="{element_name}" />\n'

	# Function to generate HTML for a complex type
	def generate_complex_input(element_name, type_info):
		html = f'<div class="section-header">{format_label(element_name)}</div>\n'
		html += '<div class="form-group">\n'
		
		# Process each element in the complex type
		for child in type_info.findall('.//xs:element', {'xs': 'http://www.w3.org/2001/XMLSchema'}):
			child_name = child.get('name')
			if child_name:
				if 'type' in child.attrib:
					child_type = child.get('type')
					html += generate_simple_input(child_name, child_type)
				else:
					# Handle complex child elements recursively
					complex_content = child.find('.//xs:complexContent', {'xs': 'http://www.w3.org/2001/XMLSchema'})
					if complex_content is not None:
						html += generate_complex_input(child_name, complex_content)

		html += '</div>\n'
		return html

	# Main HTML generation
	html_output = ''
	
	# Process root elements
	for element in root.findall('.//xs:element', {'xs': 'http://www.w3.org/2001/XMLSchema'}):
		element_name = element.get('name')
		if element_name:
			complex_type = element.find('.//xs:complexType', {'xs': 'http://www.w3.org/2001/XMLSchema'})
			if complex_type is not None:
				html_output += generate_complex_input(element_name, complex_type)
			else:
				html_output += generate_simple_input(element_name, element)

	return html_output

# Usage
if __name__ == '__main__':
	import xml.etree.ElementTree as ET
	
	# Parse the XSD files
	base_tree = ET.parse('HPXMLBaseElements.xsd')
	data_tree = ET.parse('HPXMLDataTypes.xsd')
	
	# Combine the roots
	root = base_tree.getroot()
	data_root = data_tree.getroot()
	
	# Generate the HTML form
	html_form = generate_hpxml_form()
	
	# Write to file
	with open('hpxml_form.html', 'w') as f:
		f.write(html_form)
