import paho.mqtt.client as mqtt
import os, cec, time, signal, threading, sys
# redirect all output to stderr
sys.stdout = sys.stderr

def get_cec_conn():
	cecconfig = cec.libcec_configuration()
	cecconfig.strDeviceName = "pyLibCec"
	cecconfig.bActivateSource = 0
	cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
	cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
	return cec.ICECAdapter.Create(cecconfig)

lib = get_cec_conn()
# previously used the context to open and close on demand; driver doesn't like that
# so just open it once
lib.Open('RPI')
class cec_context():
	def __init__(self):
		self.lib = None
	def __enter__(self):
		global lib
		#self.lib = get_cec_conn()
		#self.lib.Open('RPI')
		#return self.lib
		return lib
	def __exit__(self, *args):
		#self.lib.Close()
		pass

def on_connect(client, userdata, flags, rc):
	client.subscribe("/tv/update/power")
	client.subscribe("/tv/update/permission")

powered_via_hab = False
permission_allowed = False
power_lock = threading.Lock()

def on_message(client, userdata, msg):
	global powered_via_hab, power_lock, permission_allowed
	if msg.topic == '/tv/update/permission':
		power_lock.acquire()
		try:
			print 'Setting TV usage permission: ',
			permission_allowed = str(msg.payload) in ('ON', '1')
			print str(permission_allowed)
			client.publish('/tv/state/permission', 'ON' if permission_allowed else 'OFF')
		except:
			pass
		finally:
			power_lock.release()
	elif msg.topic == '/tv/update/power':
		m = str(msg.payload) in ('ON', '1')
		power_lock.acquire()
		try:
			if m:
				print 'Powering on TV via openhab'
				with cec_context() as lib:
					if lib.GetDevicePowerStatus(cec.CECDEVICE_TV) == cec.CEC_POWER_STATUS_STANDBY:
						lib.PowerOnDevices(cec.CECDEVICE_TV)
					print '	Waiting for power status to update'
					while lib.GetDevicePowerStatus(cec.CECDEVICE_TV) != cec.CEC_POWER_STATUS_ON:
						time.sleep(1)
					print '	Powered on via openhab'
					client.publish('/tv/state/power', 'ON')
					powered_via_hab = True
			else:
				print 'Powering off TV via openhab'
				with cec_context() as lib:
					if lib.GetDevicePowerStatus(cec.CECDEVICE_TV) == cec.CEC_POWER_STATUS_ON:
						lib.StandbyDevices(cec.CECDEVICE_TV)
					print '	Waiting for power status to update'
					while lib.GetDevicePowerStatus(cec.CECDEVICE_TV) != cec.CEC_POWER_STATUS_STANDBY:
						time.sleep(1)
					print '	Powered off via openhab'
					client.publish('/tv/state/power', 'OFF')
					powered_via_hab = False
		finally:
			power_lock.release()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

def sigterm_handler(_signo, _stack_frame):
	sys.exit(0)
signal.signal(signal.SIGTERM, sigterm_handler)

client.connect('pellet.cave.kevinross.name')
client.loop_start()
shutted = False
def shutdown():
	global shutted
	if shutted:
		return
	shutted = True
	client.unsubscribe('/tv/update/power')
	client.unsubscribe('/tv/update/permission')
	client.loop_stop()

def convert_state_to_str(state):
	states = [x for x in dir(cec) if 'CEC_POWER_STATUS' in x]
	states = [x for x in states if getattr(cec, x) == state]
	if states:
		return states[0]
	
# check for permission (openhab message or something)
try:
	while True:
		if power_lock.acquire(False):
			with cec_context() as lib:
				state = lib.GetDevicePowerStatus(cec.CECDEVICE_TV)
				if state == cec.CEC_POWER_STATUS_ON and not (powered_via_hab or permission_allowed):
					print 'TV powered on but not authorized, shutting off'
					lib.StandbyDevices(cec.CECDEVICE_TV)
					print '	Waiting for power status to update'
					while lib.GetDevicePowerStatus(cec.CECDEVICE_TV) != 1:
						time.sleep(1)
					print '	Powered off via house policy'
				if state == cec.CEC_POWER_STATUS_ON:
					client.publish('/tv/state/power', 'ON')
				elif state == cec.CEC_POWER_STATUS_STANDBY:
					client.publish('/tv/state/power', 'OFF')
				else:
					print convert_state_to_str(state)
					client.publish('/tv/state/power', 'UNDEFINED')
				client.publish('/tv/state/permission', 'ON' if permission_allowed else 'OFF')
			power_lock.release()
		time.sleep(10)
except KeyboardInterrupt:
	pass
finally:
	shutdown()
