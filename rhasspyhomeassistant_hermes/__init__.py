"""Hermes MQTT server for Rhasspy fuzzywuzzy"""
import json
import logging
import os
import typing
from enum import Enum
from urllib.parse import urljoin
from uuid import uuid4

import attr
import requests
from rhasspyhermes.base import Message
from rhasspyhermes.handle import HandleToggleOff, HandleToggleOn
from rhasspyhermes.nlu import NluIntent
from rhasspyhermes.tts import TtsSay

_LOGGER = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


class HandleType(str, Enum):
    """Method for handling intents."""

    EVENT = "event"
    INTENT = "intent"


# -----------------------------------------------------------------------------


class HomeAssistantHermesMqtt:
    """Hermes MQTT server for Rhasspy intent handling with Home Assistant."""

    def __init__(
        self,
        client,
        url: str,
        access_token: typing.Optional[str] = None,
        api_password: typing.Optional[str] = None,
        event_type_format: str = "rhasspy_{0}",
        pem_file: typing.Optional[str] = None,
        handle_type: HandleType = HandleType.EVENT,
        siteIds: typing.Optional[typing.List[str]] = None,
    ):
        self.client = client
        self.url = url

        self.access_token = access_token
        self.api_password = api_password
        self.event_type_format = event_type_format
        self.pem_file = pem_file
        self.handle_type = handle_type

        self.handle_enabled = True

        self.siteIds = siteIds or []

    # -------------------------------------------------------------------------

    def handle_intent(self, nlu_intent: NluIntent):
        """Handle intent with Home Assistant."""
        try:
            if self.handle_type == HandleType.EVENT:
                self.handle_home_assistant_event(nlu_intent)
            elif self.handle_type == HandleType.INTENT:
                response_dict = self.handle_home_assistant_intent(nlu_intent)

                # Check for speech response
                tts_text = response_dict.get("speech", {}).get("text", "")
                if tts_text:
                    # Forward to TTS system
                    self.publish(
                        TtsSay(
                            text=tts_text,
                            id=str(uuid4()),
                            siteId=nlu_intent.siteId,
                            sessionId=nlu_intent.sessionId,
                        )
                    )
            else:
                raise ValueError(f"Unsupported handle_type (got {self.handle_type})")
        except Exception:
            _LOGGER.exception("handle_intent")

    # -------------------------------------------------------------------------

    def handle_home_assistant_event(self, nlu_intent: NluIntent):
        """POSTs an event to Home Assistant's /api/events endpoint."""
        # Create new Home Assistant event
        event_type = self.event_type_format.format(nlu_intent.intent.intentName)
        slots = {}
        for slot in nlu_intent.slots:
            slots[slot.slotName] = slot.value

        # Add meta slots
        slots["_text"] = nlu_intent.input
        slots["_raw_text"] = nlu_intent.raw_input

        # Send event
        post_url = urljoin(self.url, "api/events/" + event_type)
        kwargs = self.get_hass_headers()

        if self.pem_file:
            _LOGGER.debug("Using PEM: %s", self.pem_file)
            kwargs["verify"] = self.pem_file

        _LOGGER.debug(post_url)
        response = requests.post(post_url, json=slots, **kwargs)
        response.raise_for_status()

    def handle_home_assistant_intent(
        self, nlu_intent: NluIntent
    ) -> typing.Dict[str, typing.Any]:
        """POSTs a JSON intent to Home Assistant's /api/intent/handle endpoint."""
        slots = {}
        for slot in nlu_intent.slots:
            slots[slot.slotName] = slot.value

        # Add meta slots
        slots["_text"] = nlu_intent.input
        slots["_raw_text"] = nlu_intent.raw_input

        hass_intent = {"name": nlu_intent.intent.intentName, "data": slots}

        # POST intent JSON
        post_url = urljoin(self.url, "api/intent/handle")
        kwargs = self.get_hass_headers()

        if self.pem_file:
            _LOGGER.debug("Using PEM: %s", self.pem_file)
            kwargs["verify"] = self.pem_file

        _LOGGER.debug(post_url)
        response = requests.post(post_url, json=hass_intent, **kwargs)
        response.raise_for_status()

        return response.json()

    def get_hass_headers(self) -> typing.Dict[str, str]:
        """Gets HTTP authorization headers for Home Assistant POST."""
        if self.access_token:
            return {"Authorization": self.access_token}

        if self.api_password:
            return {"X-HA-Access": self.api_password}

        hassio_token = os.environ.get("HASSIO_TOKEN")
        if hassio_token:
            return {"Authorization": f"Bearer {hassio_token}"}

        # No headers
        return {}

    # -------------------------------------------------------------------------

    def on_connect(self, client, userdata, flags, rc):
        """Connected to MQTT broker."""
        try:
            topics = [
                NluIntent.topic(intentName="#"),
                HandleToggleOn.topic(),
                HandleToggleOff.topic(),
            ]

            for topic in topics:
                self.client.subscribe(topic)
                _LOGGER.debug("Subscribed to %s", topic)
        except Exception:
            _LOGGER.exception("on_connect")

    def on_message(self, client, userdata, msg):
        """Received message from MQTT broker."""
        try:
            _LOGGER.debug("Received %s byte(s) on %s", len(msg.payload), msg.topic)
            if NluIntent.is_topic(msg.topic):
                json_payload = json.loads(msg.payload)

                # Check siteId
                if not self._check_siteId(json_payload):
                    return

                self.handle_intent(NluIntent.from_dict(json_payload))
            elif HandleToggleOn.is_topic(msg.topic):
                json_payload = json.loads(msg.payload)
                if not self._check_siteId(json_payload):
                    return

                self.handle_enabled = True
                _LOGGER.debug("Intent handling enabled")
            elif HandleToggleOff.is_topic(msg.topic):
                json_payload = json.loads(msg.payload)
                if not self._check_siteId(json_payload):
                    return

                self.handle_enabled = False
                _LOGGER.debug("Intent handling disabled")
        except Exception:
            _LOGGER.exception("on_message")

    def publish(self, message: Message, **topic_args):
        """Publish a Hermes message to MQTT."""
        try:
            _LOGGER.debug("-> %s", message)
            topic = message.topic(**topic_args)
            payload = json.dumps(attr.asdict(message))
            _LOGGER.debug("Publishing %s char(s) to %s", len(payload), topic)
            self.client.publish(topic, payload)
        except Exception:
            _LOGGER.exception("on_message")

    # -------------------------------------------------------------------------

    def _check_siteId(self, json_payload: typing.Dict[str, typing.Any]) -> bool:
        if self.siteIds:
            return json_payload.get("siteId", "default") in self.siteIds

        # All sites
        return True
