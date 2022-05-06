from flask import Flask
from time import sleep
from gpiozero import JamHat
import json

app = Flask(__name__)
jh = JamHat()


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


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5001)
