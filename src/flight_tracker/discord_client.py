import json
from pathlib import Path
import requests

MESSAGE_ID_PATH = Path("data/discord_message_id.txt")
API = "https://discord.com/api/v10"


class DiscordClient:
    def __init__(self, token: str, channel_id: str):
        self.token = token
        self.channel_id = channel_id
        self.headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}

    def _request(self, method: str, url: str, **kwargs):
        response = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    def upsert_tracker_message(self, content: str, image_path: Path,
                               message_id_path: Path = MESSAGE_ID_PATH) -> str:
        message_id = message_id_path.read_text().strip() if message_id_path.exists() else ""
        url = f"{API}/channels/{self.channel_id}/messages"
        if message_id:
            try:
                self._request("PATCH", f"{url}/{message_id}", json={"content": content})
            except requests.HTTPError as exc:
                if exc.response is None or exc.response.status_code != 404:
                    raise
                message_id = ""

        with image_path.open("rb") as image_file:
            files = {"files[0]": ("price-history.png", image_file, "image/png")}
            payload = {"content": content, "attachments": []}
            if message_id:
                payload["attachments"] = [{"id": "0", "filename": "price-history.png"}]
                response = requests.patch(
                    f"{url}/{message_id}", headers={"Authorization": f"Bot {self.token}"},
                    data={"payload_json": json.dumps(payload)},
                    files=files, timeout=30,
                )
                if response.status_code == 404:
                    message_id = ""
                else:
                    response.raise_for_status()
                    message_id_path.parent.mkdir(parents=True, exist_ok=True)
                    message_id_path.write_text(message_id + "\n")
                    return message_id

            response = requests.post(
                url, headers={"Authorization": f"Bot {self.token}"},
                data={"payload_json": json.dumps({"content": content})},
                files=files, timeout=30,
            )
            response.raise_for_status()
            message_id = response.json()["id"]
        message_id_path.parent.mkdir(parents=True, exist_ok=True)
        message_id_path.write_text(message_id + "\n")
        return message_id

    def send_alert(self, user_id: str, message: str) -> None:
        self._request("POST", f"{API}/channels/{self.channel_id}/messages",
                      json={"content": f"<@{user_id}> {message}",
                            "allowed_mentions": {"users": [user_id]}})
