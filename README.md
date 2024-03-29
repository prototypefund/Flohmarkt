# flohmarkt

A decentral federated small trade platform

## Service compatibility chart

Server Applications
| Service      | Version             | Remote-Interact button | URL copying | Conversation | Following | Comment         |
|--------------|---------------------|------------------------|-------------|--------------|-----------|-------------------|
| Mastodon     |  4.1.4              | [x]                    | [x]         |     [x]      | [x]        |            |
| Firefish     | 1.0.4-beta          | [x]                    | [x]         |     [x]      | [x]        |            |
| Calckey       |  14.0.0-rc3           | [?]                    | [? ]         |     [x ]      | [?]        |   |
| Misskey       |  N/A           | [ x ]                    | [ x ]         |     [x ]      | [ x ]        | cant load avatars from flohmarkt side  |
| Pixelfed       |  ???              | [ ]                    | [x]         |     [ ]      | [x]        | The software does not supply oauth url template for remote-interact. also cannot send private messages, so no conversations  |
| Lemmy          |  0.18.2           | [ ]                    | [ ]         |     [ ]      | [ ]        | Doesnt work at all. I don't even see requests from lemmy at my side. |
| Peertube       |  5.2.0           | [ ]                    | [ ]         |     [ ]      | [ ]        | Can't display Notes. |
| Friendica       |  N/A           | [ ]                    | [x]         |     [x]      | [x]        | Works only wirth 3rd party clients. The webapp itself can't send direct messages. |
| Pleroma      | 2.5.2    | [  ]                    | [ ]         |     [x ]      | [x ]        |            |
| Mammuthus      | ?????  | [ ]                    | [ ]         |     [ ]      | [ ]        |         problems getting pubkeys from users   |
| Mitra      | ?????  | [ ]                    | [ ]         |     [ ]      | [ ]        |             |
| [microblog.pub](https://docs.microblog.pub/) | 2.0.0+ynh1 | [ ]                    | [ ]         |     [ ]      | [ ]        | lookup for users and notes fails, [issue](https://codeberg.org/grindhold/flohmarkt/issues/109) |

Client Applications
(We don't support C2S. It's just about interacting through other services.)
| Service      | Version             | Remote-Interact button | URL copying | Conversation | Following | Comment         |
|--------------|---------------------|------------------------|-------------|--------------|-----------|-------------------|
| Akkoma       |  ????               | [ ]                    | [ ]         |     [ ]      | [x]        |            |

## Public Instances

Known public instances are listed in the [instances.md](instances.md) file

## Dependencies

- python3-aiohttp
- python3-aiosmtplib
- python3-email-validator
- python3-jwt
- python3-pycryptodome
- python3-fastapi
- python3-multipart
- python3-haversine
- python3-websockets
- uvicorn

## Install

### Nix

Use the nix flake and the contained flohmarkt nixos module in order to set up your service

### Docker

1. find a good location and clone the repo

```shell
git clone https://codeberg.org/grindhold/flohmarkt.git
```

#### Development

2. rename the docker-compose.yml

```shell
mv docker-compose_dev.yaml docker-compose.yaml
```

3. start the docker container

```shell
docker compose up
```

#### Productive

2. rename env file

```shell
cp example.env .env
```

3. create secret

```shell
echo "FLOHMARKT_JWT_SECRET=$(openssl rand 256 | base64 -w 0)" >> .env
```

4. edit the other variables in .env

```shell
nano .env
```

5. rename the docker-compose.yml

```shell
cp docker-compose_prod.yaml docker-compose.yaml
```

6. start the docker container

```shell
docker compose up
```

You will be able to reach your flohmarkt instance at `http://localhost:8000`. Any mails
that the system sends will be dumped to a mailhog at `http://localhost:8025`.

### Plain

0. Install the dependencies
1. Make sure a couchdb server is ready and you have the admin password
   For installing couchdb on ubuntu, consult this howto:
   https://www.vultr.com/docs/install-an-apache-couchdb-database-server-on-ubuntu-20-04/
2. Make sure you have access to a SMTP server and the credentials to a user account on it.
3. Copy the `flohmarkt.conf.example` to `flohmarkt.conf` and edit it to fit your environment.
4. Run the database initialization script `$ python3 initialize_couchdb.py
   <couchdb_admin_pw> <couchdb_user_pw>`
5. Run the webserver `uvicorn --host 127.0.0.1 --port 8000 --reload`

You will be able to reach your flohmarkt instance at `http://localhost:8000`.

## Initial Setup

Whichever setup method you choose, you will have to setup your instance after running it for
the first time. On the console, the application will print a link to the instance setup.
E.g. under docker-compose it will look like this:

```
flohmarkt-web-1       | INFO:     Application startup complete.
flohmarkt-web-1       | Flohmarkt is not initialized yet. Please go to
flohmarkt-web-1       |             http://localhost:8000/setup/23196062-8b7d-4b3f-a89d-aef2ff58ec63
flohmarkt-web-1       |             in order to complete the setup process
```

Follow the link and set up your admin account and instance.

## Troubleshooting

  * Registration route is hanging
    Your Mailserver settings are most likely incorrect
  * I can't access my admin account
    Maybe the Initial Setup process failed. Forgot to click a point on the map maybe?
    You can always restart your instance and click the setup link again.

## License

This project is licensed under the GNU Affero General Public License 3.

