# import the necessary packages
from threading import Thread
from PIL import Image
from pymongo import MongoClient
from bson.json_util import dumps
from flask import Flask, render_template, request, jsonify
import time
import json
import sys
import io
import os, errno
import requests
import mimetypes
from io import BytesIO
from scraping import Scraping_Image
import mongodb_helper
from mongodb_helper import Mongodb_helper
from flask.templating import render_template
import directory_utils
import settings

app = Flask(__name__)

mongoclient = None
mongo = None


@app.route("/predict", methods=["POST"])
def predict():
	# /predicturl?url=http://xxx.com/abcnews
	data = {"website_folder": ""}
	result_data = {}
	result_data[settings.Website_Folder_Column] = ''
	try:		
		data = json.loads(request.data.decode())
		print('data: ' + request.data.decode())
		website = data["website"]
		includeGambling = data['includeGambling'] == "yes" if "includeGambling" in data.keys() else False
		includeAlcohol = data['includeAlcohol'] == "yes" if "includeAlcohol" in data.keys() else False
		includeNudity = data['includeNudity'] == "yes" if "includeNudity" in data.keys() else False
		runImage = data['runImage'] == "yes" if "runImage" in data.keys() else False
		runText = data['runText'] == "yes" if "runText" in data.keys() else False
		dict_map = {settings.Category_Gambling: includeGambling, settings.Category_Alcohol : includeAlcohol, settings.Category_Nudity : includeNudity}
		if runImage:
			query_dict = {}
			query_dict['website'] = website.strip()
			for k,v in dict_map.items():
				if not v:
					if k in settings.Categories_In_Program:
						settings.Categories_In_Program.remove(k)
				else:
					if k not in settings.Categories_In_Program:
						settings.Categories_In_Program.append(k)
					query_dict["result." + k] = {"$exists" : True}
			print(str(includeGambling))
			results = mongo.Query(query_dict)
			if results.count() > 0:
				s = dumps(results)
				print("result dumps: " + s)
				st = json.loads(s)
				print("len" + str(len(st)))
				if st is not None and len(st) > 0:
					x = st[0]
					result_data = {settings.Website_Folder_Column : x[settings.Website_Folder_Column], settings.Website_Column : x[settings.Website_Column], settings.Result_Column : x[settings.Result_Column], settings.Image_Name_Column : x[settings.Image_Name_Column]}
					print("jsonify_result : "+dumps(result_data))
					return jsonify(result_data)
			else:
				folderName = directory_utils.CreateFolderName(website)
				print('scraping images at: ', website)
				print('folder name: ' + folderName)
				scraping = Scraping_Image(website, folderName)
				if scraping.run():
					result_data[settings.Website_Folder_Column] = folderName
	except Exception as e:
		print("error: " + e.__str__())
		pass
	finally:
		print('finally')
		return jsonify(result_data);

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template('index.html')

def process(website):
	folderName = directory_utils.CreateFolderName(website)
	if mongo.Query({"website" : website.strip()}).count() > 0:
		data = {"success": True}
	else:
		scraping = Scraping_Image(website, folderName)
		if scraping.run():
			data = {"success": True}
			print('finishing')
		
def jsonify_result(results, one_record = False):
	s = dumps(results)
	print("jsonify_result s : " + s)
	st = json.loads(s)
	print("len" + str(len(st)))
	d = []
	if st is not None:
		for x in st:
		    o = {settings.Website_Folder_Column : x[settings.Website_Folder_Column], settings.Website_Column : x[settings.Website_Column], settings.Result_Column : x[settings.Result_Column], settings.Image_Name_Column : x[settings.Image_Name_Column]}
		    print("jsonify_result : "+dumps(o))
		    d.append(o)
	return jsonify(d if not one_record else d[0])

@app.route("/result", methods=["POST"])
def get_results():
	data = json.loads(request.data.decode())
	website = data["web"]
	includeGambling = data['includeGambling'] == "yes" if "includeGambling" in data.keys() else False
	includeAlcohol = data['includeAlcohol'] == "yes" if "includeAlcohol" in data.keys() else False
	includeNudity = data['includeNudity'] == "yes" if "includeNudity" in data.keys() else False
	dict_map = {settings.Category_Gambling: includeGambling, settings.Category_Alcohol : includeAlcohol, settings.Category_Nudity : includeNudity}
	query_dict = {}
	query_dict['website'] = website.strip()
	query_dict[settings.Suspicious_Column] = True
	for k,v in dict_map.items():
		if v:
			if k in settings.Categories_In_Program:
				query_dict["result." + k] = {"$exists" : True}
		else:
			query_dict["result." + k] = {"$exists" : False}
# 	folderName = directory_utils.CreateFolderName(website)	
	results = mongo.Query(query_dict, settings.Result_Column, 10)	
	
	return jsonify_result(results)

@app.route("/finalresults", methods = ["POST"])
def get_final_results():
	data = json.loads(request.data.decode())
	print("json: "+json.dumps(data))
	website_folder = None
	finalResults = {}
	font_color = settings.Unknown_Color
	
	runImage = data['runImage'] == "yes" if "runImage" in data.keys() else False
	runText = data['runText'] == "yes" if "runText" in data.keys() else False
	if runImage:
		finalResults[settings.Advice] = settings.Unknown_Value
		finalResults[settings.Font_Color] = font_color
		finalResults[settings.Probabilities] = settings.default_result()
		if settings.Website_Folder_Column in data:
			website_folder = data[settings.Website_Folder_Column]
		if website_folder is not None:
			group_dict = {}
			group_dict['_id'] = "$" + settings.Website_Folder_Column
			for category in settings.Categories_In_Program:
				group_dict[category] = {"$max" : "${0}.{1}".format(settings.Result_Column, category)}
			pipe_line = [{"$match": {settings.Website_Folder_Column : website_folder}}, {"$group": group_dict}]
			result = mongo.Query_Aggregate(pipe_line)
			if result is not None:
				s = dumps(result)
				st = json.loads(s)
				print("result : " + s)
				if len(st)>0:
					json_object = st[0]
					max_value = -1
					probabilities = {}
					for key, value in json_object.items():
						if isinstance(value, float) or isinstance(value, int):
							probabilities[key] = value
							if value > max_value:
								max_value = value;
					print(str(max_value))
					if max_value >= settings.advice_threshold_unsafe:
						advice = settings.Unsafe_Value
						font_color = settings.Unsafe_Color
					else:
						advice = settings.Safe_Value
						font_color = settings.Safe_Color
					
					finalResults[settings.Advice] = advice
					finalResults[settings.Font_Color] = font_color
					finalResults[settings.Probabilities] = probabilities
	return jsonify(finalResults)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	# load the function used to classify input images in a *separate*
	# thread than the one used for main classification
	mongo = Mongodb_helper()
	mongo.Drop_DataBase(settings.MONGODB_NAME)
	# start the web server
	print("* Starting web service...")
	app.run(host='0.0.0.0')