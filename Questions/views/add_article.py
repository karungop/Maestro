from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import Template
import re
from bs4 import BeautifulSoup
import requests

from TeacherWorm.models.articles import Article
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import Template
import re
from bs4 import BeautifulSoup
import requests
from TeacherWorm.models.articles import Article

import openai
from openai import OpenAI

from dotenv import load_dotenv
import os

import json

from TeacherWorm.models.questions import Question

# Load .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_API_KEY)

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
}


def load_to_models(article, difficulty, new_text="", listMCQ=[], listFRQ=[], listTF=[]):
    article = article[0]
    # Create the Article instance
    article_instance = Article(
        title=article['headline'],
        author=article['author'],
        date_published=article['posted'],
        source=article['source'],
        original_text=article['description'].replace('\n', '\n\n'),
        difficulty_level=difficulty,
        new_text=new_text,
        # Assuming these fields are not provided in the dictionary and will be populated laters
    )

    # Save the instance to the database
    article_instance.save()
    load_questions_to_models(article_instance, listMCQ, listFRQ, listTF)



def add_article(request):
    context = {'article_generated': False}  # Initialize the flag as False
    if request.method == 'POST':
        article_url = request.POST.get('article_url', None)
        num_MCQ = 7
        num_FRQ = 2
        num_TF = 4
        difficulty = request.POST.get('difficulty', None)
        print(article_url)
        print(num_MCQ)
        print(num_FRQ)
        print(num_TF)
        print(difficulty)
        print(type(difficulty))
        difficulty = difficulty.upper()
        difficulty_num_map = {"EASY": 1, "MEDIUM" : 2, "HARD" : 3, "ORIGINAL" : 4}
        difficulty_num = difficulty_num_map[difficulty]
        if article_url:
            print("Successfully posted:", article_url)
            dict = get_the_news(article_url)
            #Call a function to get scraped data from URL
            #Call another function to load scraped data into database model
            if difficulty != "ORIGINAL":
                newText = remake(dict[0], difficulty_num)
                questMCQ = []
                questMCQ = questionM(newText, num_MCQ)
                questFRQ = questionF(newText,num_FRQ)
                questTF = questionTF(newText,num_TF)
            else:
                newText = ""

            #print(type(questMCQ))
            try:
                listMCQ = json.loads(questMCQ)
            except:
                listMCQ = []
                print("failure")
            try:
                listFRQ = json.loads(questFRQ)
            except:
                listFRQ = []
                print("failure")
            try:
                listTF = json.loads(questTF)
            except:
                listTF = []
                print("failure")
            #print(listMCQ[0])
            #print(listFRQ[0])
            #print(listTF[0])
            
            #print(quest)
            #print(newText)

            load_to_models(dict, difficulty, newText, listMCQ, listFRQ, listTF)
            context['article_generated'] = True  # Set the flag as True if article processing is successful


    return render(request, 'TeacherWorm/teacher_view.html', context)



def get_article(card,url):
    """Extract article information from the raw html"""
    try:
        headline = card.find('h1').text
    except AttributeError:
        headline = ""
    try:
        #source = card.find("span class = \"caas-author").text
        source = "Yahoo"
    except AttributeError:
        source = ""
    try:
        posted = card.find('time').text.replace('·', '').strip()
    except AttributeError:
        posted = ""
    description = ""
    p_tags = card.find_all('p')
    for p_tag in p_tags:
        description += p_tag.text.strip() + '\n'

    try:
        author = card.find('span', 'caas-author-byline-collapse').text

    except AttributeError:
        author = ""

    article = {
        'headline': headline,
        'author' : author,
        'posted': posted,
        'source': source,
        'description': description.strip(),
        'link':url
    }
    return article

def load_questions_to_models(id, listMCQ=[], listFRQ=[], listTF=[]):
    count = 0
    for questions in listMCQ:
        question_instance = Question(
            question = questions["question"],
            question_type = "MCQ",
            mcq_incorrect_choice_1 = questions["wrong_answers"][0],
            mcq_incorrect_choice_2 = questions["wrong_answers"][1],
            mcq_incorrect_choice_3 = questions["wrong_answers"][2],
            mcq_correct_choice = questions["correct_answer"],
            article_id = id
        )
        question_instance.save()
        count+=1
    for questions in listTF:
        questions_instance = Question(
            question = questions["question"],
            question_type = "TF",
            mcq_correct_choice = questions["correct_answer"],
            mcq_incorrect_choice_1 = questions["wrong_answer"],
            article_id = id
        )
        question_instance.save()
        count+=1
    for questions in listFRQ:
        question_instance = Question(
            question = questions["question"],
            question_type = "FRQ",
            article_id = id
        )
        question_instance.save()
        count+=1
    print(count)

def get_the_news(url):
    """Scrape a specific article from the provided URL"""
    articles = []
    '''


    i = 1
    while i < 2:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', 'NewsArticle')
            i += 1
            # extract articles from page
            for card in cards:
                article = get_article(card)
                link = article['link']
                if not link in links:
                    links.add(link)
                    articles.append(article)
        else:
            print(f"Error: Unable to fetch the URL. Status Code: {response.status_code}")
            break
    '''
    response = requests.get(url, headers=headers)
    if(response.status_code == 200):
      #print(response.text)
      soup = BeautifulSoup(response.text, 'html.parser')
      #cards = soup.find_all('div')
      #print(cards)
      article = get_article(soup,url)
      articles.append(article)

      #for card in cards:
      #      article = get_article(card)
      #      articles.append(article)

    else:
      print(f"Error: Unable to fetch the URL. Status Code: {response.status_code}")

    return articles


def questionM(prompt, numQ):
    print("handling regular")
    jsonEX = "[{\"question\":\"WhenistheexpectedreleasetimeframefortheiPhone16?\",\"correct_answer\":\"September2024\",\"wrong_answers\":[\"June2023\",\"January2025\",\"August2024\"]},{\"question\":\"WhatisoneexpectedchangeinthedesignoftheiPhone16basemodel?\",\"correct_answer\":\"Verticaldualcameralayout\",\"wrong_answers\":[\"Triplecamerasetup\",\"Horizontalcameralayout\",\"Nocameraimprovements\"]},{\"question\":\"WhatenhancementsareexpectedintheiPhone16Promodels?\",\"correct_answer\":\"Largerdisplaysandcameraimprovements\",\"wrong_answers\":[\"Smallerdisplaysandreducedcameraquality\",\"Nodesignchanges\",\"Slowerchargingspeedsandlowerbatterycapacity\"]},{\"question\":\"WhatnewtechnologyisrumoredtobeincludedintheiPhone16lineup?\",\"correct_answer\":\"Hapticbuttonsandadvancedcamerafeatures\",\"wrong_answers\":[\"Physicalbuttonsandbasiccamerafunctions\",\"Nonewtechnologyupgrades\",\"BiometricsensorsandAIintegration\"]},{\"question\":\"WhatisApple'sfocuswitheachnewiPhonerelease?\",\"correct_answer\":\"Innovationandtechnologyadvancements\",\"wrong_answers\":[\"Cuttingcostsandreducingfeatures\",\"Scalingdownproduction\",\"Delayingreleases\"]}]"

    directions = f"Create a JSON list like {jsonEX} without printing \"'''json\" else with {numQ} dictionaries in it like [(),(),(),(),()] that is in json.loads() format to hold multiple questions for the following prompt {prompt}. Each dictionary will have five strings. The first string in each dictionary will be the multiple choice question. The second dictionary will the correct answer to the multiple choice question. The next three strings will be the remaining wrong answers to the multiple choice question. "
    #print(directions)
    messages = [{"role": "system", "content": "You are to making multiple choice test questions based on an article."}]
    messages.append({"role": "user",
                     "content": directions})

    answers = client.chat.completions.create(model="gpt-3.5-turbo",
                                             messages=messages, )
    print("recieved from gpt")

    output = answers.choices[0].message.content
    print(output)
    return output



def questionF(prompt, numQ):
    print("handling regular")
    jsonEX = "[{\"question\":\"WhenistheexpectedreleasetimeframefortheiPhone16?\",\"correct_answer\":\"September2024\",\"wrong_answers\":[\"June2023\",\"January2025\",\"August2024\"]},{\"question\":\"WhatisoneexpectedchangeinthedesignoftheiPhone16basemodel?\",\"correct_answer\":\"Verticaldualcameralayout\",\"wrong_answers\":[\"Triplecamerasetup\",\"Horizontalcameralayout\",\"Nocameraimprovements\"]},{\"question\":\"WhatenhancementsareexpectedintheiPhone16Promodels?\",\"correct_answer\":\"Largerdisplaysandcameraimprovements\",\"wrong_answers\":[\"Smallerdisplaysandreducedcameraquality\",\"Nodesignchanges\",\"Slowerchargingspeedsandlowerbatterycapacity\"]},{\"question\":\"WhatnewtechnologyisrumoredtobeincludedintheiPhone16lineup?\",\"correct_answer\":\"Hapticbuttonsandadvancedcamerafeatures\",\"wrong_answers\":[\"Physicalbuttonsandbasiccamerafunctions\",\"Nonewtechnologyupgrades\",\"BiometricsensorsandAIintegration\"]},{\"question\":\"WhatisApple'sfocuswitheachnewiPhonerelease?\",\"correct_answer\":\"Innovationandtechnologyadvancements\",\"wrong_answers\":[\"Cuttingcostsandreducingfeatures\",\"Scalingdownproduction\",\"Delayingreleases\"]}]"

    directions = f"Create a JSON list like {jsonEX} with {numQ} frq’s based on the following text: {prompt}"

    #print(directions)
    messages = [{"role": "system", "content": "You are to create frq test questions based on an article."}]
    messages.append({"role": "user",
                     "content": directions})

    answers = client.chat.completions.create(model="gpt-3.5-turbo",
                                             messages=messages, )
    print("recieved from gpt")

    output = answers.choices[0].message.content

    return output

def questionTF(prompt, numQ):
    print("handling regular")
    jsonEX = "[{\"question\":\"WhenistheexpectedreleasetimeframefortheiPhone16?\",\"correct_answer\":\"September2024\",\"wrong_answers\":[\"June2023\",\"January2025\",\"August2024\"]},{\"question\":\"WhatisoneexpectedchangeinthedesignoftheiPhone16basemodel?\",\"correct_answer\":\"Verticaldualcameralayout\",\"wrong_answers\":[\"Triplecamerasetup\",\"Horizontalcameralayout\",\"Nocameraimprovements\"]},{\"question\":\"WhatenhancementsareexpectedintheiPhone16Promodels?\",\"correct_answer\":\"Largerdisplaysandcameraimprovements\",\"wrong_answers\":[\"Smallerdisplaysandreducedcameraquality\",\"Nodesignchanges\",\"Slowerchargingspeedsandlowerbatterycapacity\"]},{\"question\":\"WhatnewtechnologyisrumoredtobeincludedintheiPhone16lineup?\",\"correct_answer\":\"Hapticbuttonsandadvancedcamerafeatures\",\"wrong_answers\":[\"Physicalbuttonsandbasiccamerafunctions\",\"Nonewtechnologyupgrades\",\"BiometricsensorsandAIintegration\"]},{\"question\":\"WhatisApple'sfocuswitheachnewiPhonerelease?\",\"correct_answer\":\"Innovationandtechnologyadvancements\",\"wrong_answers\":[\"Cuttingcostsandreducingfeatures\",\"Scalingdownproduction\",\"Delayingreleases\"]}]"

    #print(prompt)
    directions = f"Create a JSON list like {jsonEX} with {numQ} dictionaries in it like [(),(),(),(),()] to hold multiple true or false questions for the following prompt {prompt}. Each dictionary will have three strings. The first string in each dictionary will be the true or false question. The second dictionary will the correct answer. The thrid string will be the wrong answer."
    #print(directions)
    messages = [{"role": "system", "content": "You are to true or false test questions based on an article."}]
    messages.append({"role": "user",
                     "content": directions})

    answers = client.chat.completions.create(model="gpt-3.5-turbo",
                                             messages=messages, )
    print("recieved from gpt")

    output = answers.choices[0].message.content

    return output


def remake(orgArticle, difficulty):
    print("handling regular")
    mid = orgArticle["description"]
    # print(type(mid))
    
    if (difficulty == 1):
        messages = [{"role": "system", "content": "You are to rewrite an article to adjust the reading level."}]
        messages.append({"role": "user",
                         "content": f"Rewrite the following article for a reading level between kindergarten and 4th grade.: {mid}"})
        answers = client.chat.completions.create(model="gpt-3.5-turbo",
                                                 messages=messages, )
    elif (difficulty == 2):
        messages = [{"role": "system", "content": "You are to rewrite an article to adjust the reading level."}]
        messages.append({"role": "user",
                         "content": f"Rewrite the following article for a reading level between 5th grade and 7th grade.: {mid}"})
        answers = client.chat.completions.create(model="gpt-3.5-turbo",
                                                 messages=messages, )
    else:
        messages = [{"role": "system", "content": "You are to rewrite an article to adjust the reading level."}]
        messages.append({"role": "user",
                         "content": f"Rewrite the following article for a reading level between 8th grade and 12th grade.: {mid}"})
        answers = client.chat.completions.create(model="gpt-3.5-turbo",
                                                 messages=messages, )

        answers = client.chat.completions.create(model="gpt-3.5-turbo",
                                                 messages=messages, )
    print("recieved from gpt")

    output = answers.choices[0].message.content

    return output