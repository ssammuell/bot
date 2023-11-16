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
CHANEL_ID='femenino_dinamo_guadalajara'
CHANEL_ID_TEST='testbotfutbol'
EQUIPOS=[['Alevín Femenino',10,1296],['Infantil Femenino',16,1309]]
TIEMPO_JORNADA=5
timenow = time.localtime()

def bot_send_text(bot_message):
        
    #print(bot_message)
    #send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id='+BOT_ID+'&parse_mode=Markdown&text='+bot_message
    send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id=@'+CHANEL_ID_TEST+'&parse_mode=HTML&text='+bot_message

    response = requests.get(send_text)
    print(response)
    return response    
    

def sendClasificacion(categoria, grupo):
    response = requests.get('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat='+categoria+'&gru='+grupo+'&ver=C')
    
    if (response.status_code==200):
        cadena='\n'       
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.findAll('tr', attrs={'class': re.compile('fila.*')})    
        i=0
        for row in rows:
            posicion = row.find('td', attrs={'class': 'posicion'}).text
            equipo = row.find('td', attrs={'class': 'equipo'}).text
            puntos = row.find('td', attrs={'class': 'puntos'}).text
            cadena+='<strong>'
            if i == 0 :
                cadena+='🥇'+str(posicion)+' .- '+str(equipo)+'</strong>\nPuntos: '+str(puntos) +'\n'
            else:
                if i==1:
                    cadena+='🥈'+str(posicion)+' .- '+str(equipo)+'</strong>\nPuntos: '+str(puntos) +'\n'
                else:
                    if i==2:
                        cadena+='🥉'+str(posicion)+' .- '+str(equipo)+'</strong>\nPuntos: '+str(puntos) +'\n'
                    else:
                        cadena+=str(posicion)+' .- '+str(equipo)+'</strong>\nPuntos: '+str(puntos) +'\n'
            i=i+1
        
        bot_send_text(cadena)

def isJornadaPasada(texto):        
    return (datetime.strptime(texto.split('-')[1],' %d/%m/%y') < datetime.now())

def diasHastaProximaJornada(texto):
    dateFinal=datetime.strptime(texto.split('-')[1],' %d/%m/%y')
    dateInicial= datetime.now()
    duration_in_s=(dateFinal-dateInicial).total_seconds() 
    return divmod(duration_in_s, 86400)[0] 

def getNombre(equipo):
    if (equipo.find_all('acronym')):
        return ((equipo.find_all('acronym')[0].get('title')).strip())[0:15].lower()
    else :
        return (equipo.text.strip())[0:15].lower()

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

def getJornadas(categoria, grupo):
    response = requests.get('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat='+categoria+'&gru='+grupo+'&ver=R')
    cadena='\n' 
    cadenaResultados='\n'
    if (response.status_code==200):
            cadena='\n'  
            cadenaJornadas='\n'          
            soup = BeautifulSoup(response.text, 'html.parser')
            jornadas = soup.find(attrs={'id':'jor'})
            checkJornada=False
            diasJornada=0
            for item in jornadas.find_all('option'):                
                if '-' in item.text:
                     diasHastaProximaJornada(item.text)
                     if isJornadaPasada(item.text) :                         
                        cadena+=('\n\n<i>'+item.text+ '</i> \n')
                        cadena+=(getNumJornada(item.text))
                        cadena+='\n'
                       
                     else:
                         if not checkJornada:
                             checkJornada=True
                             diasJornada=diasHastaProximaJornada(item.text)                             
                         cadena+=(item.text+'\n')

            if (diasJornada>TIEMPO_JORNADA):
                bot_send_text('Semana de descanso. A disfrutar del Fin de Semana!!')                
            else:                
                bot_send_text(cadena)
                #publica la clasificacion
                sendClasificacion(categoria,grupo)
            
                



print('Telegram Bot Start!') 
#publica la proxima jornada
for item in EQUIPOS:
    bot_send_text('<strong> 💪 💪 💪 '+item[0]+' 💪 💪 💪 </strong>')
    getJornadas(str(item[1]),str(item[2]))
    

