""" ultra fuego web service for playing with an RGB led matrix
"""

import argparse
import base64
import datetime
import logging
import os
import re
import sys
import time
import json
import socket
import fcntl
import struct


from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response, render_template, send_from_directory
from flask_cors import CORS
from io import BytesIO
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from time import sleep
from threading import Thread, Timer, Event
from urllib.request import urlopen


DIR = os.path.dirname(os.path.realpath(__file__))
FONT_DIR = os.path.join(DIR, "rpi-rgb-led-matrix", "fonts")


# Set up logging
logger = logging.getLogger(__name__)
loggingHandler = logging.StreamHandler(sys.stdout)
loggingHandler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s %(message)s"))
logger.addHandler(loggingHandler)
logger.setLevel(logging.INFO)


# Set up matrix
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 6
options.parallel = 1
options.hardware_mapping = 'regular'
options.gpio_slowdown = 2
matrix = RGBMatrix(options=options)


# Set up threading
gif = False
clock = False
funky = False
runningtext = False
addressaIp = False
countDown = False
matrix_clear_event = Event()
# mark as clear, this means no threads are currently rendering on a loop
matrix_clear_event.set()


# HTTP API
app = Flask(__name__)
CORS(app)



@app.route("/reset")
def resetator():
    global gif
    global clock
    global funky
    global runningtext
    global addressaIp
    global countDown
    if not matrix_clear_event.is_set():
        gif = False
        clock = False
        funky = False
        runningtext = False
        addressaIp = False
        countDown = False
        logger.info("Waiting for matrix clear")
        matrix_clear_event.wait()
    render_clear()
    return render_template('index.tmpl')    


@app.route("/")
@app.route("/index")
def home():
    """Heartbeat
    """
    return render_template('index.tmpl')


@app.route("/painting")
def painting():
	return render_template("painting.tmpl");


@app.route("/runningtext", methods=['GET', 'POST'])
def run_text_message():
    """Receive a text message
    """
    if request.method != 'POST':
        return render_template('runningtext.tmpl')

    resetator()
    global runningtext
    runningtext = True

    msg = request.json["message"]
    barva = request.json["barva"]
    logger.info("New message: " + msg)

    Thread(target=render_runningtext, args=(msg,barva,)).start()

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/clockcountdown", methods=['GET', 'POST'])
def run_clock_count_down():
    """Receive a text message
    """
    if request.method != 'POST':
        return render_template('clockcountdown.tmpl')

    resetator()
    global countDown
    countDown = True

    cas = request.json["cas"]
    barva = request.json["barva"]

    hlaska = request.json["hlaska"]


    Thread(target=render_countDown, args=(barva,cas,hlaska)).start()

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/text", methods=["POST"])
def text_message():
    """Receive a text message
    """
    resetator()
    msg = request.json["message"]
    barva = request.json["barva"]
    logger.info("New message: " + msg)
    render_text(msg,barva)
    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/img/<format>", methods=["POST"])
def image(format):
    """Receive a text message
    """
    if format == "png":
        img_b64 = request.json["img"]
        img_formatted = re.sub("^data:image/.+;base64,", "", img_b64)
        img = Image.open(BytesIO(base64.b64decode(img_formatted))).convert("RGB")
    elif format == "url":
        data = BytesIO(urlopen(request.json["url"]).read())
        img = Image.open(data)
    else:
        return make_response(jsonify({"message": "unsupported format"}), 415)

    try:
        render_image(img)
    except:
        return make_response(jsonify({"message": "could not render image"}), 500)

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/gif", methods=["POST"])
def gif_():
    """Display GIF from URL
    """
    global gif
    gif = True
    url = request.json["url"]
    data = BytesIO(urlopen(url).read())
    gif = Image.open(data)
    Thread(target=render_gif, args=(gif,)).start()
    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/clock", methods=['GET', 'POST'])
def clock_():
    """Display the time
    """

    if request.method != 'POST':
        return render_template('clock.tmpl')

    resetator()
    global clock
    clock = True
    barva = request.json["barva"]
    Thread(target=render_clock, args=(barva,)).start()

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/funky", methods=["GET"])
def funky_():
    """
    """
    resetator()
    global funky

    funky = True
    Thread(target=render_funky).start()

    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/color-match", methods=["POST"])
def color_match_():
    """
    """
    #color_match()
    return make_response(jsonify({"message": "ok"}), 200)


@app.route("/clear", methods=["GET"])
def clear():
    """Clear the matrix
    """
    resetator()
    render_clear()
    return make_response(jsonify({"message": "ok"}), 200)


#
# Rendering functions
#


def loop_renderer(renderer):
    """Decorator for renderers that need to grab the display lock and release it
    when they're done
    """
    def f(*args):
        matrix_clear_event.clear()  # Lock matrix
        renderer(*args)
        render_clear()  # Clear matrix and release lock
    return f

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def render_text(text, barva):
    """Render a text message
    """
    global matrix

    fonts = {
        "small": {
            "name": "5x8.bdf",
            "n": 7
        },
        "medium": {
            "name": "6x10.bdf",
            "n": 7
        },
        "large": {
            "name": "10x20.bdf",
            "n": 20
        }
    }
    canvas = matrix.CreateFrameCanvas()
    font = graphics.Font()
    print(barva)
    print(hex_to_rgb(barva))
    text_color = graphics.Color(255, 255, 0)
    barva = hex_to_rgb(barva)
    text_color = graphics.Color(barva[0],barva[1],barva[2])
    if len(text) < 70:
        font_size = "large"
    elif len(text) < 130:
        font_size = "medium"
    else:
        font_size = "small"
    font.LoadFont(os.path.join(FONT_DIR, fonts[font_size]["name"]))
    lines = []
    line = ""
    for word in text.split(" "):
        if line == "":
            line += word
        else:
            if len(line + " " + word) < fonts[font_size]["n"]:
                line += " " + word
            else:
                lines.append(line)
                line = word
    lines.append(line)  # add the last line
    for i, line in enumerate(lines):
        x = 0
        y = i * font.baseline
        pos = {"x": x, "y": y + font.baseline}
        graphics.DrawText(canvas, font, pos["x"], pos["y"], text_color, line)

    matrix.SwapOnVSync(canvas)


def render_image(img):
    """Render a base64 encoded png
    """
    img.thumbnail((32, 32), Image.ANTIALIAS)
    canvas = matrix.CreateFrameCanvas()
    canvas.SetImage(img, (32 - img.size[0]) / 2, (32 - img.size[1]) / 2)
    matrix.SwapOnVSync(canvas)




@loop_renderer
def render_runningtext(my_text,barva):
    """Render the time on a 1 second loop
    """
    global runningtext
    global matrix

    barva = hex_to_rgb(barva)
    text_color = graphics.Color(barva[0],barva[1],barva[2])

    font = graphics.Font()
    font.LoadFont(os.path.join(FONT_DIR, "10x20.bdf"))

    canvas = matrix.CreateFrameCanvas()
    pos = canvas.width
    
    while runningtext:
        canvas = matrix.CreateFrameCanvas()

        len = graphics.DrawText(canvas, font, pos, 10, text_color, my_text)
        pos -= 1
        if (pos + len < 0):
            pos = canvas.width

        matrix.SwapOnVSync(canvas)

        time.sleep(0.1)       



@loop_renderer
def render_clock(barva):

    global clock
    global matrix

    barva = hex_to_rgb(barva)
    text_color = graphics.Color(barva[0],barva[1],barva[2])

    font = graphics.Font()
    font.LoadFont(os.path.join(FONT_DIR, "18x18ja.bdf"))

    while clock:
        rn = datetime.now()
        canvas = matrix.CreateFrameCanvas()

        hour = str(rn.hour)
        if rn.hour < 10:
            hour = "0" + hour
        minute = str(rn.minute)
        if rn.minute < 10:
            minute = "0" + minute
        sec = str(rn.second)
        if rn.second < 10:
            sec = "0" + sec     

        graphics.DrawText(canvas, font, 25, 20, text_color, hour+":"+minute+":"+sec)
        matrix.SwapOnVSync(canvas)
        time.sleep(0.2)



@loop_renderer
def render_ipAddress(barva):

    global addressaIp
    global matrix
    barva = hex_to_rgb(barva)
    text_color = graphics.Color(barva[0],barva[1],barva[2])

    font = graphics.Font()
    font.LoadFont(os.path.join(FONT_DIR, "10x20.bdf"))
    pocet = 0
    ipv4 = "zmerimTo.cz"
    while addressaIp:
        if pocet > 10:
            ipv4 = re.search(re.compile(r'(?<=inet )(.*)(?=\/)', re.M), os.popen('ip addr show eth0').read()).groups()[0]
        canvas = matrix.CreateFrameCanvas()
        graphics.DrawText(canvas, font, 25, 20, text_color, ipv4)
        matrix.SwapOnVSync(canvas)
        pocet+=1
        time.sleep(1)

def days_hours_minutes(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    seconds += td.microseconds / 1e6
    return hours, minutes, seconds

@loop_renderer
def render_countDown(barva, minute,hlaska):

    global countDown
    global matrix
    barva = hex_to_rgb(barva)
    text_color = graphics.Color(barva[0],barva[1],barva[2])

    font = graphics.Font()
    font.LoadFont(os.path.join(FONT_DIR, "10x20.bdf"))
    cas = datetime.now() + timedelta(minutes=int(minute))
    hours  = 9
    minutes  = 9
    secs = 9
    
    while countDown and not (hours == 23 and minutes == 59 and secs <= 60):
        rn = cas - datetime.now()
        hours, minutes, secs = days_hours_minutes(rn)

        canvas = matrix.CreateFrameCanvas()

        hour = str(hours)
        if hours < 10:
            hour = "0" + str(hours)
        minute = str(minutes)
        if minutes < 10:
            minute = "0" + str(minutes)
        
        sec = str(round(secs,1)) 
        if secs < 10:
            sec = "0" + str(round(secs,1))
         
        graphics.DrawText(canvas, font, 40, 20, text_color, hour+":"+minute+":"+sec)

        matrix.SwapOnVSync(canvas)
        time.sleep(0.03)
    
    countDown = False
    canvas = matrix.CreateFrameCanvas()       
    graphics.DrawText(canvas, font, 25, 20, text_color, hlaska)
    matrix.SwapOnVSync(canvas)    
    time.sleep(5)

        


@loop_renderer
def render_gif(jif):
    """Play a GIF
    """
    global gif

    # Create an array of frames
    frames = []
    palette = None
    try:
        while True:
            if palette is None:
                palette = jif.getpalette()
            frame = jif.copy()
            frame.putpalette(palette)
            frame = frame.convert("RGB")
            frame.thumbnail((32, 32), Image.ANTIALIAS)
            frames.append(frame)
            jif.seek(jif.tell() + 1)
    except EOFError:
        pass

    nframes = len(frames)
    idx = 0

    while gif:
        canvas = matrix.CreateFrameCanvas()
        frame = frames[idx]
        canvas.SetImage(frame, (32 - frame.size[0]) / 2, (32 - frame.size[1]) / 2)
        matrix.SwapOnVSync(canvas)
        idx = (idx + 1) % nframes
        sleep(0.05)


colors = [
    (209, 0, 0),     # red
    (255, 102, 34),  # orange
    (255, 218, 33),  # yellow
    (51, 221, 0),    # green
    (17, 51, 204),   # blue
    (34, 0, 102),    # indigo
    (51, 0, 68),     # violet
]


@loop_renderer
def render_funky():
    """Alternate ROYGBIV
    """
    global funky

    canvas = matrix.CreateFrameCanvas()
    idx = 0
    while funky:
        for x in range(0, matrix.width):
            for y in range(0, matrix.height):
                canvas.SetPixel(x, y, *colors[idx])
        matrix.SwapOnVSync(canvas)
        idx = (idx + 1) % len(colors)
        sleep(0.3)


def color_match():
    """
    """
    canvas = matrix.CreateFrameCanvas()
    #img = get_image()
    #colors = get_colors(img, 4)
    #print(colors)
    matrix.SwapOnVSync(canvas)


def render_clear():
    """Clear the matrix
    """
    logger.info("Clearing matrix")
    canvas = matrix.CreateFrameCanvas()
    matrix.SwapOnVSync(canvas)
    matrix_clear_event.set()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", dest="port", type=int, default=3000)
    args = parser.parse_args()

    addressaIp = True

    Thread(target=render_ipAddress, args=("#FFFFFF",)).start()
    app.run(host="0.0.0.0", port=args.port)
