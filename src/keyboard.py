"""Keyboard command interface for GuardianAI applications."""

from typing import Any


class Keyboard:
    """Read user input without depending on pipeline internals."""

    def read_command(self) -> Any:
        """Read the next keyboard command.

        Returns:
            Application-level command value.
        """
        # TODO: Read keyboard input and return an application command.
