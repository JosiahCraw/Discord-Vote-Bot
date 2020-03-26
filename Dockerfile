FROM python:3.6.10-buster

RUN pip install --user mcrcon discord.py

WORKDIR /work
COPY bot.py .

CMD python bot.py