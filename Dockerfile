FROM python:3.8

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt .
RUN python -m pip install -r requirements.txt

RUN npm -g config set user root \
    && npm install -g canvas \
    && npm install -g vega vega-lite vega-cli

ADD . /app/bot
WORKDIR /app/bot
RUN mkdir -p graphs data

CMD ["python", "clock.py"]