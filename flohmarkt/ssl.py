import ssl
import os

from flohmarkt.config import cfg

if os.path.exists(cfg["SMTP"]["CAFile"]):
    ssl_context = ssl.create_default_context(cafile=cfg["SMTP"]["CAFile"])
else:
    ssl_context = ssl.create_default_context()

if int(cfg["General"]["DebugMode"]) > 0:
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

