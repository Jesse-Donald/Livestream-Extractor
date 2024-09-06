import os
import json

def getConfig():
    with open('config.json') as f:
        config = json.load(f)
        return(config)

def getTimes():
    with open('times.json') as f:
        config = json.load(f)
        return(config)
