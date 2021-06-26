# COVID-19 Norge - Twitter Bot
<a href="https://twitter.com/covid19norge">
<div align="center">
<img src="https://user-images.githubusercontent.com/11590359/83902735-38810c80-a75d-11ea-94f8-dbc6aff85a61.png"/>

<b>COVID-19 Norge</b><br>
*https://twitter.com/covid19norge*
</div>
</a>

## Description
Twitter bot for tracking live COVID-19 statistics in Norway.

The bot autoposts live updates with a [Twitter developer account](https://developer.twitter.com/en/apply-for-access):
```yaml
twitter:
  auth:
    consumer_key: <CONSUMER_KEY>
    consumer_secret: <CONSUMER_SECRET>
    access_token: <ACCESS_TOKEN>
    access_token_secret: <ACCESS_SECRET>
```

## DataSource
[https://github.com/frefrik/covid19norge-data](https://github.com/frefrik/covid19norge-data) (accessed through [covid19norge.no/api](https://covid19norge.no/api))

## Features

- **Live updates**
  - Tested
  - Confirmed cases
  - Deaths
  - Admissions
  - Respiratory
  - Vaccine doses
  - Smittestopp
- **Graphs**
  - Tested
  - Confirmed cases
  - Dead
  - Hospitalized
  - Vaccine doses
  - Smittestopp
- **RSS**
  - News from FHI (Folkehelseinstituttet)
  - News from the goverment (Regjeringen)

## Screenshots

<details open>
<summary><b>Daily Summary Statistics</b></summary>

<p align="left">
<img width=415 alt="c19_graphs" src="https://user-images.githubusercontent.com/11590359/103143694-0b597300-471c-11eb-820c-ea3ed1913d73.png">
<img width=415 alt="c19_stats" src="https://user-images.githubusercontent.com/11590359/103143687-f846a300-471b-11eb-9e0b-a855099b4057.png">
</p>

</details>

<details>
<summary><b>Live updates</b> (click to expand)</summary>
<p align="left">
<img width=500 alt="c19_live" src="https://user-images.githubusercontent.com/11590359/103143763-3395a180-471d-11eb-9414-8230b4974ffc.png">
</p>
</details>

<details>
<summary><b>RSS</b> (click to expand)</summary>
<p align="left">
 <img width=415 alt="c19_rss-1" src="https://user-images.githubusercontent.com/11590359/103143703-35129a00-471c-11eb-82f4-f802ae3bbd0d.png">
 <img width=415 alt="c19_rss-2" src="https://user-images.githubusercontent.com/11590359/103143731-c1bd5800-471c-11eb-8437-c7a0a2086e91.png">
</p>
</details>

## Installation

### Docker
##### Create a file named `docker-compose.yml` and add the following:
```yaml
version: '3.8'

services:
  bot:
    container_name: covid19norge-twitter
    image: frefrik/covid19norge-twitter:latest
    restart: unless-stopped
    environment:
      - TZ=Europe/Oslo
    volumes:
      - ./config:/app/bot/config
      - ./data:/app/bot/data
```

##### Download and edit bot configuration
```shell
$ mkdir -p config \
  && wget https://raw.githubusercontent.com/frefrik/covid19norge-twitter/main/config/config.dist.yml -O config/config.yml
```

##### Start bot
```shell
$ docker-compose up -d
```

---
### git + Docker
##### Clone the repository
```shell
$ git clone https://github.com/frefrik/covid19norge-twitter.git
$ cd covid19norge-twitter/
```
##### Copy `config.dist.yml` to `config.yml` and edit configuration
```shell
$ cp config/config.dist.yml config/config.yml
```

##### Start bot
```shell
$ docker-compose up -d
```

---
### Command line
##### Install dependencies
```shell
$ pip install -r requirements.txt
```

##### Copy `config.dist.yml` to `config.yml` and edit configuration
```shell
$ cp config/config.dist.yml config/config.yml
```

##### Start bot
```shell
$ screen -dmS covid19norge-twitter python clock.py
```

##### Attaching to the screen
```shell
$ screen -r covid19norge-twitter
```

---

#### Docker Notes
##### Editing config
If `config.yaml` is updated while bot is running, the container must be restarted to use the updated config.
```shell
$ docker restart covid19norge-twitter
```
##### Bot logs
Use `docker logs -f covid19norge-twitter` to show informational logs.
