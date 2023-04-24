"""Config flow for Manhattan integration."""
from __future__ import annotations

import asyncio
import aiohttp
import requests
import logging
import yaml
import json
from typing import Any
from pprint import *
from homeassistant import config_entries 
import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_COUNT, CONF_NAME, CONF_PATH, CONF_PASSWORD, CONF_USERNAME, CONF_TARGET, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, MQTT_ROOT_TOPIC, DEVICE_UUID, RELAY_COUNT, DEVICE_PASSWORD, MQTT_BROKER, MQTT_USERNAME, MQTT_PASSWORD

data_schema_user = {
    vol.Required(CONF_PASSWORD): str
}

data_schema_relay = {
    vol.Required(CONF_COUNT): str
}

data_schema_mqtt = {
    vol.Required(CONF_TARGET): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_PORT, default=8883): int
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
        self.data[CONF_PATH] = []
        self.data[CONF_NAME] = []
        self._errors = {}
        self.host = ''
        self.name = ''
        self.counting = 0

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user",
                                        errors=self._errors)
        
        
        #await self.async_set_unique_id(self.data[DEVICE_UUID])
        #self._abort_if_unique_id_configured()
        
        return await self.async_step_zeroconf()



    async def async_step_zeroconf(self, discovery_info:
            zeroconf.ZeroconfServiceInfo) -> FlowResult:
        _LOGGER.info("CF: Host: " + discovery_info.host)
        self.host = discovery_info.host
        self.name = discovery_info.hostname.split('.')[0]
        _LOGGER.info("CF: hostname: " + discovery_info.hostname + " name: " + discovery_info.name );
        for i in discovery_info.addresses:
            _LOGGER.info("CF: addresses" + i);
        _LOGGER.info("CF: " + yaml.dump(discovery_info.properties));
        return await self.async_step_deviceID()

    async def async_step_deviceID(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.info("user step")

        if user_input is None:
            return self.async_show_form(step_id="deviceID",
                                        data_schema=vol.Schema(data_schema_user),
                                        description_placeholders={"DEVICE_UUID":self.name},
                                        errors=self._errors)
        
        _LOGGER.info(pformat(user_input))
        self.data[DEVICE_PASSWORD] = user_input[CONF_PASSWORD]
        self.data[DEVICE_UUID] = self.name;
        
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
        self.data[CONF_PORT] = user_input[CONF_PORT]
        if self.data[CONF_PORT] == 0:
            self.data[CONF_PORT] = 8883;
        _LOGGER.info("[MQTT] "+self.data[MQTT_USERNAME] +self.data[MQTT_PASSWORD]
        + str(self.data[CONF_PORT]))
        data = '{"password":"'+self.data[DEVICE_PASSWORD]+'","hostname":"'+self.data[MQTT_BROKER]+'"}';
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        async with session.post("https://"+self.host+"/uri/blocker",data=data) as resp:
            if resp.status != 200:
                return await abort();
        #ret = requests.post("https://"+self.host+"/uri/blocker",data,verify=False);
        data = '{"password":"'+self.data[DEVICE_PASSWORD]+'","MQTTUser":"'+self.data[MQTT_USERNAME]+'","MQTTPassword":"'+self.data[MQTT_PASSWORD]+'"}';
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        async with session.post("https://"+self.host+"/uri/mqtt_conf",data=data) as resp:
            if resp.status != 200:
                return await abort();
        return await self.async_step_relay_count()    

    async def async_step_relay_count(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _LOGGER.info("relay step")
        text = "";
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        async with session.get("https://"+self.host+"/uri/relay_count") as resp:
            if resp.status != 200:
                return await abort();
            else:
                text = resp.text
        data = json.load(text);
        self.data[RELAY_COUNT] = data[count];
        self.counting = 0;
        return await self.async_step_relay_name()

    async def async_step_relay_name(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="relay_name",
                                        data_schema=vol.Schema(data_schema_relay),
                                        description_placeholders={"name": self.counting};
                                        errors=self._errors)
        _LOGGER.info(pformat(user_input))
        self.data[CONF_NAME].append(self.data[CONF_NAME]);
        self.data[CONF_PATH].append(self.data["counting"]);
        self.counting +=1;
        if self.counting < self.data[RELAY_COUNT]:
            return self.async_show_form(step_id="relay_name",
                                        data_schema=vol.Schema(data_schema_relay),
                                        description_placeholders={"name": str(self.data["counting"])};
                                        errors=self._errors)
        return self.async_create_entry(title=DOMAIN,data=self.data)
