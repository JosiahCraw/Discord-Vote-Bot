FROM python:3.6.10-buster

RUN pip install --user mcrcon discord.py

WORKDIR /work
COPY bot.py .

ENV DISCORD_TOKEN=NjkxODEzNTc3MzM3NzMzMTUx.XnlcFg.oIWLv6nIHjz_VazpeD7RxcLZx0Q
ENV DISCORD_GUILD=Ciiiv
ENV MC_SERVER_IP=192.168.1.99
ENV MC_RCON_PORT=25575
ENV MC_RCON_PASS=supersecretpasscodething

CMD python bot.py