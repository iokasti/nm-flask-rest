#!flask/bin/python
from flask import Flask, jsonify, request, make_response, abort
from pymongo import MongoClient
from bson.json_util import dumps

max_distance = 0.29

db_host = 'localhost'
db_name = 'open_cell_id'
db_port = 27017
transactions_collection = 'cell_towers'

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

# returns all information for a specified cell using mcc, area, cell, net
@app.route('/getcellinfo', methods=['GET'])
def getCellInfo():
	args = request.args.to_dict()

	if ('mcc' not in args) or ('lac' not in args) or ('cellid' not in args) or ('mnc' not in args):
		abort(400)

	mongoClient = MongoClient(db_host, db_port)
	database = mongoClient[db_name]
	collection = database[transactions_collection]

	cell = collection.find_one(	{'mcc':int(args['mcc']), 'area':int(args['lac']), 'cell':int(args['cellid']), 'net':int(args['mnc'])},\
								{'_id': False})
	if cell == None:
		abort(404)

	return dumps(cell), 200

# returns all information regarding mobile's coordinates from cells in certain distance
@app.route('/getcellinfoinarea', methods=['GET'])
def getCellInfoInArea():
	args = request.args.to_dict()
	
	if ('phoneLat' not in args) or ('phoneLong' not in args):
		abort(400)

	mongoClient = MongoClient(db_host, db_port)
	database = mongoClient[db_name]
	collection = database[transactions_collection]

	cells = collection.find({'coords':{'$near':[float(args['phoneLat']), float(args['phoneLong'])], '$maxDistance':max_distance}},\
							{'_id':False, 'coords.type':False})

	if cells == None:
		abort(404)

	return dumps(cells), 200

# just a test url, to check service functionality.
@app.route('/test', methods=['GET'])
def test():
	return make_response(jsonify({'Test': 'Connection successful'}), 200)

if __name__ == '__main__':
	app.run(host='0.0.0.0')