# Rhasspy Fuzzywuzzy Hermes

[![Continous Integration](https://github.com/rhasspy/rhasspy-fuzzywuzzy-hermes/workflows/Tests/badge.svg)](https://github.com/rhasspy/rhasspy-fuzzywuzzy-hermes/actions)
[![GitHub license](https://img.shields.io/github/license/rhasspy/rhasspy-fuzzywuzzy-hermes.svg)](https://github.com/rhasspy/rhasspy-fuzzywuzzy-hermes/blob/master/LICENSE)

Implements `hermes/nlu` functionality from [Hermes protocol](https://docs.snips.ai/reference/hermes) using [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy).

## Running With Docker

```bash
docker run -it rhasspy/rhasspy-fuzzywuzzy-hermes:<VERSION> <ARGS>
```

## Building From Source

Clone the repository and create the virtual environment:

```bash
git clone https://github.com/rhasspy/rhasspy-fuzzywuzzy-hermes.git
cd rhasspy-fuzzywuzzy-hermes
make venv
```

Run the `bin/rhasspy-fuzzywuzzy-hermes` script to access the command-line interface:

```bash
bin/rhasspy-fuzzywuzzy-hermes --help
```

## Building the Debian Package

Follow the instructions to build from source, then run:

```bash
source .venv/bin/activate
make debian
```

If successful, you'll find a `.deb` file in the `dist` directory that can be installed with `apt`.

## Building the Docker Image

Follow the instructions to build from source, then run:

```bash
source .venv/bin/activate
make docker
```

This will create a Docker image tagged `rhasspy/rhasspy-fuzzywuzzy-hermes:<VERSION>` where `VERSION` comes from the file of the same name in the source root directory.

NOTE: If you add things to the Docker image, make sure to whitelist them in `.dockerignore`.

## Command-Line Options

```
usage: rhasspy-fuzzywuzzy-hermes [-h] [--examples EXAMPLES]
                                 [--intent-graph INTENT_GRAPH]
                                 [--sentences SENTENCES] [--slots SLOTS]
                                 [--slot-programs SLOT_PROGRAMS]
                                 [--watch-delay WATCH_DELAY] [--host HOST]
                                 [--port PORT] [--siteId SITEID]
                                 [--language LANGUAGE] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --examples EXAMPLES   Path to examples JSON file
  --intent-graph INTENT_GRAPH
                        Path to intent graph JSON file
  --sentences SENTENCES
                        Watch sentences.ini file(s) for changes and re-train
  --slots SLOTS         Directories with static slot text files
  --slot-programs SLOT_PROGRAMS
                        Directories with slot programs
  --watch-delay WATCH_DELAY
                        Seconds between polling sentence file(s) for training
  --host HOST           MQTT host (default: localhost)
  --port PORT           MQTT port (default: 1883)
  --siteId SITEID       Hermes siteId(s) to listen for (default: all)
  --language LANGUAGE   Language used for number replacement
  --debug               Print DEBUG messages to the console
```
