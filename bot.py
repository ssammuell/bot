import telebot
import requests
import re
import schedule
import time
import pycron
from bs4 import BeautifulSoup
from datetime import datetime



BOT_TOKEN = '6880103592:AAGMSqaIM1gOGmvPEC52IiE50cTpS3v64Pc'
BOT_ID ='269014811'
timenow = time.localtime()

def bot_send_text(bot_message):
        
    #send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id='+BOT_ID+'&parse_mode=Markdown&text='+bot_message
    send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id=@femenino_dinamo_guadalajara&parse_mode=markdown&text='+bot_message

    response = requests.get(send_text)
    print(response)
    return response

def sendClasificacion():
    response = requests.get('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat=16&gru=1309&ver=C')
    
    if (response.status_code==200):
        cadena='\n'       
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.findAll('tr', attrs={'class': re.compile('fila.*')})    
        
        for row in rows:
            posicion = row.find('td', attrs={'class': 'posicion'}).text
            equipo = row.find('td', attrs={'class': 'equipo'}).text
            puntos = row.find('td', attrs={'class': 'puntos'}).text
            cadena+=(str(posicion)+' .- '+str(equipo)+'\nPuntos: '+str(puntos) +'\n\n')
        
        bot_send_text(cadena)

def isJornadaPasada(texto):        
    return (datetime.strptime(texto.split('-')[1],' %d/%m/%y') < datetime.now())

def getNombre(equipo):
    if (equipo.find_all('acronym')):
        return ((equipo.find_all('acronym')[0].get('title')).strip())[0:15]
    else :
        return (equipo.text.strip())[0:15]

def getInfoJornada(numJornada):
    cadena=''
    myResponse = requests.get('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat=16&gru=1309&ver=R&jor='+numJornada)
    if (myResponse.status_code == 200):
        soup = BeautifulSoup(myResponse.text, 'html.parser')
        tabla=(soup.find('tbody')).find_all('tr')
        for item in tabla:
            cadena+=getNombre(item.find(attrs={'class':'EquipoL'}))+'  VS  '+getNombre(item.find(attrs={'class':'EquipoV'}))
            if len(item.find_all(attrs={'class':'puntos'}))>0 :
                cadena+=(' ('+ str(item.find_all(attrs={'class':'puntos'})[0].text)+' - '+str(item.find_all(attrs={'class':'puntos'})[1].text)+')\n')
    return cadena         
    

def getNumJornada(texto):    
    return getInfoJornada(texto.split(' ')[1])

def getJornadas():
    response = requests.get('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat=16&gru=1309&ver=R')
    cadena='\n'
    cadenaResultados='\n'
    if (response.status_code==200):
            cadena='\n'  
            cadenaJornadas='\n'          
            soup = BeautifulSoup(response.text, 'html.parser')
            jornadas = soup.find(attrs={'id':'jor'})
            
            for item in jornadas.find_all('option'):                
                if '-' in item.text:
                     
                     if isJornadaPasada(item.text) :                         
                        cadena+=('\n\n_'+item.text+ ' (finalizada) _ \n')
                        cadena+=(getNumJornada(item.text))
                       
                     else:
                        cadena+=(item.text+'\n')
            
            bot_send_text(cadena)
            
                



print('Telegram Bot Start!') 

#publica la proxima jornada
getJornadas()

#publica la clasificacion
sendClasificacion()

while False:
    
   # print("I'm working...", str( time.strftime("%H:%M", timenow) )) 
#                     |----------------- on minute 0, so every full hour
#                     |  |--------------- on hours 9 till 16
#                     |  |  | |-------- every day in month and every month
#                     V  V  V V  v------ on weekdays Monday till Friday
    if pycron.is_now('1 1 11-13 * * mon-fri'):        
        sendClasificacion()
        time.sleep(60)
time.sleep(60)
