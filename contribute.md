# Issues and Features

Issues are reported [GitHub](https://github.com/themoeway/Immersionbot/issues) should include information about:
- What the problem, question, or request is.
- What browser is being used.
- What version of Yomitan is being used.
- If applicable, an export of the settings file.

- # Development

Contributions are welcome from any developers who would like to help out.
Below are a few guidelines to ensure contributions have a good level of quality and consistency:

- Open GitHub issues to discuss large features before writing code.
- Write clean, modern [PEP8](https://realpython.com/python-pep8/) code (classes, whitespacing, etc.)
- Large pull requests without a clear scope will not be merged.
- Incomplete or non-standalone features will not be merged.

Create a role called "Moderator" on your discord server where you invited the bot to and assign it to yourself.
To develop on the bot, start the bot then set change to the code. If you change something in the `immersionbotcogs` directory, then instead of restarting the bot, use the `/reload_cog` command, which restarts that one command block i.e cog/file.
If you change a file outside of the `immersionbotcogs` direcotry, then you need to restart the bot so the changes take effect.

## Setup

The immersion bot uses [Python 3.9.0](https://www.python.org/downloads/release/python-390/) and [pip 24.2](https://discuss.python.org/t/announcement-pip-24-2-release/59402) tools for building and testing.

##  Testing

Unit tests and various other tests can be executed by running `python -m pytest -v`. The source for the specific tests can be find in the [test](https://github.com/themoeway/Immersionbot/tree/main/test) directory.
