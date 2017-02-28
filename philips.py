import requests, re, sys

class Hue:
    data = {}

    __bridge_url = ''
    __light_num = 0
    __hue_bri_max = 254
    bridge_online = None
    light_status = []

    def __init__(self, bridge, username):
        self.__bridge_url = 'http://'+ bridge +'/api/'+ username +'/'

    def getLightData(self,num=0):
        self.data = {}
        self.__light_num = int(num)

        try:
            if(self.__light_num > 0):
                response = requests.get(self.__bridge_url +'lights/'+ str(self.__light_num))
            else:
                response = requests.get(self.__bridge_url +'lights')

            self.bridge_online = True
            self.data = response.json()

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            self.bridge_online = False

    def changeLightColor(self,light_num,cil_xy):
        r = requests.put(self.__bridge_url +'lights/'+ str(light_num) +'/state', json={"on": True, "bri":255,"xy":cil_xy })

    def __handleLight(self,state, light_num):
        light_data = self.data

        if(str(light_num) in self.data):
            light_data = self.data[light_num]

        if(state == True):
            if((str(light_num) in self.data and self.data[light_num]['state']['on'] == True) or ('state' in self.data and self.data['state']['on'] == True) ):
                self.light_status.append({
                    'status' : '208',
                    'num' : light_num,
                    'modelid' : light_data['modelid'],
                    'uniqueid' : str(light_data['uniqueid'].split('-')[0]),
                    'swversion' : light_data['swversion'],
                    'state' : {
                        'on' : True
                    }
                })

            else:
                r = requests.put(self.__bridge_url +'lights/'+ str(light_num) +'/state', json={"on": True, "bri": int(self.__hue_bri_max)})
                if(r.status_code == 200):
                    self.light_status.append({
                        'status' : '200',
                        'num' : light_num,
                        'modelid' : light_data['modelid'],
                        'uniqueid' : str(light_data['uniqueid'].split('-')[0]),
                        'swversion' : light_data['swversion'],
                        'state' : {
                            'on' : True
                        }
                    })

                else:
                    self.light_status.append({
                        'status' : '404',
                        'num' : light_num,
                        'uniqueid' : str(light_data['uniqueid'].split('-')[0]),
                        'swversion' : light_data['swversion'],
                        'error' : 'Error!'
                    })

        elif(state == False):
            if((str(light_num) in self.data and self.data[light_num]['state']['on'] == False) or ('state' in self.data and self.data['state']['on'] == False) ):
                self.light_status.append({
                    'status' : '208',
                    'num' : light_num,
                    'modelid' : light_data['modelid'],
                    'uniqueid' : str(light_data['uniqueid'].split('-')[0]),
                    'swversion' : light_data['swversion'],
                    'state' : {
                        'on' : False
                    }
                })
            else:
                r = requests.put(self.__bridge_url +'lights/'+ str(light_num) +'/state', json={"on": False})
                if(r.status_code == 200):
                    self.light_status.append({
                        'status' : '200',
                        'num' : light_num,
                        'modelid' : light_data['modelid'],
                        'uniqueid' : str(light_data['uniqueid'].split('-')[0]),
                        'swversion' : light_data['swversion'],
                        'state' : {
                            'on' : False
                        }
                    })

                else:
                    self.light_status.append({
                        'status' : '404',
                        'num' : light_num,
                        'uniqueid' : str(light_data['uniqueid'].split('-')[0]),
                        'swversion' : light_data['swversion'],
                        'error' : 'Error!'
                    })

    def lightOn(self,state):
        self.light_status = []

        if(self.__light_num > 0):
            self.__handleLight(state, self.__light_num)
        else:
            for lights in self.data:
                self.__handleLight(state, lights)

    def findAllLights(self):
        self.getLightData()
        if(len(self.data) > 0):
            lights = []

            for light in self.data:
                lights.append({
                    'id' : light,
                    'swversion' : self.data[light]['swversion'],
                    'uniqueid' : str(self.data[light]['uniqueid'].split('-')[0]),
                    'modelid' : self.data[light]['modelid'],
                    'state' : {
                        'on' : self.data[light]['state']['on'],
                        'bri' : self.data[light]['state']['bri']
                    }
                })

            return lights
        else:
            if(self.bridge_online == False):
                return {
                    'status' : 500,
                    'msg' : 'Philips Hue Bridge is offline'
                }
            else:
                return {
                    'status' : 500,
                    'msg' : 'Philip Hue found no lights'
                }

    def findAllSensors(self):
        self.data = {}
        response = requests.get(self.__bridge_url +'sensors')
        self.data = response.json()

        sensors = {}

        for data in self.data:
            if('uniqueid' in self.data[data]):
                uniqueid = str(self.data[data]['uniqueid'].split('-')[0])
            else:
                continue

            if(len(uniqueid.split(':')) != 8):
                continue

            if(uniqueid not in sensors):
                sensors[uniqueid] = {
                    'uniqueid' : uniqueid,
                    'battery' : None,
                    'modelid' : str(self.data[data]['modelid']),
                    'sensors' : []
                }

            tmp_sensor = {
                'id' : str(data),
                'state' : {}
            }


            if(self.data[data]['type'] == 'ZLLPresence'):
                tmp_sensor['state'] = {
                    'type' : 'Presence',
                    'value' : str(self.data[data]['state']['presence'])
                }

            if(self.data[data]['type'] == 'ZLLTemperature'):
                tmp_sensor['state'] = {
                    'type' : 'Temperature',
                    'value' : int(self.data[data]['state']['temperature'])
                }

            if(self.data[data]['type'] == 'ZLLLightLevel'):
                tmp_sensor['state'] = {
                    'type' : 'LightLevel',
                    'value' : int(self.data[data]['state']['lightlevel'])
                }

            if(sensors[uniqueid]['battery'] is None and 'config' in self.data[data] and 'battery' in self.data[data]['config'] and self.data[data]['config']['battery'] != 'None'):
                sensors[uniqueid]['battery'] = int(self.data[data]['config']['battery'])

            sensors[uniqueid]['sensors'].append(tmp_sensor)

        return sensors

    def getSensorData(self, num):
        response = requests.get(self.__bridge_url +'sensors/'+ num)
        self.data = {}
        self.data = response.json()

        uniqueid = str(self.data['uniqueid'].split('-')[0])

        sensor = {
            'uniqueid' : uniqueid,
            'modelid' : self.data['modelid'],
            'swversion' : self.data['swversion'],
            'type' : None,
            'state' : {}
        }

        if(self.data['type'] == 'ZLLPresence'):
            sensor['type'] = 'presence'
            sensor['state'] = {
                'value' : 1 if self.data['state']['presence'] == True else 0
            }

        elif(self.data['type'] == 'ZLLTemperature'):
            sensor['type'] = 'temperature'
            sensor['state'] = {
                'value' : int(self.data['state']['temperature'])
            }

        elif(self.data['type'] == 'ZLLLightLevel'):
            sensor['type'] = 'lightlevel'
            sensor['state'] = {
                'value' : int(self.data['state']['lightlevel'])
            }

        return sensor
