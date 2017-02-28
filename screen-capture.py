import PIL.ImageGrab, datetime, time, configparser, os

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(dir_path +'/config.ini')

storage = True if config['capture']['storage_file'] == '1' else False
sleep_time = float(config['capture']['sleep_time'])

while(True):
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S_%f')

	filename_analyze = "capture.jpg"
	filename_storage = str(st) +".jpg"
	snapshot = PIL.ImageGrab.grab()

	snapshot.save(dir_path +"/capture/" + filename_analyze)

	if(storage == True):
		snapshot.save(dir_path +"/storage/" + filename_storage)

	print("analyze screenshot by name: ", filename_analyze)

	if(storage == True):
		print("storage screenshot by name: ", filename_storage)

	time.sleep(sleep_time)
