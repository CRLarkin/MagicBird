import json, re, datetime, csv, unicodedata, sys, base64

class decoder:

    _tweets_checked = 0
    _tweet_count = 0
    _date_data = {}

    def __init__ (self, keywords, dirOut, directory, dirTemp, emojify, emoji_file):
        self.keywords = {}
        for kw in keywords.keys():
            self.keywords.update({kw.lower() : 0})
        self.dirOut = dirOut
        self.directory = directory
        self.dirTemp = dirTemp
        self.emojis = {}
        if emojify == 1:
            with open(directory + emoji_file, 'r') as f:
                reader = csv.reader(f)
                emoji_list = list(reader)
                for emoji in emoji_list:
                    self.emojis.update({emoji[0].lower() : emoji[1]})
        

    # This is the first thing that needs to be done!
    # This esentially cleans up each tweet in the json format and seperates them into their individual tweet data
    # It will return a list at the end containing all the tweets and their data
    def fixjson(self, dirIn, fileName, coords_only, emojify):
        with open(dirIn+'/'+fileName, 'r') as f:
            current = 0
            brk = True
            while brk:
                if current == 0:
                    tweet = ''
                else:
                    tweet = '{'
                while("}{" not in tweet):
                    chunk = f.readline()
                    tweet += chunk
                    if chunk == '':
                        tweet += '}}'
                        brk = False
                        break
                tweet = tweet[:-2]
                try:
                    dic = json.loads(tweet)
                    decoder.jsontocsv(self, dic, fileName, coords_only, emojify, current)
                except:
                    doNothing = 0
                current += 1
        
    # This text the text portion of the tweet and formats it into a way that we can read it  
    def parseText(self, data, trunc):       
        if trunc:
            try: text = data['extended_tweet']['full_text']
            except: text = '[missing data]'
        else:
            try: text = data['text']
            except: text = '[missing data]'
        #text = unicodedata.encode('ascii', 'ignore')
        text = re.sub('"', ' ["] ', text)
        text = re.sub(r'\\n', ' [RETURN] ', text)
        text = re.sub(r'\\r', ' [RETURN] ', text)
        text = re.sub(',', ' [COMMA] ', text)
        text = re.sub('&amp;', '&', text)
        text = re.sub('\\\\', ' ', text)
        return str(text.encode("unicode-escape"))[2:-1].lower()

    def emojify(self, text):
        if '\\u' in text:
            text = text.replace('\\\\u' , ' \\\\u')
            words = text.split()
            for word in words:
                if '\\u' in word:
                    if word in self.emojis.keys():
                            words[words.index(word)] = self.emojis[word]
            return ' '.join(words)
        return text

    # This clears the counters for everything
    # Used to gather data on each individual day
    def clear(self):
        self._tweet_count = 0
        self._tweets_checked = 0
        for kw in self.keywords.keys():
            self.keywords[kw] = 0   

    # Grabs the coordinates from the tweet
    # If the tweet has no coordinates it just leaves it empty
    def getCoords(self, data):
        try:    #attempts to get the coordinates from the tweet
            return data['coordinates']['coordinates']
        except: #if there are no coordinates then exception is called and make coords blank
            return ['','']

    # Goes through each keyword in the decoder and checks if it is in the tweet
    # If a keyword is in the tweet it will return a 1 so it knows it is to print the tweet in the csv file
    # If there is no keyword then return a 0 to skip over the tweet
    def checkForKWs(self, kwtext):
        kwtext = re.sub('#', '', kwtext)
        #kwtext = re.sub('@', '', kwtext)
        for kw in self.keywords.keys():     #for each keyword in the file
            if ' ' + kw + ' ' in kwtext:      #if the keyword is in the text
                self.keywords[kw] += 1             #add one to the keyword counter
                #print(kw)
                return 1
        return 0


    def writeToCSV(self, data, text, fn, count, truncated): 

        entities = []
        outfile = self.dirTemp+str(fn[:14]+'_data.csv')   ######################### <--- update to be more descriptive
        entities.append('\''+str(data['user']['id']))   #userID
        entities.append(data['user']['screen_name'].encode('utf-8')) #user
        try: entities.append(str(int(data['user']['utc_offset'])/3600)) #utc
        except TypeError: entities.append('') #utc
        entities.append(data['user']['created_at']) #created
        entities.append(str(data['user']['favourites_count'])) #faves
        entities.append(str(data['user']['followers_count'])) #followers
        entities.append(str(data['user']['friends_count'])) #following
        entities.append(str(data['user']['statuses_count'])) #tweets
        entities.append('\''+data['id_str']) #t_id
        try:
            entities.append('\''+data['retweeted_status']['id_str']) #t_id_rt
            entities.append(data['retweeted_status']['user']['screen_name']) #user_rt
            entities.append(data['retweeted_status']['retweet_count']) #rt_count
        except:
            entities.append('') #t_id_rt
            entities.append('') #user_rt
            entities.append(0) #rt_count
        entities.append(truncated) #truncated
        entities.append(text) #text
        date = data['created_at']
        entities.append(date) #date
        entities.append(date[:3]) #day
        entities.append(date[-4:]) #year
        entities.append(date[:7][-3:]) #month
        entities.append(date[:10][-2:]) #day
        entities.append(date[:13][-2:]) #hour
        entities.append(date[:16][-2:]) #min
        entities.append(date[:19][-2:]) #sec
        entities.append('http://twitter.com/'+str(data['user']['screen_name'].encode('utf-8'))+'/status/'+str(data['id_str'])) #url
        coords = decoder.getCoords(self, data)
        entities.append(coords[0]) #Lat
        entities.append(coords[1]) #Lon
        
        if truncated:
            try:
                for mentions in data['extended_tweet']['entities']['user_mentions']:
                    entities.append(mentions['screen_name'])
            except:
                doNothing = 0
        
        with open(outfile,'a') as csvfile:      
            saveFile = csv.writer(csvfile, delimiter=',', lineterminator='\n')        
            if count == 0:
                saveFile.writerow(['userID', 'username', 'retweet user', 'utc off', 'profile created',
                                   'favorites', 'followers', 'following', 'tweets', 'tweetID',
                                   'retweetID', 'retweet count','extended', 'text', 'date', 'day', 'year', 'month', 'day', 
                                   'hour', 'min', 'sec', 'url', 'lat', 'lon', 'mentions'])                    
            saveFile.writerow([entity for entity in entities])


    # This needs to take in the record list from the fixjson function and this will split it all up into a happy format for the csv file
    def jsontocsv(self, data, fileName, coords_only, emojify, count):
        
        # This is only needed to see when it is the first tweet in the list and the csv file will make a header before writing the tweet

        # This is the main loop where all the tweets in the record get checked
        try: truncated = (data['truncated'])
        except: truncated = False
        kwtext = decoder.parseText(self, data, truncated) # parse the text so that it can be examined
        decoder._tweets_checked += 1 #increment the number of tweets checked

        printed = 0
        coords = decoder.getCoords(self, data)    #gets the coords from the tweet
        if coords_only == 1:    #do we only care about tweets with coords?
            if coords[0] == '':
                printed = 1 #determines if a tweet has been written to the file
        if printed == 0:        
            if decoder.checkForKWs(self, kwtext) == 1: #means that a keyword was found in the tweet
                decoder._tweet_count += 1    #increment the count on the number of tweets printed
                if emojify == 1:
                    kwtext = decoder.emojify(self, kwtext)
                decoder.writeToCSV(self, data, kwtext, fileName, count, truncated)

        decoder.clear(self) #clears the data from that day




