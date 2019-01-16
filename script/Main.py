import JsonParser
import json


with open("jsons.txt","r") as f:
	result = JsonParser.parse(f.read(), "Result")
	
	print(result)
	
	with open("ResultModel.swift", "w") as w:
		w.writelines([line+'\n' for line in result])	
