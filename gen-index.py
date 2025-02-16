from jinja2 import Template

# Read the template file
with open('index.html', 'r') as file:
    template_content = file.read()

# Read the form HTML content
with open('form.html', 'r') as file:
    form_html = file.read()

# Create Jinja template
template = Template(template_content)

# Render template with form HTML
output_html = template.render(form_html=form_html)

# Write the result to a new file
with open('index.html', 'w+') as file:
    file.write(output_html)
