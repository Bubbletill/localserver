from flask import Flask, request
from time import sleep
from gpiozero import JamHat
import json
import subprocess
from Adafruit_Thermal import *
from types import SimpleNamespace

app = Flask(__name__)
# jh = JamHat()
# printer = Adafruit_Thermal("/dev/usb/lp0")

with open('data.json', 'r') as datafile:
    data = json.loads(datafile.read())
    if int(data['regno']) == -1:
        subprocess.Popen(["java", "-jar", data["backoffice"]])
    elif int(data['regno']) > 0:
        subprocess.Popen(["java", "-jar", data["pos"]])


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

@app.route('/info/backend')
def info_backend():
    with open('data.json', 'r') as datafile:
        data = json.loads(datafile.read())
        return '' + str(data['backend']), 200


@app.route('/print/receipt', methods=['POST'])
def print_receipt():
    if 'store' not in request.get_json() or 'reg' not in request.get_json() \
            or 'datetime' not in request.get_json() or 'oper' not in request.get_json() \
            or 'trans' not in request.get_json() or 'items' not in request.get_json() \
            or 'paydata' not in request.get_json() or 'copy' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    items = json.loads(request.get_json()['items'])
    tender = dict(items['tender'])

    print_basics("Sale")

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
    printer.println("Store: " + request.get_json()['store'] + " | Reg: " + request.get_json()['reg'] + " | Trans: " +
                    request.get_json()['trans'])
    printer.println("Oper: " + request.get_json()['oper'] + " | " + request.get_json()['datetime'])

    printer.feed(1)

    printer.justify("C")
    printer.setBarcodeHeight(100)
    printer.printBarcode("123456789", printer.UPC_A)

    printer.println("** CUSTOMER COPY **")
    printer.feed(2)

    return "", 200


@app.route('/print/xread', methods=['POST'])
def print_xread():
    if 'data' not in request.get_json():
        return '{"success": false, "message":"Incomplete request."}', 200

    data = json.loads(request.get_json()['data'], object_hook=lambda d: SimpleNamespace(**d))

    print_basics("X Read")

    printer.println("Store: " + str(data.store))
    printer.println("Reg: " + str(data.register))
    printer.println("Oper: " + data.operator)
    printer.println("Date Time: " + data.requestDateTime)
    printer.println("Reg Opened: " + data.regOpened)
    printer.println("Reg Closed: " + data.regClosed)

    printer.feed(2)

    print_medium_title("Sale Summary")
    print_key_value("Trans. Count", "" + str(data.transactionCount))
    print_key_value("Units Sold", "" + str(data.unitsSold))
    print_key_value("Grand Total", "£" + str('{0:.2f}'.format(data.grandTotal)))

    printer.feed(2)
    print_medium_title("Sales Categories")
    percat = vars(data.totalPerCategory)
    for cat in percat:
        print_key_value(str(cat), "£" + str('{0:.2f}'.format(percat[cat])))

    printer.feed(2)
    print_medium_title("Payment Details")
    perpaytype = vars(data.totalPerPaymentType)
    for det in perpaytype:
        print_key_value(str(det), "£" + str('{0:.2f}'.format(perpaytype[det])))

    printer.feed(1)
    print_key_value("Calculated CID", "£" + str('{0:.2f}'.format(data.cashInDraw)))
    print_key_value("System CID", "£" + str('{0:.2f}'.format(data.systemCashInDraw)))

    printer.feed(2)
    print_medium_title("Transaction Details")
    pertranstype = vars(data.totalPerTransactionType)
    for det in pertranstype:
        print_key_value(str(det), "£" + str('{0:.2f}'.format(pertranstype[det])))

    printer.feed(2)
    print_medium_title("Register Actions")
    print_key_value("Transaction Voids", str(data.transVoidTotal))
    print_key_value("Item Voids", str(data.itemVoidTotal))

    printer.feed(1)
    printer.justify("C")
    printer.println("** STORE COPY **")
    printer.feed(2)

    return '', 200


def print_basics(printtype):
    printer.setDefault()

    printer.setSize("L")
    printer.justify("C")
    printer.boldOn()
    printer.underlineOn()
    printer.println("Bubbletill")

    printer.feed(2)
    printer.setSize("M")
    printer.underlineOff()
    printer.println(printtype)

    printer.feed(1)
    printer.setDefault()


def print_medium_title(title):
    printer.setDefault()
    printer.setSize("M")
    printer.justify("C")
    printer.boldOn()
    printer.println(title)
    printer.println("--------------------")

    printer.feed(1)
    printer.setDefault()


def print_key_value(key, value):
    printer.setDefault()
    printer.println(key + " - " + value)
    # printer.feed(0)
    # printer.print(key)
    # printer.feed(0)
    # printer.print(value)
    # printer.justify("R")
    # printer.feed(0)


# Launch apps
@app.route('/launch/backoffice')
def launch_backoffice():
    with open('data.json', 'r') as datafile:
        data = json.loads(datafile.read())
        subprocess.Popen(["java", "-jar", data["backoffice"]])
        return '', 200


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5001)
