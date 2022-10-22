from __future__ import annotations

import logging


import voluptuous as vol

from pprint import pformat

from .const import DEVICE_UUID



import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (DOMAIN, PLATFORM_SCHEMA, LightEntity)
from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_ADDRESS, CONF_PATH
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


_LOGGER = logging.getLogger("Manhattan")

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.ensure_list,
    vol.Optional(CONF_PATH): cv.ensure_list,
    vol.Optional(CONF_ADDRESS): cv.string,
})

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Manhattan Light platform."""
    #Add Devices
    _LOGGER.info(pformat(config))

    for i in range(0,len(config[CONF_NAME])):
        light = {
            "name": config[CONF_NAME][i],
            "relay_num": config[CONF_PATH][i],
            "address": config[CONF_ADDRESS],
        }
        add_entities([ManhattanLight(light)])

async def async_setup_entry(
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entries,
):
    _LOGGER.info(pformat(config_entry.entry_id))
    config = config_entry.data
    _LOGGER.info(pformat(config));

    for i in range(0, len(config[CONF_NAME])):
        light = {
            "name": config[CONF_NAME][i],
            "relay_num": config[CONF_PATH][i],
            "address": config[DEVICE_UUID],
        }
        add_entities([ManhattanLight(light)])
    
class ManhattanLight(LightEntity):
    """Representation of an Manhattan Light."""
    
    def __init__(self, light) -> None:
        """Initialize an ManhattanLight"""
        _LOGGER.info(pformat(light))
        self._name = light["name"]
        self._state = False
        self.relay_num = light["relay_num"]
        self.topic = f"/light/{self.relay_num}/state"
        self.topic_switch = f"/light/{self.relay_num}/switch"

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name
    
    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs:Any) -> None:
        """Instruct the light to turn on."""
        self._state = True
        self.publishToMQTT()

    async def async_turn_off(self, **kwargs:Any) -> None:
        """Instruct the light to turn off."""
        self._state = False
        self.publishToMQTT()

    def update(self) -> None:
        """Fetch new state data from this light."""
        self._state = self.is_on

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            if message.payload == "on":
                self._state = True
            elif message.payload == "off":
                self._state = False
            else:
                self._state = None

            #self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.topic,
            message_received,
            1,
        )

    def publishToMQTT(self):
        topic = self.topic_switch
        #self.hass.components.mqtt.publish(self.hass, topic, str(int(self._attr_is_on)))
        if self.is_on == True:
            self.hass.components.mqtt.publish(self.hass, topic, "on")
        else:
            self.hass.components.mqtt.publish(self.hass, topic, "off")
        
