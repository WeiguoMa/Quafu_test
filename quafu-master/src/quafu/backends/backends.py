import requests
import json
import re
import networkx as nx

class Backend(object):
    def __init__(self, name):
        self.name = name

    def get_info(self, url, api_token):
        data = {"system_name": self.name.lower()}
        headers={"api_token": api_token}
        chip_info = requests.post(url = url + "qbackend/scq_get_chip_info/", data=data, 
        headers=headers)

        backend_info = json.loads(chip_info.text)
       
        return backend_info


class ScQ_P10(Backend):
    def __init__(self):
        super().__init__("ScQ-P10")

class ScQ_P20(Backend):
    def __init__(self):
        super().__init__("ScQ-P20")

class ScQ_P50(Backend):
    def __init__(self):
        super().__init__("ScQ-P50")