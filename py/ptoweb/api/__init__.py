from ptoweb import cache, app, get_db
from flask import Response, g, request
from bson import json_util
import json
from ptoweb.api.auth import require_auth
import re
from datetime import datetime
import iql.convert as iqlc
import pprint



def cors(resp):
  resp.headers['Access-Control-Allow-Origin'] = '*'
  return resp

def json200(obj):
  return cors(Response(json.dumps(obj, default=json_util.default), status=200, mimetype='application/json'))

def json400(obj):
  return cors(Response(json.dumps(obj, default=json_util.default), status=400, mimetype='application/json'))

def json404(obj):
  return cors(Response(json.dumps(obj, default=json_util.default), status=404, mimetype='application/json'))

def text200(obj):
  return cors(Response(obj, status=200, mimetype='text/plain'))


@app.route('/')
def api_index():
  """
  Dummy method answering with `{"status":"running"}` when the API is available.
  """

  for e in get_db().query("SELECT 1+1;").dictresult():
    print(e)

  return json200({'status':'running'})


@app.route('/query')
def api_query():

  iql = request.args.get('q')

  if iql == None or iql == '':
    return json400({"error" : "Empty query!"})

  try:
    iql = json.loads(iql)
  except:
    return json400({"error" : "Not valid JSON!"})

  try:
    sql = iqlc.convert(iql)
  except ValueError as error:
    return json400({"error" : str(error)})

  dr = get_db().query(sql).dictresult()
  result_json = []

  i = 0

  for e in dr:

    for key in e:
      if key.lower() in ['time_to' ,'time_from']:
        e[key] = e[key].timestamp()

    
    if ('val_i' in e) and ('val_s' in e):
      if e['val_i'] != None:
        e['value'] = e['val_i']
      elif e['val_s'] != None:
        e['value'] = e['val_s']
      else:
        e['value'] = None

      del e['val_i']
      del e['val_s']
    elif 'val_i' in e:
      e['value'] = e['val_i']
      del e['val_i']
    elif 'val_s' in e:
      e['value'] = e['val_s']
      del e['val_s']

    result_json.append(e)

    i += 1
    if(i > 128): break

  return json200({"results" : result_json})



@app.route('/translate')
def api_translate():

  iql = request.args.get('q')

  if iql == None or iql == '':
    return json400({"error" : "Empty query!"})

  try:
    iql = json.loads(iql)
  except:
    return json400({"error" : "Not valid JSON!"})

  try:
    sql = iqlc.convert(iql)
  except ValueError as error:
    return json400({"error" : str(error)})

  pp = pprint.PrettyPrinter(indent = 2)
  piql = pp.pformat(iql)

  lines = piql.splitlines()
  piql = '\n'.join(map(lambda a: '-- ' + a, lines))

  dr = get_db().query(sql).dictresult()
  result_json = ""

  i = 0

  for e in dr:

    for key in e:
      if key.lower() in ['time_to' ,'time_from']:
        e[key] = e[key].timestamp()

    
    if ('val_i' in e) and ('val_s' in e):
      if e['val_i'] != None:
        e['value'] = e['val_i']
      elif e['val_s'] != None:
        e['value'] = e['val_s']
      else:
        e['value'] = None

      del e['val_i']
      del e['val_s']
    elif 'val_i' in e:
      e['value'] = e['val_i']
      del e['val_i']
    elif 'val_s' in e:
      e['value'] = e['val_s']
      del e['val_s']

    result_json += json.dumps(e) + "\n"

    i += 1
    if(i > 128): break

 
  return text200(piql + "\n\n" + sql + "\n\n" + result_json)


def to_int(value):
  try:
    return int(value, 10)
  except:
    return 0


