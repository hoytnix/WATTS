import xml.etree.ElementTree as ET
import html
from tqdm import tqdm

def parse_xsd(filepath):
    tree = ET.parse(filepath)
    return tree.getroot()

def generate_form():
    # Parse the XSD files
    hpxml_root = parse_xsd('HPXMLMerged.xsd')
    data_types_root = parse_xsd('DataTypes.xsd')
    base_elements_root = parse_xsd('BaseElements.xsd')
    
    # Extract namespaces
    ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    
    # Generate tabs for main categories
    tabs_html = '<ul class="nav nav-tabs" role="tablist">\n'
    panels_html = '<div class="tab-content p-3">\n'
    
    # Process main HPXML elements (categories)
    for i, elem in enumerate(tqdm(hpxml_root.findall(".//xs:element", ns), desc="Generating Form")):
        name = elem.get('name', '')
        if not name:
            continue
            
        # Generate tab
        active = 'active' if i == 0 else ''
        tab_id = f"tab-{name}"
        
        tabs_html += f'''
        <li class="nav-item" role="presentation">
            <button class="nav-link {active}" id="{tab_id}" data-bs-toggle="tab" 
                    data-bs-target="#panel-{name}" type="button" role="tab">
                {name}
            </button>
        </li>'''
        
        # Generate panel content
        panels_html += f'''
        <div class="tab-pane fade {'show ' if i == 0 else ''}{active}" 
             id="panel-{name}" role="tabpanel" tabindex="0">
            <div class="mb-3">
                <form class="needs-validation" novalidate>'''
        
        # Find complexType definition for this element
        type_name = elem.tag.split('}')[1]  # Get the tag name without the namespace
        if type_name:
            # Find the complexType definition in base_elements_root
            for type_def in base_elements_root.findall(f".//xs:complexType[@name='{type_name}']", ns):
                panels_html += process_complexType(type_def, ns, data_types_root)
                
        panels_html += '''
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            </div>
        </div>'''
    
    tabs_html += '</ul>\n'
    panels_html += '</div>\n'
    
    # Combine all HTML
    form_html = f'''
    <div class="container mt-4">
        {tabs_html}
        {panels_html}
    </div>
    '''
    
    return form_html

def process_complexType(type_def, ns, data_types_root):
    html = ''
    for base_elem in type_def.findall(".//xs:element", ns):
        # Discover the type of the element
        data_type = base_elem.get('type', '')
        if data_type:
            type_def = data_types_root.find(f".//xs:simpleType[@name='{data_type}']", ns)
            if type_def is not None:
                input_type = "text"  # default
                if "Date" in data_type:
                    input_type = "date"
                elif "Boolean" in data_type:
                    input_type = "checkbox"
                elif "Number" in data_type or "Integer" in data_type:
                    input_type = "number"
                elif "String" in data_type:
                    input_type = "text"
                
                html += f'''
                <div class="mb-3">
                    <label for="{base_elem.get('name')}" class="form-label">{base_elem.get('name')}</label>
                    <input type="{input_type}" class="form-control" 
                           id="{base_elem.get('name')}" name="{base_elem.get('name')}" required>
                    <div class="invalid-feedback">
                        Please provide a valid {base_elem.get('name')}.
                    </div>
                </div>'''
        
        # Recursively process nested complexTypes
        for nested_type_def in base_elem.findall(".//xs:complexType", ns):
            html += process_complexType(nested_type_def, ns, data_types_root)
    return html

if __name__ == "__main__":
    with open('form.html', 'w') as f:
        f.write(generate_form())