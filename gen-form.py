import xml.etree.ElementTree as ET
import re

def parse_xsd(xsd_file):
    tree = ET.parse(xsd_file)
    root = tree.getroot()
    return root

def generate_form():
    # Parse XSD files
    hpxml_root = parse_xsd('HPXML.xsd')
    base_root = parse_xsd('BaseElements.xsd')
    types_root = parse_xsd('DataTypes.xsd')
    
    # Extract namespace
    ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    
    # Generate form HTML
    form_html = '''
    <form id="hpxml-form" class="container mt-4">
        <div class="accordion" id="hpxmlAccordion">
    '''
    
    # Process main HPXML elements (Categories)
    hpxml_element = hpxml_root.find('.//xs:element[@name="HPXML"]', ns)
    if hpxml_element is not None:
        complex_type = hpxml_element.find('.//xs:sequence', ns)
        if complex_type is not None:
            for idx, element in enumerate(complex_type.findall('xs:element', ns)):
                category_name = element.get('name')
                form_html += f'''
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading{idx}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                                data-bs-target="#collapse{idx}" aria-expanded="false" aria-controls="collapse{idx}">
                            <i class="bi bi-folder me-2"></i> {category_name}
                        </button>
                    </h2>
                    <div id="collapse{idx}" class="accordion-collapse collapse" 
                         aria-labelledby="heading{idx}" data-bs-parent="#hpxmlAccordion">
                        <div class="accordion-body">
                '''
                
                # Find corresponding base element
                base_element = base_root.find(f'.//xs:element[@name="{category_name}"]', ns)
                if base_element is not None:
                    complex_type = base_element.find('.//xs:sequence', ns)
                    if complex_type is not None:
                        form_html += '<div class="row g-3">'
                        for field in complex_type.findall('.//xs:element', ns):
                            field_name = field.get('name')
                            field_type = field.get('type')
                            
                            # Find data type in DataTypes.xsd
                            type_info = types_root.find(f'.//xs:simpleType[@name="{field_type}_simple"]', ns)
                            
                            if type_info is not None:
                                restriction = type_info.find('.//xs:restriction', ns)
                                if restriction is not None:
                                    # Handle enumeration
                                    enums = restriction.findall('xs:enumeration', ns)
                                    if enums:
                                        form_html += f'''
                                        <div class="col-md-6">
                                            <label for="{field_name}" class="form-label">{field_name}</label>
                                            <select class="form-select" id="{field_name}" name="{field_name}">
                                                <option value="">Select {field_name}</option>
                                        '''
                                        for enum in enums:
                                            value = enum.get('value')
                                            form_html += f'<option value="{value}">{value}</option>'
                                        form_html += '''
                                            </select>
                                        </div>
                                        '''
                                    else:
                                        # Handle other types
                                        base = restriction.get('base')
                                        input_type = 'text'
                                        if base == 'xs:integer' or base == 'xs:double':
                                            input_type = 'number'
                                        elif base == 'xs:date':
                                            input_type = 'date'
                                        elif base == 'xs:boolean':
                                            input_type = 'checkbox'
                                            
                                        form_html += f'''
                                        <div class="col-md-6">
                                            <label for="{field_name}" class="form-label">{field_name}</label>
                                            <input type="{input_type}" class="form-control" id="{field_name}" name="{field_name}">
                                        </div>
                                        '''
                            else:
                                # Default to text input if type not found
                                form_html += f'''
                                <div class="col-md-6">
                                    <label for="{field_name}" class="form-label">{field_name}</label>
                                    <input type="text" class="form-control" id="{field_name}" name="{field_name}">
                                </div>
                                '''
                        form_html += '</div>'
                
                form_html += '''
                        </div>
                    </div>
                </div>
                '''
    
    form_html += '''
        </div>
        <div class="mt-4 mb-4">
            <button type="submit" class="btn btn-primary">Submit</button>
        </div>
    </form>
    '''
    
    # Write to output file
    with open('form.html', 'w+') as f:
        f.write(form_html)

if __name__ == '__main__':
    generate_form()