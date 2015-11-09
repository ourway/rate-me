#!/usr/bin/env python


## by farsheed ashouri, for appido services.

try:
    import eventlet
    eventlet.monkey_patch()
except ImportError:
    print('Eventlet is not available')
    pass

import ujson as json
from bottle import Bottle, request, response, run, hook
from models import r
import re

application = Bottle()

rate_item_key = 'RATE-ME|{custId}|{raterId}|{itemId}'



@application.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, authorization'
    response.headers['Access-Control-Request-Methods'] = 'Origin, X-Requested-With, Content-Type, Accept, Post'
    response.headers['Access-Control-Request-Method'] = '*'



@application.get('/ping')
def ping():
    return json.dumps({'message':'PONG'})


@application.route('/api/rate/<custId>/<raterId>/<itemId>', method=['OPTIONS', 'POST'])
def rate_item(custId, raterId, itemId):
    """ rate something """
    payload = request.json
    if payload and 'value' in payload:  ## it's ok to rate
        key = rate_item_key.format(custId=custId, raterId=raterId, itemId=itemId)
        r.set(key, payload['value'])
        return json.dumps(dict(status=0))
    return json.dumps(dict(status=-1))



@application.route('/api/unrate/<custId>/<raterId>/<itemId>',  method=['OPTIONS', 'POST'])
def unrate_item(custId, raterId, itemId):
    """  remove rating """
    key = rate_item_key.format(custId=custId, raterId=raterId, itemId=itemId)
    r.delete(key)
    return json.dumps(dict(status=0))



@application.route('/api/did_rate/<custId>/<raterId>/<itemId>', method=['GET', 'OPTIONS'])
def did_rate(custId, raterId, itemId):
    """ a true or false """
    key = rate_item_key.format(custId=custId, raterId=raterId, itemId=itemId)
    return json.dumps(dict(result=r.exists(key)))


@application.route('/api/get_rate/<custId>/<raterId>/<itemId>', method=['GET', 'OPTIONS'])
def get_rate(custId, raterId, itemId):
    """ get rating """
    key = rate_item_key.format(custId=custId, raterId=raterId, itemId=itemId)
    return json.dumps(dict(result=r.get(key)))



@application.route('/api/get_raters/<custId>/<itemId>', method=['GET', 'OPTIONS'])
def get_raters(custId, itemId):
    """ get ratters """
    pattern = rate_item_key.format(custId=custId, raterId='*', itemId=itemId)
    raters = []
    pat = re.compile(r'RATE-ME\|[\w\d-]*\|([\w\d-]*)\|[\w\d-]*')
    for each in r.keys(pattern):
        rater = re.findall(pat, each.decode('utf-8'))
        if len(rater):
            raters.append(rater[0])
    return json.dumps(dict(redult=raters))



@application.route('/api/who_rated/<custId>/<itemId>/<rate>', method=['GET', 'OPTIONS'])
def who_rated(custId, itemId, rate):
    """ get those who rate 3 """
    pattern = rate_item_key.format(custId=custId, raterId='*', itemId=itemId)
    raters = []
    pat = re.compile(r'RATE-ME\|[\w\d-]*\|([\w\d-]*)\|[\w\d-]*')
    for each in r.keys(pattern):
        rater = re.findall(pat, each.decode('utf-8'))
        if len(rater) and r.get(each) and r.get(each).decode('utf-8')==rate:
            raters.append(rater[0])
    return json.dumps(dict(result=raters))



@application.route('/api/how_many_rated/<custId>/<itemId>/<rate>', method=['GET', 'OPTIONS'])
def how_many_rated(custId, itemId, rate):
    raters = json.loads(who_rated(custId, itemId, rate)).get('result', [])
    return json.dumps(dict(result=len(raters)))



@application.route('/api/how_many_rated_pack/<custId>/<itemId>', method=['GET', 'OPTIONS'])
def how_many_rated_pack(custId, itemId):
    pack = dict()
    for i in xrange(1,6):
        pack[i] = json.loads(how_many_rated(custId, itemId, i)).get('result', 0)

    return json.dumps(dict(result=pack))



@application.route('/api/get_average_rate/<custId>/<itemId>', method=['GET', 'OPTIONS'])
def get_average_rate(custId, itemId):
    """ get avarage rate """



if __name__ == '__main__':
    run(application, host='0.0.0.0', port=8000)
