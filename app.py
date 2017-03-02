import sys, PIL.ImageGrab, datetime, time, configparser, os, shutil, philips
from PIL import Image
from pathlib import Path
from shutil import copyfile

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(dir_path +'/config.ini')

storage = True if config['capture']['storage_file'] == '1' else False
sleep_time = float(config['capture']['sleep_time'])



cil_x = 0
cil_y = 0

tmp_cil_x = 0
tmp_cil_y = 0

def calc_images_colors():
    global dir_path, cil_y, cil_x

    my_file = Path(dir_path + "/capture/capture.jpg")
    if my_file.is_file():
        copyfile(dir_path + "/capture/capture.jpg", dir_path + "/capture/capture_tmp.jpg")
        im = Image.open(dir_path + "/capture/capture_tmp.jpg")
        pix = im.load()

        """ Sample pixel pick points to capture-sample.jpg
        photo_pick_point = [2450,549] # Yellow
        photo_pick_point = [2571,800] # Red
        photo_pick_point = [780,412] # Blue
        """

        photo_pick_point = [int(config['philips.hue']['photo_x']),int(config['philips.hue']['photo_y'])]


        print("Photo size: ", im.size)
        print("RGB color: ", pix[photo_pick_point[0],photo_pick_point[1]])


        red = pix[photo_pick_point[0],photo_pick_point[1]][0]
        green = pix[photo_pick_point[0],photo_pick_point[1]][1]
        blue = pix[photo_pick_point[0],photo_pick_point[1]][2]

        red_val = pow((red + 0.055) / (1.0 + 0.055), 2.4) if red > 0.04045 else (red / 12.92)
        green_val = pow((green + 0.055) / (1.0 + 0.055), 2.4) if (green > 0.04045) else (green / 12.92)
        blue_val = pow((blue + 0.055) / (1.0 + 0.055), 2.4) if (blue > 0.04045) else (blue / 12.92)

        X = float(red_val * 0.664511 + green_val * 0.154324 + blue_val * 0.162028)
        Y = float(red_val * 0.283881 + green_val * 0.668433 + blue_val * 0.047685)
        Z = float(red_val * 0.000088 + green_val * 0.072310 + blue_val * 0.986039)

        cil_x = float(X / (X + Y + Z)) if X > 0 else 0
        cil_y = float(Y / (X + Y + Z)) if Y > 0 else 0

        screen_w = im.size[0]
        screen_h = im.size[1]

    os.remove(dir_path + "/capture/capture_tmp.jpg")

def screenshot():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S_%f')

    filename_analyze_save = "capture_save.jpg"
    filename_analyze = "capture.jpg"
    filename_storage = str(st) +".jpg"
    snapshot = PIL.ImageGrab.grab()

    snapshot.save(dir_path +"/capture/" + filename_analyze_save )

    if(storage == True):
        snapshot.save(dir_path +"/storage/" + filename_storage)

    print("analyze screenshot by name: ", filename_analyze)

    shutil.move(dir_path +"/capture/" + filename_analyze_save , dir_path +"/capture/" + filename_analyze)

    if(storage == True):
        print("storage screenshot by name: ", filename_storage)

while(True):

    screenshot()
    calc_images_colors()

    if(tmp_cil_x != cil_x or tmp_cil_y != cil_y):
        tmp_cil_x = cil_x
        tmp_cil_y = cil_y

        philips_hue = philips.Hue(config['philips.hue']['ip'], config['philips.hue']['username'])

        print(philips_hue.findAllLights())

        lights = config['philips.hue']['light_num'].split(',')

        print('')
        for light in lights:
            philips_hue.getLightData(int(light))
            philips_hue.changeLightColor(int(light),[cil_x, cil_y])

        print(philips_hue.data)

    time.sleep(sleep_time)
