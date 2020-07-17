"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   05/03/2019

Provides useful helper functions for training plugins.
"""

import click
from pkg_resources import iter_entry_points


class LazyPluginGroup(click.Group):
    def __init__(self, entry_point_name, **kwargs):
        commands = {entry_point.name.replace('_', '-'): entry_point
                    for entry_point in iter_entry_points(entry_point_name)}
        self._loaded = set()
        super().__init__(commands=commands, **kwargs)

    def _load_entry_point(self, name):
        if name not in self._loaded:
            self.commands[name] = self.commands[name].load()
            self._loaded.add(name)

    def get_command(self, ctx, cmd_name):
        command = self.commands.get(cmd_name)
        if command is not None and cmd_name not in self._loaded:
            self.commands[cmd_name] = command.load()
        return super().get_command(ctx, cmd_name)

    def format_commands(self, ctx, formatter):
        commands = self.list_commands(ctx)
        if commands:
            with formatter.section("Commands"):
                formatter.write_dl((name, "") for name in commands)


