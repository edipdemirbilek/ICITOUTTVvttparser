# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 22:42:44 2016

@author: edipdemirbilek
"""

import codecs
import copy
import sys
import os
import re
import tempfile
from bs4 import BeautifulSoup
import urllib3
import requests


if len(sys.argv)<2:
    print("Please provide episode URL as argument.")
    raise SystemExit
    
showEpisodeURL=sys.argv[1]

if sys.platform.startswith('win'):
    inputdir="C:/Users/edip.demirbilek/Dropbox/GitHub/ICITOUTTV/"
elif sys.platform.startswith('darwin'):
    inputdir="/Users/edipdemirbilek/Dropbox/GitHub/ICITOUTTV/"

tempDir=tempfile.gettempdir()

step1=True #Download
step2=True #Preprocess
step3=True #Extract Text
step4=True #Add Timestamps
            
def findSubstring(s1, s2):
    len_s1 = len(s1)
    len_s2 = len(s2)
    
    if len_s1 >1 and len_s2>1:
        len_min = min(len_s1, len_s2)
        
        for i in range (len_min, 1, -1):
            sub_s1=s1[len(s1)-i:]
            sub_s2=s2[:i]
            if sub_s1 == sub_s2:
                return i
    return 0
    
if step1:
    print ("Downloading Episode HTML File From: "+showEpisodeURL)
    http = urllib3.PoolManager()
    r  = requests.get(showEpisodeURL)
    
    print ("Processing HTML File for VTT information.")
    soup = BeautifulSoup(r.text, 'html.parser')

    lists = soup.find_all('meta')
    filename=re.search('2016.*jpg', str(lists[-1])).group(0)[:-7] +'.vtt'
    fullURL="http://static.tou.tv/medias/webvtt/"+filename
    
    print ("Downloading Episode VTT File From: "+fullURL)
    f = open(inputdir+filename,'wb')
    f.write(requests.get(fullURL).content)
    f.close()
    
base=os.path.basename(filename)
filename = os.path.splitext(base)[0]

vttFile=inputdir+filename+".vtt"
preFile=tempDir+filename+".pre"
extractFile=tempDir+filename+".extract"
txtFile=inputdir+filename+".txt"
    
if step2:
    fi = codecs.open(vttFile, "r", "utf-8")
    fo = codecs.open(preFile, "w", "utf-8")
    
    longLine=""
    
    print("Merging multiple lines into one line.")
    for line in fi:
        if len(line) > 1:
            longLine+=line.rstrip('\n')+" "
            
        else:
            longLine.rstrip(' ')
            fo.write(longLine)
            fo.write("\n")
            #print(longLine)
            longLine=""
    
    fo.close()
    fi.close()

if step3:
    fi = codecs.open(preFile, "r", "utf-8")
    fo = codecs.open(extractFile, "w", "utf-8")
    i=0
    lastLine=""
    first_line = fi.readline()
    
    print("Removing duplicates in text.")
    for line in fi:

        newLine=copy.copy(line[30:].rstrip('\n'))
        #print(str(i))
        
        maxStrInd = findSubstring(lastLine, newLine)                   
                    
        if maxStrInd > 0:            
            lastLine+=copy.copy(newLine[maxStrInd:])
        else:        
            lastLine+=" "+copy.copy(newLine)
                
        i+=1
            
    fo.write(lastLine.replace("- ", "\n- "))
    fo.close()
    fi.close()
    


if step4:
    fi_extract = codecs.open(extractFile, "r", "utf-8")
    fi_pre = codecs.open(preFile, "r", "utf-8")
    fo = codecs.open(txtFile, "w", "utf-8")
    
    pre_lines=fi_pre.readlines()
    index=0
    
    print ("Adding timestamps.")
    for line in fi_extract:
        if line[:2] =="- " and len(line)>3:
            token="- "+line[2:].split()[0]     
            
            while index < len(pre_lines):
                if pre_lines[index].find(token) != -1:
                    timeStamp=pre_lines[index][:8]
                    line=line.replace(token, timeStamp+" "+token)
                    fo.write(line)
                    break
                index+=1
       
    fo.close()
    fi_extract.close()
    fi_pre.close()
    
    os.remove(vttFile) if os.path.exists(extractFile) else None
    os.remove(extractFile) if os.path.exists(extractFile) else None
    os.remove(preFile) if os.path.exists(preFile) else None
    
    print("Done!") 
    print("Content at: "+txtFile) 
    
    
                
        
                
        
        
        
        
        
        
        
        
        
        
        