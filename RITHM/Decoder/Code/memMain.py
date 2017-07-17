# Test Program to decypher the template

import time, os, re, sys, timeit
from memDecode import decoder
from combine import csvcombine

start = timeit.default_timer()

directory = "//home/jason/repos/RITHM/decoder/" #this is the directory to try first
try: 
    directory = os.path.dirname(os.path.realpath(__file__))+'/' #otherwise it will take the directory that this file is in and get the template.txt from there
except: 
    print('Failed to set dir_path programmatically!\n',
              'Parser works better if run from command line.\n',
              'Setting dir_path to: ', directory)
    input('Press Enter to continue...')

with open(directory + "template.txt", 'r') as template:
    kwMode = False
    for line in template:
        line = re.sub('\r', '', line)
        line = re.sub('\n', '', line)
        line = line.lower()
        if line[:1] =='#' or line == '':
            doNothing = 0
        else:
            if 'dir_in:' in line or 'dirin:' in line:
                dirIn = str(line)[str(line).find(":")+2:]
            if 'dir_out:' in line or 'dirout:' in line:
                dirOut = str(line)[str(line).find(":")+2:]
            if 'dir_temp:' in line or 'dirtemp:' in line:
                dirTemp = str(line)[str(line).find(":")+2:]
            if 'start:' in line or 'begin:' in line:
                start = (str(line)[str(line).find(":")+1:])
                start = re.sub('-', '', start)
                start = re.sub('/', '', start)
                start = re.sub(' ', '', start)
                start = int(start)
            if 'end:' in line or 'finish:' in line:
                end = (str(line)[str(line).find(":")+1:])
                end = re.sub('-', '', end)
                end = re.sub('/', '', end)
                end = re.sub(' ', '', end)
                end = int(end)
            if 'geo:' in line or 'location:' in line or 'loc:' in line:
                geo = str(line)[str(line).find(":")+2:]
                if geo == "1" or geo == 'true' or geo == 'yes':
                    geo = 1
                else:
                    geo = 0
            if 'emojis:' in line or 'emojify:' in line or 'emoji:' in line or 'emojifile:' in line or 'emoji_file:' in line:
                emoji_file = str(line)[str(line).find(":")+2:]
                emojify = 0
                if emoji_file != '':
                    emojify = 1
            if 'combine:' in line:
                combine = str(line)[str(line).find(":")+2:]
                if combine == 'month' or combine == 'monthly' or combine == 'm' or combine == 'mon':
                    combine == 'monthly'
                if combine == 'all' or combine == '' or combine == 'everything':
                    combine == 'all'
            if 'clear:' in line or 'erase:' in line:
                clear = str(line)[str(line).find(":")+2:]       #Clear will remove all files in the tempDir when finished
                if clear == '1' or clear == 'true' or clear == 'yes':
                    clear = 1
                else:
                    clear = 0
            if 'keywords:' in line or 'kws:' in line:
                keywords = {}
                kw = str(line)[str(line).find(":")+2:]
                if kw == '' or kw == ' ':
                    doNothing = 0
                else:
                    keywords.update({kw:0})
                kwMode = True
            if kwMode:
                if line.rstrip() not in keywords.keys():
                    if line.rstrip() != '' and line.rstrip() != ' ':
                        keywords.update({line.rstrip():0})

if clear == 1:
    files = sorted(os.listdir(dirTemp))
    for f in files:
        os.remove(dirTemp+f)

files = sorted(os.listdir(dirIn))
print("\nREADING TWEETS FROM " + str(start) + ' to ' + str(end) +'\n')
#read all the files in the directory
t = str(time.time())
for f in files:
    if f[-5:] =='.json':
        if int(f[:8]) >= start:
            if int(f[:8]) <= end:
                d = decoder(keywords, dirOut, directory, dirTemp, emojify, emoji_file)
                d.fixjson(dirIn, f, geo, emojify)

c = csvcombine(dirOut, directory, dirTemp)
c.combinecsv(combine, clear)

stop = timeit.default_timer()
print(stop - start)
