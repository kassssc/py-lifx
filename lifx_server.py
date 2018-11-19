#!/usr/bin/env python
# coding=utf-8
import sys
import time
import json

from lifxlan import LifxLAN
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = 'localhost'
PORT_NUMBER = 6969

class Server:
    def __init__(self):
        self.server = HTTPServer((HOST_NAME, PORT_NUMBER), ReqHandler)

        self.server.get_path = '/lifx/status'
        self.server.post_path = '/lifx'

        print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
        num_lights = None

        if len(sys.argv) != 2:
            print("\nDiscovery will go much faster if you provide the number of lights on your LAN:")
            print("  python {} <number of lights on LAN>\n".format(sys.argv[0]))
        else:
            num_lights = int(sys.argv[1])

        # instantiate LifxLAN client, num_lights may be None (unknown).
        # In fact, you don't need to provide LifxLAN with the number of bulbs at all.
        # lifx = LifxLAN() works just as well. Knowing the number of bulbs in advance
        # simply makes initial bulb discovery faster.
        print("\nSearching for lights...")
        self.server.lifx = LifxLAN(num_lights)

        # get devices
        self.server.devices = self.server.lifx.get_lights()
        if len(self.server.devices) == 0:
            print("No LIFX lights found on network")
            sys.exit(0)

        print("Found {} LIFX light(s):".format(len(self.server.devices)))
        for d in self.server.devices:
            try:
                print('\t' + d.get_label())
            except:
                pass

        try:
            print("Awaiting commands...")
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.server_close()
            print('\n', time.asctime(), 'Server Stops - %s:%s\n' % (HOST_NAME, PORT_NUMBER))
            sys.exit(0)

class ReqHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == self.server.get_path:
            self.respond(200, json.dumps({'status': "OK"}))
        else:
            self.respond(404)

    def do_POST(self):
        if self.path != self.server.post_path:
            self.respond(404)
            return
        # refuse to receive non-json content
        payload_type = self.headers['content-type']
        if payload_type != 'application/json':
            self.respond(400)
            return

        # Get Dictionary of Post payload
        length = int(self.headers['content-length'])
        raw_payload = self.rfile.read(length)
        try:
            payload = json.loads(raw_payload)
            json_response = self.handle_light_command(payload)
        except Exception as e:
            self.respond(400)
        self.respond(200, json_response)

    def respond(self, status_code, json_response=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if json_response is not None:
            self.wfile.write(json_response.encode('utf-8'))

    def handle_light_command(self, payload):
        command = payload['command']
        command_text = ""

        if len(payload) == 1:
            if command.lower() == "all on" or command.lower() == "on":
                command_text = "All lights on command received"
                self.server.lifx.set_power_all_lights("on")
            elif command.lower() == "all off" or command.lower() == "off":
                command_text = "All lights off command received"
                self.server.lifx.set_power_all_lights("off")

        else:
            light_label = payload['light_label']
            light = self.get_light(light_label)
            command_text = "{} command to {} received".format(command, light_label)

            if command.lower() == 'on':
                light.set_power("on")
            elif command.lower() == 'off':
                light.set_power("off")
            elif command.lower() == 'toggle' or command.lower() == 't':
                curr_power = light.get_power()
                if curr_power > 0:
                    light.set_power("off")
                else:
                    light.set_power("on")
            elif command.lower() == 'b+' or command == '+':
                color = light.get_color()
                light.set_color((
                    color[0],
                    color[1],
                    self.cap_brightness(color[2] + 10000),
                    color[3]
                ))
            elif command.lower() == 'b-' or command == '-':
                color = light.get_color()
                light.set_color((
                    color[0],
                    color[1],
                    self.cap_brightness(color[2] - 10000),
                    color[3]
                ))

        return json.dumps({"msg": command_text})

    def get_light(self, label):
        for device in self.server.devices:
            if device.label.lower() == label.lower():
                return device

    def cap_brightness(self, b):
        if b >= 65535:
            return 65535
        if b < 0:
            return 0
        return b

if __name__=="__main__":
    server = Server()