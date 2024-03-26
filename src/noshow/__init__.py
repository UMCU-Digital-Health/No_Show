import tomli

# load mute_period from toml file
with open("pyproject.toml", mode="rb") as fp:
    config = tomli.load(fp)
    MUTE_PERIOD = config["global-variables"]["mute_period"]
