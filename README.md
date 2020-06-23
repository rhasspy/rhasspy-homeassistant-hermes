# Rhasspy Home Assistant Hermes

[![Continous Integration](https://github.com/rhasspy/rhasspy-homeassistant-hermes/workflows/Tests/badge.svg)](https://github.com/rhasspy/rhasspy-homeassistant-hermes/actions)
[![GitHub license](https://img.shields.io/github/license/rhasspy/rhasspy-homeassistant-hermes.svg)](https://github.com/rhasspy/rhasspy-homeassistant-hermes/blob/master/LICENSE)

Handles intents using [Home Assistant](https://www.home-assistant.io/) and [Hass.io](https://www.home-assistant.io/hassio/)

## Requirements

* Python 3.7

## Installation

```bash
$ git clone https://github.com/rhasspy/rhasspy-homeassistant-hermes
$ cd rhasspy-homeassistant-hermes
$ ./configure
$ make
$ make install
```

## Deployment

```bash
$ make dist
```

See `dist/` directory for `.tar.gz` file.

## Running

```bash
$ bin/rhasspy-homeassistant-hermes <ARGS>
```

## Command-Line Options

```
usage: rhasspy-homeassistant-hermes [-h] --url URL
                                    [--access-token ACCESS_TOKEN]
                                    [--api-password API_PASSWORD]
                                    [--handle-type {event,intent}]
                                    [--event-type-format EVENT_TYPE_FORMAT]
                                    [--certfile CERTFILE] [--keyfile KEYFILE]
                                    [--host HOST] [--port PORT]
                                    [--username USERNAME]
                                    [--password PASSWORD] [--tls]
                                    [--tls-ca-certs TLS_CA_CERTS]
                                    [--tls-certfile TLS_CERTFILE]
                                    [--tls-keyfile TLS_KEYFILE]
                                    [--tls-cert-reqs {CERT_REQUIRED,CERT_OPTIONAL,CERT_NONE}]
                                    [--tls-version TLS_VERSION]
                                    [--tls-ciphers TLS_CIPHERS]
                                    [--site-id SITE_ID] [--debug]
                                    [--log-format LOG_FORMAT]

optional arguments:
  -h, --help            show this help message and exit
  --url URL             URL of Home Assistant server
  --access-token ACCESS_TOKEN
                        Long-lived access token (Authorization)
  --api-password API_PASSWORD
                        API password (X-HA-Access, deprecated)
  --handle-type {event,intent}
                        Use Home Assistant events or intent API
  --event-type-format EVENT_TYPE_FORMAT
                        Format string for event types
  --certfile CERTFILE   SSL certificate file
  --keyfile KEYFILE     SSL private key file (optional)
  --host HOST           MQTT host (default: localhost)
  --port PORT           MQTT port (default: 1883)
  --username USERNAME   MQTT username
  --password PASSWORD   MQTT password
  --tls                 Enable MQTT TLS
  --tls-ca-certs TLS_CA_CERTS
                        MQTT TLS Certificate Authority certificate files
  --tls-certfile TLS_CERTFILE
                        MQTT TLS certificate file (PEM)
  --tls-keyfile TLS_KEYFILE
                        MQTT TLS key file (PEM)
  --tls-cert-reqs {CERT_REQUIRED,CERT_OPTIONAL,CERT_NONE}
                        MQTT TLS certificate requirements (default:
                        CERT_REQUIRED)
  --tls-version TLS_VERSION
                        MQTT TLS version (default: highest)
  --tls-ciphers TLS_CIPHERS
                        MQTT TLS ciphers to use
  --site-id SITE_ID     Hermes site id(s) to listen for (default: all)
  --debug               Print DEBUG messages to the console
  --log-format LOG_FORMAT
                        Python logger format
```
