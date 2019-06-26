import json
import requests

route = 4
sender = '1SHARE'

class Base():

    baseUrl = "http://control.msg91.com/api/"
    authkey = ''
    
    @staticmethod
    def actionURLBuilder(actionurl):
        return Base.baseUrl + str(actionurl)

    @staticmethod
    def call(actionurl, args):
        url = Base.actionURLBuilder(actionurl)
        payload = (args)
        response = requests.post(url, data=payload, verify=False)
        return response

class Message:

    def __init__(self, key):

        Base.authkey = key

    def set_route(self, new_route):
        global route
        route = new_route 

    def set_sender(self, new_sender):
        global sender
        sender = new_sender 

    def send (self, send_values):
        global sender
        global route
        default_value = {
            'authkey' : Base.authkey,
            'response' : 'json',
            'route' : route,
            'sender' : sender
        }

        values = {}
        values.update(default_value)
        values.update(send_values)

        response = Base.call('sendhttp.php', values)
        return response