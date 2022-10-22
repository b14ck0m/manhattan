"""The Manhattan Light Integration"""
import asyncio
import logging

from homeassistant import config_entries, core
from .const import DOMAIN
from pprint import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    _LOGGER.info(pformat("setup entry"))
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    _LOGGER.debug(hass_data)
    #unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    #hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data
    _LOGGER.info(pformat(hass_data))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light")
    )
    return True

async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    _LOGGER.info(pformat("unsetup entry"))
    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, "light")]
        )
    )

    # Remove config entry from domain.
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def  async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the GitHub Custom component from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True
