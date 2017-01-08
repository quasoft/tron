# TRON (ToRainOrNot) weather widget

*Under development*

## Vision statement

TRON is a widget that provides unsolicited advise on clothing and/or taking umbrella, based on weather forecast.

## Goals

### Minimal:
- [ ] Provide advise on schedule (provided by user in advance)
- [ ] Advise reminds you to take umbrella, jacket or hat
- [ ] Work on PC and mobile phone

### May be:
- [ ] Hardware device with some interface (lcd/audio/button) near the front door that:
    - [ ] detects when user is leaving home and plays unsolicited audio advise
    - [ ] has a simple push button for user to request advise 

## TODO:

### Server:
- [X] Write server app that provides weather data in json
- [X] Write tests for weather providers:
    * [X] location scrapping;
    * [X] downloading weather data.
- [ ] Add darksky.io provider
- [ ] Add setup.py script for server app

### Clients
- [ ] Create cross-platform PC application
- [ ] Create reponsive web application
- [ ] Create android application
