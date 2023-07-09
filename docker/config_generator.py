#!/usr/bin/python3.11

import os

from jinja2 import Template

CONFIG_TEMPLATE = """
[General]
InstanceName = {{ instance_name }}
ExternalURL = {{ external_url }}
DebugMode = {{ debug_mode }}
JwtSecret = {{ jwt_secret }}
DataPath = {{ data_path }}

[Database]
Server = {{ database_scheme }}://{{ database_user }}:{{ database_password }}@{{ database_host }}:{{ database_port }}/

[SMTP]
Server = {{ smtp_server }}
Port = {{ smtp_port }}
User = {{ smtp_user }}
From = {{ smtp_from }}
Password = {{ smtp_password }}
CAFile = {{ smtp_cafile }}
"""

if __name__ == "__main__":
    data = {
        "instance_name": os.getenv("FLOHMARKT_INSTANCE_NAME", "Fluffy's Flohmarkt"),
        "data_path": os.getenv("FLOHMARKT_DATA_PATH", "/var/lib/flohmarkt"),
        "debug_mode": os.getenv("FLOHMARKT_DEBUG_MODE", "0"),
        "jwt_secret": os.getenv("FLOHMARKT_JWT_SECRET"),
        "external_url": os.getenv("FLOHMARKT_EXTERNAL_URL"),
        "database_scheme": os.getenv("FLOHMARKT_DB_SCHEME"),
        "database_user": os.getenv("FLOHMARKT_DB_USER"),
        "database_password": os.getenv("FLOHMARKT_DB_PASSWORD"),
        "database_host": os.getenv("FLOHMARKT_DB_HOST"),
        "database_port": os.getenv("FLOHMARKT_DB_PORT"),
        "smtp_server": os.getenv("FLOHMARKT_SMTP_SERVER"),
        "smtp_port": os.getenv("FLOHMARKT_SMTP_PORT"),
        "smtp_from": os.getenv("FLOHMARKT_SMTP_FROM"),
        "smtp_user": os.getenv("FLOHMARKT_SMTP_USER"),
        "smtp_password": os.getenv("FLOHMARKT_SMTP_PASSWORD"),
        "smtp_cafile": os.getenv("FLOHMARKT_SMTP_CAFILE"),
    }

    template = Template(CONFIG_TEMPLATE)
    config = template.render(data)

    with open("/dev/stdout", "w") as f:
        f.write(config)
