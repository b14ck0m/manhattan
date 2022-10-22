"""Config flow for Manhattan integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from pprint import *
from homeassistant import config_entries 
import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_COUNT, CONF_NAME, CONF_PATH
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, MQTT_ROOT_TOPIC, DEVICE_UUID, RELAY_COUNT

data_schema_user = {
    vol.Required(CONF_DEVICE_ID): str
}

data_schema_relay = {
    vol.Required(CONF_COUNT): str
}
_LOGGER = logging.getLogger(__name__)
test_name = ["kuchnia","lazienka","salon","biuro","sypialnia","przedpokoj 1","przedpokoj 2","sciana salon","kuchnia podswietlenie"," lustro"]

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    # (this is not implemented yet)
    VERSION = 1
    def __init__(self):
        self.data = {}
        self._errors = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.info("user step")
        if user_input is None:
            return self.async_show_form(step_id="user",
                                        data_schema=vol.Schema(data_schema_user),
                                        errors=self._errors)
        
        _LOGGER.info(pformat(user_input))
        self.data[DEVICE_UUID] = user_input["device_id"]
        self.data[RELAY_COUNT] = ""
        
        #await self.async_set_unique_id(self.data[DEVICE_UUID])
        #self._abort_if_unique_id_configured()
        
        return await self.async_step_relay_count()
    
    async def async_step_relay_count(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.info("relay step")
        if user_input is None:
            return self.async_show_form(step_id="relay_count",
                                        data_schema=vol.Schema(data_schema_relay),
                                        errors=self._errors)
        _LOGGER.info(pformat(user_input))
        self.data[RELAY_COUNT] = user_input["count"]
        self.data[CONF_NAME] = test_name
        path = [];
        for i in range(0,len(int(self.data[RELAY_COUNT]))):
            path.add(i);
        self.data[CONF_PATH] = path;
        return self.async_create_entry(title=DOMAIN,data=self.data)
