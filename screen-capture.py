import PIL.ImageGrab, datetime, time

storage = True

while(True):
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S_%f')

	filename_analyze = "captura.jpg"
	filename_storage = str(st) +".jpg"
	snapshot = PIL.ImageGrab.grab()

	snapshot.save("capture\\" + filename_analyze)

	if(storage == True):
		snapshot.save("storage\\" + filename_storage)

	print("analyze screenshot by name: ", filename_analyze)

	if(storage == True):
		print("storage screenshot by name: ", filename_storage)

	time.sleep(0.5)
