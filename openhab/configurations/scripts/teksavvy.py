#!/usr/bin/env python3
import json, sys, re, paho.mqtt.client as mqtt, config, strings
from requests import get

_, APIKEY = config.creds.get(url=lambda x: 'teksavvy:api' in str(x))
if not APIKEY:
	print('no api key')
	sys.exit(1)

if __name__ == '__main__':
	headers = {"TekSavvy-APIKey": APIKEY}
	response = get(strings.urls['tsi'], headers=headers).content
	data = json.loads(response.decode('utf-8'))

	# for convenience
	pd  = data["value"][0]["OnPeakDownload"]
	pu  = data["value"][0]["OnPeakUpload"]
	opd = data["value"][0]["OffPeakDownload"]
	opu = data["value"][0]["OffPeakUpload"]
	sd  = data["value"][0]["StartDate"]
	ed  = data["value"][0]["EndDate"]

	client = mqtt.Client()
	client.connect(config.mqtt_broker)
	client.loop_start()
	client.publish('/stats/internet/dl/peak', str(pd))
	client.publish('/stats/internet/ul/peak', str(pu))
	client.publish('/stats/internet/dl/offpeak', str(opd))
	client.publish('/stats/internet/ul/offpeak', str(opu))
	client.publish('/stats/internet/asof', re.sub('([0-9]*-[0-9]*-[0-9]*)T.*', '\\1', str(ed)))
	client.publish('/stats/internet/sum', str(pd + pu + opd + opu))
	client.loop_stop()
