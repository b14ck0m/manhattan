"""Config flow for Manhattan integration."""
from __future__ import annotations

import asyncio
import aiohttp
import logging
from typing import Any
from pprint import *
from homeassistant import config_entries 
import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_COUNT, CONF_NAME, CONF_PATH, CONF_PASSWORD, CONF_USERNAME, CONF_TARGET, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, MQTT_ROOT_TOPIC, DEVICE_UUID, RELAY_COUNT

data_schema_user = {
    vol.Required(CONF_DEVICE_ID): str,
    vol.Required(CONF_PASSWORD): str
}

data_schema_relay = {
    vol.Required(CONF_COUNT): str
}

data_schema_mqtt = {
    vol.Required(CONF_TARGET): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    CONF_PORT: int
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
        self.host = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user",
                                        data_schema=vol.Schema(),
                                        errors=self._errors)
        
        _LOGGER.info(pformat(user_input))
        
        #await self.async_set_unique_id(self.data[DEVICE_UUID])
        #self._abort_if_unique_id_configured()
        
        return await self.async_step_zeroconf()



    async def async_step_zeroconf(self, discovery_info:
            zeroconf.ZeroconfServiceInfo) -> FlowResult:
        _LOGGER.info("CF: Host: " + discovery_info.host)
        self.host = discovery_info.host
        #self.uuid =
        _LOGGER.info("CF: addresses" + discovery_info.addresses + " hostname: " + discovery_info.hostname + " name: " + discovery_info.name + "properties: " + discovert_info.properties);
        return await self.async_step_start()

    async def async_step_start(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.info("user step")

        if user_input is None:
            return self.async_show_form(step_id="init",
                                        data_schema=vol.Schema(data_schema_user),
                                        errors=self._errors)
        
        _LOGGER.info(pformat(user_input))
        self.data[DEVICE_UUID] = user_input["device_id"]
        self.data[DEVICE_PASSWORD] = user_input[CONF_PASSWORD]
        
        #await self.async_set_unique_id(self.data[DEVICE_UUID])
        #self._abort_if_unique_id_configured()
        
        return await self.async_step_mqtt()

    async def async_step_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.info("mqtt step")
        if user_input is None:
            return self.async_show_form(step_id="mqtt",
                                        data_schema=vol.Schema(data_schema_mqtt),
                                        errors=self._errors)
        _LOGGER.info(pformat(user_input))
        self.data[MQTT_BROKER] = user_input[CONF_TARGET]
        self.data[MQTT_USERNAME] = user_input[CONF_USERNAME]
        self.data[MQTT_PASSWORD] = user_input[CONF_PASSWORD]
        self.data[MQTT_PORT] = user_input[CONF_PORT]
        if self.data[MQTT_PORT] == 0:
            self.data[MQTT_PORT] == 8883;
        _LOGGER.info("[MQTT] "+self.data[MQTT_USERNAME] +self.data[MQTT_PASSWORD]
        + str(self.data[MQTT_PORT]))

        data = '{"password":"'+self.data[DEVICE_PASSWORD]+'","hostname":'+self.data[MQTT_BROKER]+'"}';

        ret = requests.post("https://"+self.host+"/uri/blocker",data,verify=False);

        if ret.text == "SUCCESS\n":
            data = '{"password":"'+self.data[DEVICE_PASSWORD]+'","MQTT_USERNAME":'+self.data[MQTT_USERNAME]+'","MQTT_PASSWORD":"'+self.data[MQTT_PASSWORD]+'"}';
            ret = requests.post("https://"+self.host+"/uri/mqtt_conf",data,verify=False);
            if ret.text !="SUCCESS\n":
                return await abort();
        else:
            return await abort();


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
        for i in range(0,int(self.data[RELAY_COUNT])):
            path.append(i);
        self.data[CONF_PATH] = path;
        return self.async_create_entry(title=DOMAIN,data=self.data)
