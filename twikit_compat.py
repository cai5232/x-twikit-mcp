"""Support X's current numeric webpack chunk map alongside the older map."""
import re

def ondemand_url(html):
    legacy = re.search(r"""["']ondemand\.s["']\s*:\s*["']([\w]+)["']""", html)
    if legacy:
        digest = legacy.group(1)
    else:
        chunk = re.search(r"""(?:^|[,\{])\s*(\d+)\s*:\s*["']ondemand\.s["']""", html)
        if not chunk:
            raise RuntimeError("X ondemand chunk was not found")
        hashed = re.search(r"""(?:^|[,\{])\s*""" + re.escape(chunk.group(1)) + r"""\s*:\s*["']([0-9a-f]+)["']""", html)
        if not hashed:
            raise RuntimeError("X ondemand chunk hash was not found")
        digest = hashed.group(1)
    return f"https://abs.twimg.com/responsive-web/client-web/ondemand.s.{digest}a.js"

def install():
    import twikit.x_client_transaction.transaction as transaction

    async def get_indices(self, home_page_response, session, headers):
        response = self.validate_response(home_page_response)
        if response is None:
            response = self.home_page_response
        script = await session.request(method="GET", url=ondemand_url(str(response)), headers=headers)
        script.raise_for_status()
        indices = [int(match.group(2)) for match in transaction.INDICES_REGEX.finditer(script.text)]
        if not indices:
            raise RuntimeError("X transaction key indices were not found in the current script")
        return indices[0], indices[1:]

    transaction.ClientTransaction.get_indices = get_indices

    # X omits the description URL list when a profile has no links.
    from twikit.user import User
    original_user_init = User.__init__

    def user_init(self, client, data):
        from copy import deepcopy
        data = deepcopy(data)
        legacy = data.get("legacy", {})
        entities = legacy.setdefault("entities", {})
        entities.setdefault("description", {}).setdefault("urls", [])
        original_user_init(self, client, data)

    User.__init__ = user_init
