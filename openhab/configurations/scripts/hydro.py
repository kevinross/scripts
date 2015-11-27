import selenium, selenium.webdriver, config, paho.mqtt.client as mqtt, strings, time, os, sys

username, password = config.creds.get(url=lambda x: 'hydro' in x)

if not username or not password:
	print 'no credentials available'
	sys.exit(1)

def ensure_content(sel, content):
	while content not in sel.page_source:
		print '.',
		time.sleep(1)
	print ''

def get_selenium():
	sel = selenium.webdriver.PhantomJS()
	sel.set_window_size(1280,800)
	return sel

def login():
	sel = get_selenium()
	print 'Opening homepage...',
	sel.get(strings.urls['home'])
	ensure_content(sel, strings.tests['home_initial'])
	print 'Logging in...',
	sel.find_element_by_id(strings.ids['username']).send_keys(username)
	sel.find_element_by_id(strings.ids['password']).send_keys(password)
	sel.find_element_by_xpath(strings.xpaths['signin']).click()
	ensure_content(sel, strings.tests['home_loggedin'])
	print 'Going to HydroLink...',
	sel.execute_script(strings.scripts['signin'])
	ensure_content(sel, strings.tests['asp_loggedin'])
	print 'Logged in'
	return sel

def get_estimated_bill(sel):
	print 'Getting estimation...',
	sel.get(strings.urls['predict'])
	ensure_content(sel, strings.tests['predict'])
	e = sel.find_element_by_id(strings.ids['predict']['amount'])
	amount = e.text
	e = sel.find_element_by_id(strings.ids['predict']['period'])
	# bunch of stuff then 'period: Month Day - Month Day (xx days)' then more stuff
	words = e.text.split()
	# pop off from front until 'period:'
	while words.pop(0) != 'period:':
		pass
	# pop off from back until 'days)'
	while words.pop(-1) != 'days)':
		pass
	length = words.pop(-1).strip('(')
	# ['Nov','13,','2015','-','Dec','11,','2015']
	period = ' '.join(words)
	print 'Got it'
	return (amount, length, period)

def get_current_usage(sel):
	print 'Getting current usage...',
	sel.get(strings.urls['usage'])
	ensure_content(sel, strings.tests['usage'])
	e = sel.find_element_by_id(strings.ids['usage']['table'])
	as_of = e.text.replace('Daily View (','').strip(')')
	def amnt(k):
		return sel.find_element_by_id(strings.ids['usage']['cell'] % k).text
	off_peak = amnt('Low')
	mid_peak = amnt('Mid')
	on_peak = amnt('High')
	print 'Got it'
	return (as_of, off_peak, mid_peak, on_peak)

if __name__ == '__main__':
	client = mqtt.Client()
	client.connect(config.mqtt_broker)
	client.loop_start()
	sel = login()
	amount, length, period = get_estimated_bill(sel)
	asof, off_peak, mid_peak, on_peak = get_current_usage(sel)
	print 'Notifying...',
	for i in ('amount', 'length', 'period', 'asof', 'off_peak', 'mid_peak', 'on_peak'):
		client.publish('/stats/hydro/%s' % i, eval(i).encode('ascii').replace('$',''))
	client.loop_stop()
	print 'done'
