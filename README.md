# flohmarkt

A decentral federated small trade platform

## Service compatibility chart

Server Applications
| Service      | Version             | Remote-Interact button | URL copying | Conversation | Following | Comment         |
|--------------|---------------------|------------------------|-------------|--------------|-----------|-------------------|
| Mastodon     |  4.1.4              | [x]                    | [x]         |     [x]      | [x]        |            |
| Firefish     | 1.0.4-beta          | [x]                    | [x]         |     [x]      | [x]        |            |
| Pixelfed       |  ???              | [ ]                    | [x]         |     [ ]      | [x]        | The software does not supply oauth url template for remote-interact. also cannot send private messages, so no conversations  | 
| Lemmy          |  0.18.2           | [ ]                    | [ ]         |     [ ]      | [ ]        | Doesnt work at all. I don't even see requests from lemmy at my side. |
| Peertube       |  5.2.0           | [ ]                    | [ ]         |     [ ]      | [ ]        | Can't display Notes. |
| Friendica       |  N/A           | [ ]                    | [x]         |     [ ]      | [x]        | Can't display Notes. |
| Calckey       |  N/A           | [ ]                    | [  ]         |     [ ]      | [  ]        | The common problem is that my server cant connect to calckey URLs  |
| Pleroma      | ?????  | [ ]                    | [ ]         |     [ ]      | [ ]        |            |
| Mammuthus      | ?????  | [ ]                    | [ ]         |     [ ]      | [ ]        |         problems getting pubkeys from users   |
| Mitra      | ?????  | [ ]                    | [ ]         |     [ ]      | [ ]        |             |

Client Applications
(We don't support C2S. It's just about interacting through other services.)
| Service      | Version             | Remote-Interact button | URL copying | Conversation | Following | Comment         |
|--------------|---------------------|------------------------|-------------|--------------|-----------|-------------------|
| Akkoma       |  ????               | [ ]                    | [ ]         |     [ ]      | [x]        |            |
## Dependencies

- python3-aiohttp
- python3-email-validator
- python3-jwt
- python3-pycryptodome
- python3-fastapi
- python3-multipart
- uvicorn

## Run

`uvicorn flohmarkt:app`

## Installing on Ubuntu / Debian

You can get couchdb according to this howto:

https://www.vultr.com/docs/install-an-apache-couchdb-database-server-on-ubuntu-20-04/

## License

This project is licensed under the GNU Affero General Public License 3.

