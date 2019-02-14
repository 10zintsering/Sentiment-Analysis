from newsapi import NewsApiClient
import csv
import json
import pprint
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions, KeywordsOptions

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2018-12-11',
    iam_apikey='2wmf5sIFDCin1NV5OZexjXtdr7BR2b_OVHA7oAn2Nfaa',
    url='https://gateway-fra.watsonplatform.net/natural-language-understanding/api'
    )

# Init
newsapi = NewsApiClient(api_key='aae92b89467f452aa62d0ffa26d51bf8')

                            

# /v2/everything
all_articles = newsapi.get_everything(q='samsung',
                                    from_param='2019-01-01',
                                    to='2019-01-17',
                                    language='en',
                                    sort_by='popularity',
                                    page_size=100
                                    )

#print(all_articles)
#filter unwanted metadata
def process_news(news):
    d = {}
    d['date'] = news['publishedAt']
    d['author'] = news['author']
    d['title'] = news['title']
    d['source'] = news['source']['name']

    return d

#save it as a csv file 
def save_to_csv(news):

    with open (r'SamsungNewsEverythingAnalyzed.csv', 'a') as file :
        writer = csv.writer(file)
        writer.writerow(list(news.values()))

def analyze_sentiment(news):
        if news['title'] :
            analysis = natural_language_understanding.analyze(
                text = news['title'],
                features= Features(sentiment= SentimentOptions())).get_result()

            analyzed = json.dumps(analysis['sentiment']['document']['score'])
            return analyzed
        else:
            return ' '
def analyze_keywords(news):
        if news['content']:
            analysis = natural_language_understanding.analyze(
            text= news['content'],
            features= Features(keywords=KeywordsOptions(sentiment=True,emotion=False,limit=3))).get_result()
            return analysis

        else:
            d= {'keywords':[]}
            return d





for i in all_articles['articles']:
    news = process_news(i)
    news['sentiment_title'] = analyze_sentiment(i)
    dictionary=analyze_keywords(i)
    index = 0
    while index < len(dictionary['keywords']):
        if index == 0:
            news['keywordOne'] = dictionary['keywords'][index]['text']
            news['kewordsentimentOne']= dictionary['keywords'][index]['sentiment']['score']
        if index == 1:
            news['keywordTwo'] = dictionary['keywords'][index]['text']
            news['kewordsentimentTwo']= dictionary['keywords'][index]['sentiment']['score']
        if index == 2:
            news['keywordThree'] = dictionary['keywords'][index]['text']
            news['kewordsentimentThree']= dictionary['keywords'][index]['sentiment']['score']
        index += 1
    save_to_csv(news)


# Create an empty string
text_combined = ' '

#Loop through all the headlines and add them to 'text_combined' 
for i in all_articles['articles']:
    text_combined += i['title'] + ' ' # add a space after every headline, so the first and last words are not glued together

# Print the first 300 characters to screen for inspection
#print(text_combined[0:300])

wordcloud = WordCloud(max_font_size=40).generate(text_combined)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()