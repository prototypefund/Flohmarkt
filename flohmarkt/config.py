import os
import configparser

CONFIGPATH = [
    '/etc/flohmarkt',
    '/etc',
    '.'
]
CONFIGNAME = "flohmarkt.conf"

cfg = configparser.ConfigParser()
found = False
for path in CONFIGPATH:
    cfgfile = os.path.join(path, CONFIGNAME)
    if os.path.exists(cfgfile):
        cfg.read(cfgfile)
        print("Using config in:", cfgfile)
        found = True
        break
if not found:
    raise Error("Could not load config!")
