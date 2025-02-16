import xml.etree.ElementTree as ET
from typing import Dict
import os

def parse_xsd_schema(file_path: str, namespace: str) -> Dict:
    tree = ET.parse(file_path)
    root = tree.getroot()
    schema = {}
    
    ns = {'xs': 'http://www.w3.org/2001/XMLSchema', 
          'ns': namespace}
    
    for complex_type in root.findall('.//xs:complexType', ns):
        name = complex_type.get('name', '')
        if name:
            schema[name] = {
                'type': 'complex',
                'elements': []
            }
            
            for seq in complex_type.findall('.//xs:sequence', ns):
                for elem in seq.findall('xs:element', ns):
                    elem_info = {
                        'name': elem.get('name', ''),
                        'type': elem.get('type', ''),
                        'minOccurs': elem.get('minOccurs', '1'),
                        'maxOccurs': elem.get('maxOccurs', '1')
                    }
                    schema[name]['elements'].append(elem_info)
    
    return schema

def generate_html():
    hpxml_schema = parse_xsd_schema('HPXML.xsd', 'http://hpxmlonline.com/2023/09')
    datatypes_schema = parse_xsd_schema('DataTypes.xsd', 'http://hpxmlonline.com/2023/09')
    elements_schema = parse_xsd_schema('BaseElements.xsd', 'http://hpxmlonline.com/2023/09')
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>HPXML Form Generator</title>
    <style>
        .tab { display: none; }
        .tab.active { display: block; }
        .tab-buttons button { padding: 10px; margin: 5px; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; }
        body { padding: 20px; font-family: Arial, sans-serif; }
    </style>
</head>
<body>
    <h1>HPXML Form Generator</h1>
    
    <div class="tab-buttons">
"""
    
    # Add tab buttons
    for category in hpxml_schema:
        html_content += f'        <button onclick="showTab(\'{category}\')">{category}</button>\n'
    
    html_content += """    </div>

    <form id="hpxmlForm" onsubmit="generateXML(event)">
"""
    
    # Add form fields
    for category, details in hpxml_schema.items():
        html_content += f'        <div id="{category}" class="tab">\n'
        html_content += f'            <h2>{category}</h2>\n'
        if details.get('elements'):
            for elem in details['elements']:
                html_content += f'            <div class="form-group">\n'
                html_content += f'                <label for="{elem["name"]}">{elem["name"]}</label>\n'
                elem_type = elem['type'].replace('ns:', '')
                if elem_type in datatypes_schema:
                    if 'string' in str(datatypes_schema[elem_type]):
                        html_content += f'                <input type="text" id="{elem["name"]}" name="{elem["name"]}">\n'
                    elif 'integer' in str(datatypes_schema[elem_type]):
                        html_content += f'                <input type="number" id="{elem["name"]}" name="{elem["name"]}" step="1">\n'
                    elif 'double' in str(datatypes_schema[elem_type]):
                        html_content += f'                <input type="number" id="{elem["name"]}" name="{elem["name"]}" step="0.01">\n'
                    elif 'boolean' in str(datatypes_schema[elem_type]):
                        html_content += f'                <input type="checkbox" id="{elem["name"]}" name="{elem["name"]}">\n'
                    elif 'date' in str(datatypes_schema[elem_type]):
                        html_content += f'                <input type="date" id="{elem["name"]}" name="{elem["name"]}">\n'
                    else:
                        html_content += f'                <input type="text" id="{elem["name"]}" name="{elem["name"]}">\n'
                html_content += '            </div>\n'
        html_content += '        </div>\n'
    
    html_content += """        <button type="submit">Generate HPXML</button>
    </form>

    <script>
        function showTab(tabId) {
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabId).classList.add('active');
        }
        
        function generateXML(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            let xmlContent = '<?xml version="1.0" encoding="UTF-8"?>\n<HPXML xmlns="http://hpxmlonline.com/2023/09">\n';
            
            for (let [name, value] of formData.entries()) {
                if (value) {
                    xmlContent += `  <${name}>${value}</${name}>\n`;
                }
            }
            
            xmlContent += '</HPXML>';
            
            const blob = new Blob([xmlContent], { type: 'text/xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'output.xml';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        // Show first tab by default
        document.querySelector('.tab').classList.add('active');
    </script>
</body>
</html>
"""
    
    with open('form.html', 'w+') as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_html()
    print("Form generated as form.html")