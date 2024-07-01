#!/usr/bin/python3
# coding=utf8
# from contextlib import ExitStack
import sys

sys.path.append('/home/pi/TurboPi/')
sys.path.append('/home/pi/boot/')
import os
import cv2
import time
import math
import signal
import numpy as np
import argparse
import RPi.GPIO as GPIO
# import threading

# import yaml_handle
import HiwonderSDK.Board as Board
import HiwonderSDK.mecanum as mecanum

# typing
from typing import Any

import warnings
try:
    import buttonman as buttonman
    buttonman.TaskManager.register_stoppable()
except ImportError:
    buttonman = None
    warnings.warn("buttonman was not imported, so no processes can be registered. This means the process can't be stopped by buttonman.",  # noqa: E501
                  ImportWarning, stacklevel=2)


KEY1_PIN = 33
KEY2_PIN = 16
KDN = GPIO.LOW
KUP = GPIO.HIGH

range_bgr = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}


class MoveProgram:
    def __init__(self,
        dry_run: bool = False,
        board=None,
        pause=False,
        startup_beep=True,
        exit_on_stop=True
    ) -> None:
        self._run = not pause
        self.dry_run = dry_run
        self.chassis = mecanum.MecanumChassis()

        self.board = Board if board is None else board

        GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.countin = ([500, 500] * 3) + [1000, 0]
        self.countout = ([500, 500] * 3) + [100, 50]

        if buttonman:
            self.key1_debouncer = buttonman.ButtonDebouncer(KEY1_PIN, self.btn1, bouncetime=50)
            self.key1_debouncer.start()
            GPIO.add_event_detect(KEY1_PIN, GPIO.BOTH, callback=self.key1_debouncer)

        if startup_beep:
            Board.setBuzzer(1)
            time.sleep(0.05)
            Board.setBuzzer(0)

        self.exit_on_stop = exit_on_stop

    def btn1(self, channel, event):
        if event == KUP:
            if self.dry_run or not self._run:
                self.dry_run = False
                self._run = True
            else:
                self.dry_run = True
                self.kill_motors()

    def kill_motors(self):
        self.chassis.set_velocity(0, 0, 0)

    def pause(self):
        self._run = False
        self.chassis.set_velocity(0, 0, 0)
        print(f"{__name__} Paused w/ PID: {os.getpid()} Camera still open...")

    def resume(self):
        self._run = True
        print(f"{__name__} Resumed")

    def stop(self):
        self._run = False
        self.chassis.set_velocity(0, 0, 0)
        self.set_rgb('None')
        cv2.destroyAllWindows()
        print(f"{__name__} Stop")
        if buttonman:
            buttonman.TaskManager.unregister()
        if self.exit_on_stop:
            sys.exit()  # exit the python script immediately

    def set_rgb(self, color):
        # Set the RGB light color of the expansion board to match the color you want to track
        if color not in range_bgr:
            color = "black"
        b, g, r = range_bgr[color]
        self.board.RGB.setPixelColor(0, self.board.PixelColor(r, g, b))
        self.board.RGB.setPixelColor(1, self.board.PixelColor(r, g, b))
        self.board.RGB.show()

    def go(self):
        self.set_rgb('blue')
        p, a, w = self.controls
        if not self.dry_run:
            self.chassis.set_velocity(100, 90, -0.5)  # Control robot movement function

    def loop(self):
        self.go()

    def main(self):

        def sigint_handler(sig, frame):
            self.stop()

        def sigtstp_handler(sig, frame):
            self.pause()

        def sigcont_handler(sig, frame):
            self.resume()

        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)
        signal.signal(signal.SIGTSTP, sigtstp_handler)
        signal.signal(signal.SIGCONT, sigcont_handler)

        try:
            if not self.countdown:
                self.go()
                time.sleep(self.t)
                self.stop()
                return
            while True:
                self.loop()
        except KeyboardInterrupt:
            self.stop()
            raise
        except BaseException as err:
            self.exit_on_stop = False
            self.stop()
            raise

        self.stop()


def get_parser(parser, subparser):
    parser.add_argument("--dry_run", action='store_true')
    parser.add_argument("--startpaused", action='store_true')
    return parser, subparser


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    get_parser(parser, None)
    args = parser.parse_args()

    program = MoveProgram(args)
    program.main()
