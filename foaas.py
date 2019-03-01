#!/usr/bin/env python

from flask import Flask, request, jsonify
import requests
import json
import random

app = Flask(__name__)


debug = False
verbose = False


def set_debug_mode():
    global debug
    global verbose
    if request.values.get('debug'):
        debug = True
        app.config['DEBUG'] = True
    if request.values.get('verbose'):
        verbose = True


def debugger(var):
    global debug
    if debug:
        app.logger.debug(var)

def print_request():
    global verbose
    if verbose:
        debugger(request.values)

@app.route('/fuckoff_slashcommand', methods=['GET', 'POST'])
def slashcommand():
    fo = gen_fuckoff()
    return jsonify({
        "response_type": "in_channel",
        "attachments": [{
            'title': fo['subtitle'],
            'fallback': fo['message'],
            'text': fo['message'],
            'parse': 'none',
            'mrkdwn': False
        }]
    })


@app.route('/fuckoff', methods=['GET', 'POST'])
def webhook():
    fo = gen_fuckoff()
    res_text = fo['message'] + "\n_" + fo['subtitle'] + '_'
    resp = {
        'text': res_text
    }

    return json.dumps(resp)


def gen_fuckoff():
    set_debug_mode()
    print_request()

    # trigger warning: trigger word
    trigger_word = request.values.get('trigger_word')

    # from/dest params
    name_from = request.values.get('user_name')
    text = request.values.get('text')

    # strip trigger word
    name = text
    if trigger_word and text:
        name = text.replace(trigger_word, "", 1)

    # grab available fuckoff operations
    ops_r = requests.get('https://foaas.com/operations')
    ops = json.loads(ops_r.text)

    # strip out operations that require extra fields
    basic_ops = []
    for op in ops:
        fields = op['fields']
        field_names = [field['field'] for field in fields]

        # only allow ones with from/to
        if not name and set(field_names) == set(['from']) or set(field_names) == set(['name', 'from']):
            basic_ops.append(op)

    debugger(basic_ops)

    # pick random op
    op = random.choice(basic_ops)

    url = op['url']

    if name_from:
        url = url.replace(':from', name_from)

    if name:
        url = url.replace(':name', name)

    # get fuckoff
    fo_r = requests.get('https://foaas.com%s' % url, headers={ 'Accept': 'application/json' })
    fo = json.loads(fo_r.text)
    return fo

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
