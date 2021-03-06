import os
import datetime
import ssl
import urllib.request
import json

from jinja2 import Environment, select_autoescape, FileSystemLoader

from slugify import slugify

with urllib.request.urlopen("https://api.github.com/repos/paulhtremblay/covid19/contributors") as url:
    contributors = json.loads(url.read().decode())

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

ENV.filters['slugify'] = slugify

def make_about():
    about_page_update = datetime.datetime.utcnow().replace(microsecond=0)
    t = ENV.get_template('about.j2')
    html = t.render(page_title = 'About This Site',
            page_class_attr = ["aboutSite"],
            contributors = contributors,
            about_page_update = about_page_update
            )
    with open(os.path.join('html_temp', 'about'), 'w') as write_obj:
        write_obj.write(html)

if __name__ == '__main__':
    make_about()
