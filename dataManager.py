import json
import os


class DataManager:
    def __init__(self, data_file="bot_data.json"):
        self.data_file = os.getenv("BOT_DATA_PATH", data_file)
        self.data = {}
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    print("Error decoding JSON. Initializing with empty data.")
                    self.data = {}
        else:
            self.data = {}

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    # ---- Methods for Handling Data ----

    #  -- Thread Holding --

    def add_held_thread(self, guild_id: int, thread_id: int):
        """Add a held thread under a specific guild."""
        guild_id, thread_id = str(guild_id), str(thread_id)
        self.data.setdefault("held_threads", {}).setdefault(guild_id, []).append(
            thread_id
        )
        self.save_data()

    def remove_held_thread(self, guild_id: int, thread_id: int):
        guild_id, thread_id = str(guild_id), str(thread_id)
        if guild_id in self.data.get("held_threads", {}):
            self.data["held_threads"][guild_id] = [
                t for t in self.data["held_threads"][guild_id] if t != thread_id
            ]
            if not self.data["held_threads"][guild_id]:
                del self.data["held_threads"][guild_id]
            self.save_data()

    def get_held_threads(self, guild_id: int = -1):
        """Return a list of held thread IDs for a given guild"""
        held_threads = self.data.get("held_threads", {})

        if guild_id == -1:
            return held_threads

        return held_threads.get(str(guild_id), {})

    #  -- Reaction Roles --
    def add_reaction_role(
        self, guild_id: int, channel_id: int, message_id: int, emoji: str, role_id: int
    ):
        """Associate a reaction emoji with a role for a given message."""
        guild_id, channel_id, message_id = (
            str(guild_id),
            str(channel_id),
            str(message_id),
        )
        role_id = int(role_id)

        self.data.setdefault("reaction_roles", {}).setdefault(guild_id, {}).setdefault(
            channel_id, {}
        ).setdefault(message_id, {})[emoji] = role_id
        self.save_data()

    def remove_reaction_role(
        self, guild_id: int, channel_id: int, message_id: int, emoji=None
    ):
        guild_id, channel_id, message_id = (
            str(guild_id),
            str(channel_id),
            str(message_id),
        )

        if guild_id in self.data.get("reaction_roles", {}):
            if channel_id in self.data["reaction_roles"][guild_id]:
                if message_id in self.data["reaction_roles"][guild_id][channel_id]:
                    if emoji:
                        pop_data = self.data["reaction_roles"][guild_id][channel_id][
                            message_id
                        ].pop(emoji, None)
                    else:
                        pop_data = self.data["reaction_roles"][guild_id][
                            channel_id
                        ].pop(message_id, None)

                    # Cleanup empty dictionaries
                    if not self.data["reaction_roles"][guild_id][channel_id]:
                        del self.data["reaction_roles"][guild_id][channel_id]
                    if not self.data["reaction_roles"][guild_id]:
                        del self.data["reaction_roles"][guild_id]

                    self.save_data()
                    return pop_data

    def get_reaction_roles(
        self,
        guild_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        emoji=None,
    ):
        """Retrieve reaction-role mappings for a specific message, channel, or an entire guild."""
        reaction_roles = self.data.get("reaction_roles", {})

        if guild_id is None and channel_id is None and message_id is None:
            return reaction_roles

        guild_data = reaction_roles.get(str(guild_id), {})

        if channel_id is None:
            return guild_data

        channel_data = guild_data.get(str(channel_id), {})

        if message_id is None:
            return channel_data

        message_data = channel_data.get(str(message_id), {})

        if emoji is None:
            return message_data

        return message_data.get(emoji.name)

    #  -- Temp Channels --

    def setup_voice_hub(self, guild_id: int, hub_channel_id: int):
        """Loads guild VH into data"""
        guild_id = str(guild_id)

        if "temp_channels" not in self.data:
            self.data["temp_channels"] = {}

        self.data["temp_channels"].setdefault(guild_id, {})["hub_channel_id"] = (
            hub_channel_id
        )
        self.data["temp_channels"][guild_id].setdefault("temp_channels", {})

        self.save_data()

    def destroy_voice_hub(self, guild_id: int):
        """Removes data pertaining to the guild's temp voice"""
        if "temp_channels" in self.data and str(guild_id) in self.data["temp_channel"]:
            del self.data["temp_channel"][guild_id]
            self.save_data()

    def set_channel_owner(self, guild_id: int, channel_id: int, new_owner_id: int):
        self.get_channel_data(guild_id, channel_id)["owner_id"] = new_owner_id
        self.save_data()

    def add_temp_channel(self, guild_id: int, channel_id: int, owner_id: int):
        """Store a temporary channel with its owner."""
        guild_id = str(guild_id)
        channel_id, owner_id = str(channel_id), int(owner_id)

        if guild_id not in self.data["temp_channels"]:
            self.data["temp_channels"][guild_id] = {"temp_channels": {}}
        self.data.setdefault("temp_channels", {}).setdefault(guild_id, {}).setdefault(
            "temp_channels", {}
        )[channel_id] = {"owner_id": owner_id}
        self.save_data()

    def remove_temp_channel(self, guild_id: int, channel_id: int):
        """Remove a temporary channel."""
        guild_id = str(guild_id)
        channel_id = str(channel_id)

        if guild_id in self.data.get("temp_channels", {}):
            self.data["temp_channels"][guild_id]["temp_channels"].pop(channel_id, None)
            self.save_data()

    def get_temp_channels(self, guild_id: int = None):
        """Retrieve all temporary channels for a guild, if one is not given the temp_channels data is given."""
        temp_channels = self.data.get("temp_channels", {})

        if guild_id is None:
            return temp_channels

        return temp_channels.get(str(guild_id), {})

    def get_channel_data(self, guild_id: int, channel_id: int):
        return (
            self.get_temp_channels(guild_id)
            .get("temp_channels", {})
            .get(str(channel_id), {})
        )

    def get_guild_voice_hub(self, guild_id: int):
        """Gets the ID of the voice hub channel given a guild"""
        return self.get_temp_channels(guild_id).get("hub_channel_id", {})
