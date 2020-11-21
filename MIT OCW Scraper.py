import requests
import os,requests
import csv
import json
import os
from time import sleep
from bs4 import BeautifulSoup
import urllib


def add_data(topic, subTopic, speciality, courseName, courseId, link, resourceType, name, path):
	data = [topic, subTopic, speciality, courseName, courseId, link, resourceType, name, path]
	with open("scraper.csv", "a") as fp:
	    wr = csv.writer(fp, dialect='excel')
	    wr.writerow(data)

topics = []

mainURL = "https://ocw.mit.edu/courses/find-by-topic/topics.json"
print ("Listing the Topics .......")#escuchando los topicos
loop1 = True
while loop1:
	try:
		r = requests.get(mainURL)
		loop1 = False
	except IOError as e:
		print ("Socket error. Sleeping for 2 seconds")
		sleep(2)
		continue
	except requests.exceptions.ConnectionError as e:
		print ("Proxy Error. Sleeping for 2 seconds")
		sleep(2)
		continue

jsonTexts =  json.loads(r.content.decode())
for jsonText in jsonTexts:
	topics.append([jsonText["name"],jsonText['file']])
print ("\nFollowing Topics are available to Scrape : \n")
#listar topicos del 1 al....
topicsCount = len(topics)
for i in range(0,topicsCount):
	print (str(i+1) + ") " + topics[i][0] + "")
#ingresa el numero de topico 
topicNumber = 0
while topicNumber == 0:
	topicNumber = int(input("\nPlease give the topic number which you want to scrape? \n"))
	if topicNumber > topicsCount:
		topicNumber = 0
#con el numero ingresado queda en la variable topicNumber
selectedTopicNumber = topicNumber - 1
selectedTopicName = topics[selectedTopicNumber][0]#
selecteTopicUrl = "https://ocw.mit.edu/courses/find-by-topic/" + topics[selectedTopicNumber][1]

print ("Scraping the topic " + selectedTopicName + ". (Based on the number of subjects in topic, scraping might take some time.) \n")
#ingresa la cantidad de cursos que descargas del topico elegido
loop2 = True
while loop2:
	try:
		r = requests.get(selecteTopicUrl)
		loop2 = False
	except IOError as e:
		print ("Socket error. Sleeping for 2 seconds")
		sleep(2)
		continue
	except requests.exceptions.ConnectionError as e:
		print ("Proxy Error. Sleeping for 2 seconds")
		sleep(2)
		continue
json_texts =  json.loads(r.content.decode())

subjectsCount = len(json_texts)
print ("Total subjects in topic " + selectedTopicName + " are " + str(subjectsCount) + ". \n")

subjectsToScrape = 0
while subjectsToScrape == 0 :
	subjectsToScrape = int(input("How many Subjects do you want to scrape? \n"))
	if subjectsToScrape > subjectsCount:
		subjectsToScrape = 0

print ("Starting to scrape " + str(subjectsToScrape) + " subjects.")
#inicia el scraping!
for i in range(0,subjectsToScrape):
	courseName = json_texts[i]['title']
	courseLink = json_texts[i]['href']
	courseId = json_texts[i]['id']
	print (str(i+1) + ") Scraping " + courseName + ".")

	if(json_texts[i]["textbooks"] == False):
		if courseLink.startswith("courses"):
			finalUrl = "https://ocw.mit.edu/" + courseLink + "/download-course-materials/"
		elif courseLink.startswith("resources"):
			finalUrl = "https://ocw.mit.edu/" + courseLink + "/download-resource-materials/"
		else:
			continue

		loop3 = True
		while loop3:
			try:
				r = requests.get(finalUrl)
				loop3 = False
			except IOError as e:
				print ("Socket error. Sleeping for 2 seconds")
				sleep(2)
				continue
			except requests.exceptions.ConnectionError as e:
				print ("Proxy Error. Sleeping for 2 seconds")
				sleep(2)
				continue

		soup1 = BeautifulSoup(r.text)

		if len(soup1.select("a.downloadNowButton")) >= 1:
			print ("Downloading the Study Material for this subject. ")
			downloadUrl = soup1.select("a.downloadNowButton")[0]['href']
			downloadUrl = "https://ocw.mit.edu" + downloadUrl
			fullfilename = os.path.join('courses/'+ selectedTopicName +'/', courseId + ".zip")
			loop4 = True
			while loop4:
				try:
					#Because of some problems with proxy, I was unable to use urllib.
					#wget.download(downloadUrl,fullfilename)
					get_response = requests.get(downloadUrl,stream=True)
					file_name  = downloadUrl.split("/")[-1]
					with open(file_name, "wb") as zipFile:
						for chunk in get_response.iter_content(chunk_size=1024):
							if chunk: # filter out keep-alive new chunks
								zipFile.write(chunk)
					loop4 = False
				except IOError as e:
					print (e)
					print ("Socket error. Sleeping for 2 seconds")
					sleep(2)
					continue
				except requests.exceptions.ConnectionError as e:
					print ("Proxy Error. Stopping the script for 2 seconds")
					sleep(2)
					continue
			print ("Download Finished, Adding details to csv. \n")
			for topics in json_texts[i]['topics']:
				subTopic = topics['subCat']
				speciality = topics['speciality']
				add_data(selectedTopicName,subTopic,speciality,courseName,courseId,courseLink,"Study Material",' ',fullfilename)

		else:
			for details in json_texts[i]['topics']:
				subTopic = details['subCat']
				speciality = details['speciality']
				add_data(selectedTopicName,subTopic,speciality,courseName,courseId,courseLink," ",' ',' ')
			print ("No course material available for this Subject. Adding Subject details to csv. \n")

	else:
		for details in json_texts[i]['topics']:
			subTopic = details['subCat']
			speciality = details['speciality']
			add_data(selectedTopicName,subTopic,speciality,courseName,courseId,courseLink," ",' ',' ')
		print ("No course material available for this Subject. Adding subject details to csv. \n")

print ("Scraping all " + str(subjectsToScrape) + " Subjects Done (y) .\n")
print ("Thank You for using this script. For any issues please mail to sunil@suniltatipelly.in :) \n")
