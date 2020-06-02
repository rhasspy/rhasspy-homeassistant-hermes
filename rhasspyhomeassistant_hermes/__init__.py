"""Hermes MQTT server for Rhasspy fuzzywuzzy"""
import logging
import os
import ssl
import typing
from enum import Enum
from urllib.parse import urljoin
from uuid import uuid4

import aiohttp
from rhasspyhermes.base import Message
from rhasspyhermes.client import GeneratorType, HermesClient
from rhasspyhermes.handle import HandleToggleOff, HandleToggleOn
from rhasspyhermes.nlu import NluIntent
from rhasspyhermes.tts import TtsSay

_LOGGER = logging.getLogger("rhasspyhomeassistant_hermes")

# -----------------------------------------------------------------------------


class HandleType(str, Enum):
    """Method for handling intents."""

    EVENT = "event"
    INTENT = "intent"


# -----------------------------------------------------------------------------


class HomeAssistantHermesMqtt(HermesClient):
    """Hermes MQTT server for Rhasspy intent handling with Home Assistant."""

    def __init__(
        self,
        client,
        url: str,
        access_token: typing.Optional[str] = None,
        api_password: typing.Optional[str] = None,
        event_type_format: str = "rhasspy_{0}",
        certfile: typing.Optional[str] = None,
        keyfile: typing.Optional[str] = None,
        handle_type: HandleType = HandleType.EVENT,
        site_ids: typing.Optional[typing.List[str]] = None,
    ):
        super().__init__("rhasspyhomeassistant_hermes", client, site_ids=site_ids)

        self.subscribe(NluIntent, HandleToggleOn, HandleToggleOff)

        self.url = url

        self.access_token = access_token
        self.api_password = api_password
        self.event_type_format = event_type_format
        self.handle_type = handle_type

        self.handle_enabled = True

        # SSL
        self.ssl_context = ssl.SSLContext()
        if certfile:
            _LOGGER.debug("Using SSL with certfile=%s, keyfile=%s", certfile, keyfile)
            self.ssl_context.load_cert_chain(certfile, keyfile)

        # Async HTTP
        self._http_session: typing.Optional[aiohttp.ClientSession] = None

    @property
    def http_session(self):
        """Get or create async HTTP session"""
        if self._http_session is None:
            self._http_session = aiohttp.ClientSession()

        return self._http_session

    # -------------------------------------------------------------------------

    async def handle_intent(
        self, nlu_intent: NluIntent
    ) -> typing.AsyncIterable[TtsSay]:
        """Handle intent with Home Assistant."""
        try:
            if self.handle_type == HandleType.EVENT:
                await self.handle_home_assistant_event(nlu_intent)
            elif self.handle_type == HandleType.INTENT:
                response_dict = await self.handle_home_assistant_intent(nlu_intent)
                assert response_dict, f"No response from {self.url}"

                # Check for speech response
                tts_text = (
                    response_dict.get("speech", {}).get("plain", {}).get("speech", "")
                )
                if tts_text:
                    # Forward to TTS system
                    yield TtsSay(
                        text=tts_text,
                        id=str(uuid4()),
                        site_id=nlu_intent.site_id,
                        session_id=nlu_intent.session_id,
                    )
            else:
                raise ValueError(f"Unsupported handle_type (got {self.handle_type})")
        except Exception:
            _LOGGER.exception("handle_intent")

    # -------------------------------------------------------------------------

    async def handle_home_assistant_event(self, nlu_intent: NluIntent):
        """POSTs an event to Home Assistant's /api/events endpoint."""
        try:
            # Create new Home Assistant event
            event_type = self.event_type_format.format(nlu_intent.intent.intent_name)
            slots: typing.Dict[str, typing.Any] = {}

            if nlu_intent.slots:
                for slot in nlu_intent.slots:
                    slots[slot.slot_name] = slot.value["value"]

            # Add meta slots
            slots["_text"] = nlu_intent.input
            slots["_raw_text"] = nlu_intent.raw_input
            slots["_intent"] = nlu_intent.to_dict()

            # Send event
            post_url = urljoin(self.url, "api/events/" + event_type)
            headers = self.get_hass_headers()

            _LOGGER.debug(post_url)

            # No response expected
            async with self.http_session.post(
                post_url, json=slots, headers=headers, ssl=self.ssl_context
            ) as response:
                response.raise_for_status()
        except Exception:
            _LOGGER.exception("handle_home_assistant_event")

    async def handle_home_assistant_intent(
        self, nlu_intent: NluIntent
    ) -> typing.Dict[str, typing.Any]:
        """POSTs a JSON intent to Home Assistant's /api/intent/handle endpoint."""
        try:
            slots: typing.Dict[str, typing.Any] = {}

            if nlu_intent.slots:
                for slot in nlu_intent.slots:
                    slots[slot.slot_name] = slot.value["value"]

            # Add meta slots
            slots["_text"] = nlu_intent.input
            slots["_raw_text"] = nlu_intent.raw_input
            slots["_intent"] = nlu_intent.to_dict()

            hass_intent = {"name": nlu_intent.intent.intent_name, "data": slots}

            # POST intent JSON
            post_url = urljoin(self.url, "api/intent/handle")
            headers = self.get_hass_headers()

            _LOGGER.debug(post_url)

            # JSON response expected with optional speech
            async with self.http_session.post(
                post_url, json=hass_intent, headers=headers, ssl=self.ssl_context
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception:
            _LOGGER.exception("handle_home_assistant_intent")

        # Empty response
        return {}

    def get_hass_headers(self) -> typing.Dict[str, str]:
        """Gets HTTP authorization headers for Home Assistant POST."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}

        if self.api_password:
            return {"X-HA-Access": self.api_password}

        hassio_token = os.environ.get("HASSIO_TOKEN")
        if hassio_token:
            return {"Authorization": f"Bearer {hassio_token}"}

        # No headers
        return {}

    # -------------------------------------------------------------------------

    async def on_message(
        self,
        message: Message,
        site_id: typing.Optional[str] = None,
        session_id: typing.Optional[str] = None,
        topic: typing.Optional[str] = None,
    ) -> GeneratorType:
        """Received message from MQTT broker."""
        if isinstance(message, NluIntent):
            if self.handle_enabled:
                async for intent_result in self.handle_intent(message):
                    yield intent_result
        elif isinstance(message, HandleToggleOn):
            self.handle_enabled = True
            _LOGGER.debug("Intent handling enabled")
        elif isinstance(message, HandleToggleOff):
            self.handle_enabled = False
            _LOGGER.debug("Intent handling disabled")
        else:
            _LOGGER.warning("Unexpected message: %s", message)
