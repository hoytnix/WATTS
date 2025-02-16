import xml.etree.ElementTree as ET
import html

def parse_schema(xsd_file):
    tree = ET.parse(xsd_file)
    root = tree.getroot()
    namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    return root, namespace

def get_simple_type_info(simple_type):
    namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}
    restrictions = simple_type.find('.//xs:restriction', namespace)
    if restrictions is None:
        return "text", []
    
    base = restrictions.get('base', '').split(':')[-1]
    enums = restrictions.findall('.//xs:enumeration', namespace)
    
    if enums:
        return "select", [e.get('value') for e in enums]
    elif base in ['string']:
        return "text", []
    elif base in ['integer', 'double', 'decimal']:
        return "number", []
    elif base in ['boolean']:
        return "checkbox", []
    elif base in ['date']:
        return "date", []
    return "text", []

def generate_html():
    # Parse all schema files
    hpxml_root, ns = parse_schema('HPXML.xsd')
    types_root, _ = parse_schema('DataTypes.xsd')
    base_root, _ = parse_schema('BaseElements.xsd')

    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>HPXML Form</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .form-section { margin-bottom: 2rem; }
        .card { margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">HPXML Data Entry Form</h1>
        <form id="hpxmlForm">'''

    # Process main categories from HPXML.xsd
    for element in hpxml_root.findall('.//xs:element', ns):
        name = element.get('name')
        if name and name != 'HPXML':
            html_content += f'''
            <div class="card form-section">
                <div class="card-header">
                    <h3>{name}</h3>
                </div>
                <div class="card-body">'''
            
            # Process type definitions from DataTypes.xsd
            complex_type = element.find('.//xs:complexType', ns)
            if complex_type is not None:
                for sub_element in complex_type.findall('.//xs:element', ns):
                    sub_name = sub_element.get('name', '')
                    type_name = sub_element.get('type', '').split(':')[-1]
                    
                    # Find corresponding simple type in DataTypes.xsd
                    simple_type = types_root.find(f'.//xs:simpleType[@name="{type_name}_simple"]', ns)
                    if simple_type is not None:
                        input_type, options = get_simple_type_info(simple_type)
                        
                        if input_type == "select":
                            html_content += f'''
                            <div class="mb-3">
                                <label for="{html.escape(sub_name)}" class="form-label">{html.escape(sub_name)}</label>
                                <select class="form-select" id="{html.escape(sub_name)}" name="{html.escape(sub_name)}">
                                    <option value="">Select...</option>'''
                            for option in options:
                                html_content += f'''
                                    <option value="{html.escape(option)}">{html.escape(option)}</option>'''
                            html_content += '''
                                </select>
                            </div>'''
                        else:
                            html_content += f'''
                            <div class="mb-3">
                                <label for="{html.escape(sub_name)}" class="form-label">{html.escape(sub_name)}</label>
                                <input type="{input_type}" class="form-control" id="{html.escape(sub_name)}" name="{html.escape(sub_name)}">
                            </div>'''
            
            html_content += '''
                </div>
            </div>'''

    html_content += '''
            <button type="submit" class="btn btn-primary">Generate HPXML</button>
        </form>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('hpxmlForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            console.log('Form data:', data);
            // Here you can add code to generate HPXML
        });
    </script>
</body>
</html>'''

    with open('form.html', 'w+') as f:
        f.write(html_content)

if __name__ == '__main__':
    generate_html()