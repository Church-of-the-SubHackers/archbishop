# Archbishop

A basic Discord bot skeleton intended to act as a host for Cogs developed for the Church of the Subhackers discord community.

# Setup

Rename `example.env` to `.env` and add your discord bot token to the `BOT_TOKEN` variable.

# Running in Docker

## Building Image

```
git clone https://github.com/Church-of-the-SubHackers/archbishop
cd archbishop
docker build -t archbishop .
```

## Running Container

To allow for adding new Cogs or modifying existing cogs without rebuilding the Docker Image or restarting Archbishop, when running within Docker, Archbishop does not copy the `cogs` directory into the image. It is important that the `cogs` directory be mounted as part of the `docker run` command in order to allow for real-time access and modification of Cogs.

```
cd archbishop
docker run -d -v $HOME/archbishop/cogs:/app/cogs archbishop
```