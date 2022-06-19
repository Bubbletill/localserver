from flask import Flask, request
from time import sleep
from gpiozero import JamHat
import json
import subprocess
from Adafruit_Thermal import *

app = Flask(__name__)
#jh = JamHat()
#printer = Adafruit_Thermal("/dev/usb/lp0")

with open('data.json', 'r') as datafile:
    data = json.loads(datafile.read())
    if int(data['regno']) != -1:
        subprocess.Popen(["java", "-jar", data["pos"]])
    else:
        subprocess.Popen(["java", "-jar", data["backoffice"]])


@app.route("/")
def service_version():
    return '{"service":"Bubbletill LOCALSERVER", "version": "22.0.1"}', 200


# Buzzer
@app.route('/buzzer/double')
def buzzer_double():
    jh.buzzer.play(69)
    sleep(0.2)
    jh.off()

    sleep(0.05)

    jh.buzzer.play(69)
    sleep(0.4)
    jh.off()
    return '', 200


@app.route('/buzzer/single')
def buzzer_single():
    jh.buzzer.play(69)
    sleep(0.2)
    jh.off()
    return '', 200


@app.route('/buzzer/singlelong')
def buzzer_singlelong():
    jh.buzzer.play(69)
    sleep(0.5)
    jh.off()
    return '', 200


# Local Data
@app.route('/info/regno')
def info_regno():
    with open('data.json', 'r') as datafile:
        data = json.loads(datafile.read())
        return '' + str(data['regno']), 200


@app.route('/info/storeno')
def info_storeno():
    with open('data.json', 'r') as datafile:
        data = json.loads(datafile.read())
        return '' + str(data['storeno']), 200


@app.route('/info/accesstoken')
def info_accesstoken():
    with open('data.json', 'r') as datafile:
        data = json.loads(datafile.read())
        return '' + str(data['token']), 200


@app.route('/print/receipt', methods=['POST'])
def print_receipt():
    if 'store' not in request.get_json() or 'reg' not in request.get_json() \
            or 'datetime' not in request.get_json() or 'oper' not in request.get_json() \
            or 'trans' not in request.get_json() or 'items' not in request.get_json() \
            or 'paydata' not in request.get_json() or 'copy' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    items = json.loads(request.get_json()['items'])
    tender = dict(items['tender'])

    printer.setDefault()

    printer.setSize("L")
    printer.justify("C")
    printer.boldOn()
    printer.underlineOn()
    printer.println("Bubbletill")

    printer.feed(2)
    printer.setSize("M")
    printer.underlineOff()
    printer.println("Sale")

    printer.feed(1)
    printer.setDefault()

    if bool(request.get_json()['copy']):
        printer.feed(1)
        printer.justify("C")
        printer.println("** Copy ** ")
        printer.justify("L")
        printer.feed(1)

    basketTotal = 0.00
    for i in items['basket']:
        category = int(i['category'])
        code = int(i['code'])
        description = i['description']
        ogprice = float(i['price'])
        reduction = float(i['priceReduction'])

        price = ogprice - reduction
        basketTotal += price

        printer.println("" + description + " - £" + str(price))
        printer.println("" + str(category) + "/" + str(code))

    printer.feed(1)
    printer.println("TOTAL £" + str(basketTotal))

    for key in tender:
        printer.println(key + " £" + str(tender[key]))

    printer.feed(3)
    printer.println("Store: " + request.get_json()['store'] + " | Reg: " + request.get_json()['reg'] + " | Trans: " + request.get_json()['trans'])
    printer.println("Oper: " + request.get_json()['oper'] + " | " + request.get_json()['datetime'])

    printer.feed(1)

    printer.justify("C")
    printer.printBarcode("1" + request.get_json()['store'] + request.get_json()['reg'] + request.get_json()['trans']
                         + "090622", printer.UPC_A)

    printer.println("** CUSTOMER COPY **")
    printer.feed(2)

    return "", 200


# Launch apps
@app.route('/launch/backoffice')
def launch_backoffice():
    with open('data.json', 'r') as datafile:
        data = json.loads(datafile.read())
        subprocess.Popen(["java", "-jar", data["backoffice"]])
        return '', 200


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5001)
