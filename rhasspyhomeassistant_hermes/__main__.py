"""Hermes MQTT service for rhasspy homeassistant"""
import argparse
import logging

import paho.mqtt.client as mqtt

from . import HomeAssistantHermesMqtt

_LOGGER = logging.getLogger(__name__)


def main():
    """Main method."""
    parser = argparse.ArgumentParser(prog="rhasspy-homeassistant-hermes")
    parser.add_argument("--url", required=True, help="URL of Home Assistant server")
    parser.add_argument(
        "--access-token", help="Long-lived access token (Authorization)"
    )
    parser.add_argument("--api-password", help="API password (X-HA-Access, deprecated)")
    parser.add_argument(
        "--handle-type",
        choices=["event", "intent"],
        default="event",
        help="Use Home Assistant events or intent API",
    )
    parser.add_argument(
        "--event-type-format",
        default="rhasspy_{0}",
        help="Format string for event types",
    )
    parser.add_argument(
        "--pem-file", help="Path to PEM file for self-signed certificates"
    )
    parser.add_argument(
        "--host", default="localhost", help="MQTT host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=1883, help="MQTT port (default: 1883)"
    )
    parser.add_argument(
        "--siteId",
        action="append",
        help="Hermes siteId(s) to listen for (default: all)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print DEBUG messages to the console"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    _LOGGER.debug(args)

    try:
        # Listen for messages
        client = mqtt.Client()
        hermes = HomeAssistantHermesMqtt(
            client,
            url=args.url,
            access_token=args.access_token,
            api_password=args.api_password,
            event_type_format=args.event_type_format,
            pem_file=args.pem_file,
            handle_type=args.handle_type,
            siteIds=args.siteId,
        )

        def on_disconnect(client, userdata, flags, rc):
            try:
                # Automatically reconnect
                _LOGGER.info("Disconnected. Trying to reconnect...")
                client.reconnect()
            except Exception:
                logging.exception("on_disconnect")

        # Connect
        client.on_connect = hermes.on_connect
        client.on_disconnect = on_disconnect
        client.on_message = hermes.on_message

        _LOGGER.debug("Connecting to %s:%s", args.host, args.port)
        client.connect(args.host, args.port)

        client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _LOGGER.debug("Shutting down")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
