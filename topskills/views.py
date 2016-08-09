from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from nltk.util import ngrams
from lxml import html
from .models import Skill
import urllib, csv, json, re, nltk, json
import pandas as pd

# Create your views here.
def index(request):
	#return HttpResponse("Hello World")
	return render(request, 'topskills/index.html')

def results(request):
	sizeQueries=request.POST['sizeQueries']
	jobtitles=[]
	companies=[]

	for i in range(1,int(sizeQueries)+1):
		jobtitles.append(request.POST['jobtitle'+str(i)])
		companies.append(request.POST['company'+str(i)])
		
	#return HttpResponse(sizeQueries)

	dataset=topEmployersJobDescriptions(companies, jobtitles)
	word_dataset=getWordsfromText(dataset)
	top20=getHardSkills(word_dataset)

	#context={'top20':top20}
	#return render(request, 'topskills/result.html', context)

	new_dict = []
	for item in top20:
		new_dict.append({"name":item[0], "value":item[1]})
	context={'result':json.dumps(new_dict), 'top20':top20}
	return render(request, 'topskills/result_d3.html', context)

def dictionary(request):
	skills = Skill.objects.all()
	context = {'dictionary':skills}
	return render(request, 'topskills/dictionary.html', context)

def dictionaryAdd(request):
	if request.POST['skill'] != "":
		item = Skill(name=request.POST['skill'])
		item.save()
	return HttpResponseRedirect('../')

def dictionaryDelete(request):
	item = Skill.objects.filter(name=request.GET['name'])
	item.delete()
	return HttpResponseRedirect('../')

def urlToText(url):
	try:
		r = urllib.urlopen(url)
		page = r.read()
		page = page.replace("\n","")
		page = page.replace("<br>"," ")
		page = page.replace("</br>"," ")
		page = page.replace("<b>"," ")
		page = page.replace("</b>"," ")
		page = page.replace("<ul>"," ")
		page = page.replace("<li>"," ")
		page = page.replace("</ul>"," ")
		page = page.replace("</li>"," ")
		page = page.replace("</li>"," ")
		page = page.replace("<p>"," ")
		page = page.replace("</p>"," ")

		tree = html.fromstring(page)
		desc = tree.xpath('//span[@class="summary"]')
		
		if len(desc) > 0:
			if desc[0].text is not None:
				return re.sub('[^a-z0-9+#]', ' ', re.sub('[-.&()\]]','',desc[0].text.encode('utf-8').lower().replace('.net','dotnet')))
			else:
				return ""
		else:
			return ""
	except Exception:
		return ""
 	
def topEmployersJobDescriptions(company, jobtitle):
	df = pd.DataFrame(columns=['company','jobtitle','url','description'])
	texts=[]
	i=0
	try:
		for j in range(len(company)):
			url="http://api.indeed.com/ads/apisearch?publisher=4428860654723226&v=2&format=json&radius=&limit=100&jt=fulltime&co=us&q=" + jobtitle[j]
			if company != "":
				url+=" company:" + company[j]
			r = json.load(urllib.urlopen(url))
			if r['results']:
				for item in r['results']:
					texts.append(urlToText(item['url']))
					df.loc[i] = [item['company'], item['jobtitle'], item['url'], urlToText(item['url'])]
					i+=1
	except Exception:
		print "Error"
	return texts

def getWordsfromText(documents):

	result = []

	for document in documents:
		words = document.split()
		# remove stopwords
		cachedStopWords = nltk.corpus.stopwords.words("english")
		filtered_words = [word for word in words if not word in cachedStopWords]

		# ngrams
		bigram = ngrams(filtered_words, 2)
		trigram = ngrams(filtered_words, 3)

		bigram_string = [' '.join(t) for t in bigram]
		trigram_string = [' '.join(t) for t in trigram]

		# combining ngrams
		filtered_words += bigram_string
		filtered_words += trigram_string

		result.append(filtered_words)

	return result

def getHardSkills(filtered_words):
	# dictionary
	items = Skill.objects.all()
	technical_dictionary = [item.name for item in items]
	
	result = []
	for document in filtered_words:
		used_word = [word for word in technical_dictionary if word in document]
		result += used_word

	# TF
	technical_tf = nltk.FreqDist(result)
	return technical_tf.most_common(20)