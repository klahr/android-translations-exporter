#!/usr/bin/env python3

import argparse
import os
from xml.dom import minidom

def isTranslated(translations, key):
	for translation in translations:
		elements = translation["xmldoc"].getElementsByTagName("string")
		translated = False
		for element in elements:
			if element.attributes["name"].value == key:
				if element.firstChild != None:
					translated = True
					break
		
		if translated == False:
			return False

	return True

def getTranslation(translations, key, language):
	for translation in translations:
		if translation["language"] == language:
			elements = translation["xmldoc"].getElementsByTagName("string")
			for element in elements:
				if element.attributes["name"].value == key:
					if element.firstChild is not None:
						return element.firstChild.data
					else:
						return ""

	return None

def getFilenameForLanguage(filename, language):
	return filename[0:filename.rfind('/')] + "-" + language + "/strings.xml"

def doExport(filename, languages, output):
	if output == None or output == "":
		output = "./out.csv"

	translations = []
	for language in languages:
		stringsFilename = getFilenameForLanguage(filename, language)
		if os.path.isfile(stringsFilename):
			xmldoc = minidom.parse(stringsFilename)
			elements = xmldoc.getElementsByTagName("string")
			dictionary = {}
			dictionary["language"] = language
			dictionary["filename"] = stringsFilename
			dictionary["xmldoc"] = xmldoc
			translations.append(dictionary)

	file = open(output, "w")

	xmldoc = minidom.parse(filename)
	stringElements = xmldoc.getElementsByTagName("string")
	file.write("key;default;")
	for translation in translations:
		file.write(translation["language"] + ";")

	file.write("\n")

	for key in stringElements:
		if key.hasAttribute("translatable"):
			if key.attributes["translatable"].value == "false":
				continue

		if not isTranslated(translations, key.attributes["name"].value):
			file.write(key.attributes["name"].value + ";")
			file.write(key.firstChild.data + ";")
			for translation in translations:
				t = getTranslation(translations, key.attributes["name"].value, translation["language"])
				if t is not None:
					file.write(t + ";")
				else:
					file.write(";")

			file.write("\n")

	file.close()

parser = argparse.ArgumentParser()
parser.add_argument("--filename", action="store")
parser.add_argument("--languages", action="store")
parser.add_argument("--output", action="store")
results = parser.parse_args()

if "filename" not in results or results.filename is None or "output" not in results:
	print("usage: ./export.py --filename </PATH/TO/strings.xml> --languages <COMMA_SEPARATED_LANGUAGES> --output <FILENAME>")
	print("example: ./export.py --filename ./app/src/main/res/values/strings.xml --languages=sv,no,fi --output ./out.csv")
else:
	languages = results.languages.split(',')
	doExport(results.filename, languages, results.output)
