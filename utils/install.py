#/usr/bin/env python
import os
import shutil
from jinja2 import Environment, FileSystemLoader
from settings.config import config


def install_template(infile="nginx-api.conf.template", outfile="nginx-api.conf"):
    '''
    load template from settings/templates
    create conf file by:
    - injecting values that are loaded from settings directory of the project
    - injecting values defined by user in "settings.json"
    write back into conf for debug 
    copy into correct filesystem location
    '''    
    # try:
    template_dir = os.path.join(config["ENVIRONNEMENT"]["conf"], "templates")
    env = Environment(loader = FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    # if config["SSL"]["activate"] is False and "nginx" in infile:
    #     infile = infile.replace("nginx-", 'nginx-nossl-')
    #     outfile = outfile.replace("nginx-", 'nginx-nossl-')
    
    template = env.get_template(infile)
    new_conf = template.render(**config)
    
    service,name_f = outfile.split("-")
    conf_file = os.path.join(config["ENVIRONNEMENT"]["conf"], name_f)
    with open(conf_file, "w") as f:
        f.write(new_conf)

    if service == "nginx":
        shutil.copy2(conf_file, os.path.join("/etc/nginx/sites-available/",name_f))
        shutil.copy2(conf_file, os.path.join("/etc/nginx/sites-enabled/",name_f))
    elif service == "supervisor":
        shutil.copy2(conf_file, os.path.join("/etc/supervisor/conf.d/",name_f))
    elif service == "front":
        shutil.copy2(conf_file, os.path.join(config["FRONT"]["dir"],"src", name_f))
    else:
        pass

def deploy_webapps():
    conf_templates = os.path.join(config["ENVIRONNEMENT"]["conf"], "templates")
    #setting nginx and supervisord for API 
    # and main.js for front
    ssl = config["SSL"]["activate"]
    candidates = [tpf for tpf in os.listdir(conf_templates) if tpf.endswith('.template')]
    
    for template_f in candidates:
        _f = template_f.replace('.template', '')    
        install_template(template_f,_f)

    
if __name__ == '__main__':
    deploy_webapps()
