"""Hermes MQTT service for rhasspy homeassistant"""
import argparse
import asyncio
import logging

import paho.mqtt.client as mqtt

from . import HomeAssistantHermesMqtt

_LOGGER = logging.getLogger("rhasspyhomeassistant_hermes")

# -----------------------------------------------------------------------------


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
    parser.add_argument("--certfile", help="SSL certificate file")
    parser.add_argument("--keyfile", help="SSL private key file (optional)")
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
    parser.add_argument(
        "--log-format",
        default="[%(levelname)s:%(asctime)s] %(name)s: %(message)s",
        help="Python logger format",
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=args.log_format)
    else:
        logging.basicConfig(level=logging.INFO, format=args.log_format)

    _LOGGER.debug(args)

    try:
        loop = asyncio.get_event_loop()

        # Listen for messages
        client = mqtt.Client()
        hermes = HomeAssistantHermesMqtt(
            client,
            url=args.url,
            access_token=args.access_token,
            api_password=args.api_password,
            event_type_format=args.event_type_format,
            certfile=args.certfile,
            keyfile=args.keyfile,
            handle_type=args.handle_type,
            siteIds=args.siteId,
            loop=loop,
        )

        _LOGGER.debug("Connecting to %s:%s", args.host, args.port)
        client.connect(args.host, args.port)
        client.loop_start()

        # Run event loop
        hermes.loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _LOGGER.debug("Shutting down")


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
