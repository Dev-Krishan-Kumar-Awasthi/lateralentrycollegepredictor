from jinja2 import Template

# Let's test with a college name containing a single quote, e.g. "St. John's College"
template_str1 = """onclick="openRoutePlanner('{{ name | replace('\\'', '\\\\\\\'') }}')" """
template_str2 = """onclick="openRoutePlanner('{{ name | replace("'","\\\\'") }}')" """

t1 = Template(template_str1)
t2 = Template(template_str2)

name = "St. John's College"
print("T1 Output:", t1.render(name=name))
print("T2 Output:", t2.render(name=name))
