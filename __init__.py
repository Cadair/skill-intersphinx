from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import re
import aiohttp
from urllib.parse import urljoin
from sphobjinv import Inventory

REGEX = "`(\S+)`"


class Intersphinx(Skill):
    def __init__(self, opsdroid, config):
        super().__init__(opsdroid, config)
        self.object_map = None


    async def setup_inventories(self):
        if self.object_map is not None:
            return

        self.object_map = {}
        self.inventories = []
        async with aiohttp.ClientSession() as session:
            for iurl in self.config['inventories']:
                obj_url = urljoin(iurl, "objects.inv")
                async with session.get(obj_url) as resp:
                    inv = Inventory(await resp.read())
                    self.inventories.append(inv)
                self.object_map.update({i.name: urljoin(iurl, i.uri) for i in inv.objects})

    @match_regex(REGEX)
    async def respond_with_docs(self, message):
        await self.setup_inventories()

        matches = re.findall(REGEX, message.text)

        response = ""
        for match in matches:
            obj = self.object_map.get(match, None)
            if obj is not None:
                url = obj
                if url.endswith("$"):
                    url = url.replace("$", match)
                print(url)
                if response:
                    response += ", "
                response += f"<a href={url}>{match}</a>"

        if response:
            await message.respond(response)

