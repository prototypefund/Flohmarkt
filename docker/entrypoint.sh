#!/usr/bin/env bash

# generate config file
mkdir -p /etc/flohmarkt
python3 /config_generator.py > /etc/flohmarkt/flohmarkt.conf
echo "config generated, sha256: `sha256sum /etc/flohmarkt/flohmarkt.conf`"

case "$1" in
    "web")
        uvicorn --host 0.0.0.0 --port 8000 flohmarkt:app
        ;;
    "initdb")
        python3 initialize_couchdb.py ${FLOHMARKT_DB_PASSWORD} ${FLOHMARKT_DB_PASSWORD}
        ;;
    *)
        echo "Nothing to see here, move along!"
        echo "Seriously, though. This is a multipurpose image and accepts"
        echo "the following commands:"
        echo "  * web: run the web server"
        echo "  * background: run the background service"
        echo "  * initdb: run the db initialization script."
        ;;
esac
