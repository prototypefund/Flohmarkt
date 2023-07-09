# flohmarkt-docker

## Commands

| Command | Description |
| ------- | ----------- |
| web | Run the web server, requires and initialized couchdb instance |
| background | Run the background service |
| initdb | Initialize the database |

## Environment Variables

| Variable Name | Required | Default Value | Description | 
| ------------- | -------- | ------------- | ----------- |
| `FLOHMARKT_INSTANCE_NAME` | No | `"Fluffy's Flohmarkt"` | Instance name | 
| `FLOHMARKT_DATA_PATH` | No | `"/var/lib/flohmarkt"` | Path for flohmarkt data, e.g. images | 
| `FLOHMARKT_DEBUG_MODE` | No | `"1"` | Debug Mode setting, `"0"` = disabled, `"1"` = enabled |
| `FLOHMARKT_JWT_SECRET` | Yes | - | Secret used for deriving JWK. Used for securing user sessions. This should not change once the instance is fedeated | 
| `FLOHMARKT_EXTERNAL_URL` | Yes | - | External URL of the flohmarkt instance | 
| `FLOHMARKT_DB_SCHEME` | Yes | - | Scheme portion of the database connection string, usually `http` or `https` | 
| `FLOHMARKT_DB_USER` | Yes | - | Scheme portion of the database connection string. Should be `admin` | 
| `FLOHMARKT_DB_PASSWORD` | Yes | - | Password for connecting to the database | 
| `FLOHMARKT_DB_HOST` | Yes | - | Host portion of the database connection string | 
| `FLOHMARKT_DB_PORT` | Yes | - | Port portion of the database connection string | 
| `FLOHMARKT_SMTP_SERVER` | Yes | - | address of the SMTP server used for sending notification emails |
| `FLOHMARKT_SMTP_PORT` | Yes | - | port of the SMTP server used for sending notification emails |
| `FLOHMARKT_SMTP_USER` | Yes | - | username used for connecting to the SMTP server |
| `FLOHMARKT_SMTP_FROM` | Yes | - | From address used for sending emails. |
| `FLOHMARKT_SMTP_PASSWORD` | Yes | - | password used for connecting to the SMTP server |
| `FLOHMARKT_SMTP_CAFILE` | Yes | - | CA file used for connecting to the SMTP server in case STARTTLS is enabled |

# How to build

* Build for your platform: `docker build -t flohmarkt:latest .`
* Cross-build for arm64: `docker buildx build --platform arm64 flohmarkt:latest .`

