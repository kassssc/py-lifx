#!/usr/bin/env python
# coding=utf-8
import sys

from lifxlan import LifxLAN
import json

def main():

    MAIN_MENU_COMMANDS = (
        "Enter a light name to select it\n"
        "\tOR\n"
        "Enter one of the commands:\n"
        "\tAll lights on: 'all on', 'on'\n"
        "\tAll lights off: 'all off' 'off'\n"
        "\tQuit program: 'q'"
    )
    LIGHT_COMMANDS = (
        "Commands:\n"
        "\tPower On: 'on', '1'\n"
        "\tPower Off: 'off', '0'\n"
        "\tToggle Power: 'toggle', 't'\n"
        "\tBrightness Up: 'b+', '+'\n"
        "\tBrightness Down: 'b-', '-'\n"
        "\tBack to main menu: 'q'"
    )

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
    print("Discovering lights...")
    lifx = LifxLAN(num_lights)

    # get devices
    devices = lifx.get_lights()
    print("\nFound {} light(s):\n".format(len(devices)))
    for d in devices:
        try:
            print(d)
        except:
            pass

    print(MAIN_MENU_COMMANDS)
    while True:
        user_input = input("Enter your command: ")

        if user_input.lower() == 'q':
            sys.exit()
        elif user_input == "":
            continue
        elif user_input.lower() == "all on" or user_input.lower() == "on":
            lifx.set_power_all_lights("on")
            continue
        elif user_input.lower() == "all off" or user_input.lower() == "off":
            lifx.set_power_all_lights("off")
            continue

        light = get_light(devices, user_input)

        if light is None:
            print("Light not found")
            continue

        # Device command Loop
        print(LIGHT_COMMANDS)
        while True:
            command = input("Enter a command for {}: ".format(user_input))

            if command == 'on' or command == '1':
                light.set_power("on")
            elif command == 'off' or command == '0':
                light.set_power("off")
            elif command == 'toggle' or command == 't':
                curr_power = light.get_power()
                if curr_power > 0:
                    light.set_power("off")
                else:
                    light.set_power("on")
            elif command.lower() == 'b+' or command == '+':
                color = light.get_color()
                light.set_color((color[0], color[1], cap_brightness(color[2] + 10000), color[3]))
            elif command.lower() == 'b-' or command == '-':
                color = light.get_color()
                light.set_color((color[0], color[1], cap_brightness(color[2] - 10000), color[3]))
            elif command.lower() == 'q':
                break


def get_light(device_list, label):
    for device in device_list:
        if device.label.lower() == label.lower():
            return device

def cap_brightness(b):
    if b >= 65535:
        return 65535
    if b < 0:
        return 0
    return b

if __name__=="__main__":
    main()