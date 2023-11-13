import telebot
import requests
import re
import schedule
import time
import pycron
from bs4 import BeautifulSoup


BOT_TOKEN = '6880103592:AAGMSqaIM1gOGmvPEC52IiE50cTpS3v64Pc'
BOT_ID ='269014811'

def bot_send_text(bot_message):
    send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id='+BOT_ID+'&parse_mode=Markdown&text='+bot_message

    response = requests.get(send_text)
    print(response)
    return response

def sendClasificacion():
    response = requests.get('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat=16&gru=1309&ver=C')
    
    if (response.status_code==200):
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.findAll('tr', attrs={'class': re.compile('fila.*')})    
        cadena='\n'
        for row in rows:
            posicion = row.find('td', attrs={'class': 'posicion'}).text
            equipo = row.find('td', attrs={'class': 'equipo'}).text
            puntos = row.find('td', attrs={'class': 'puntos'}).text
            cadena+=(str(posicion)+' .- '+str(equipo)+' - Puntos: '+str(puntos) +'\n\n')
        
        bot_send_text(cadena)


#test_bot = bot_send_text('¡Hola, Telegram!')

while True:
    timenow = time.localtime()
    print("I'm working...", str( time.strftime("%H:%M", timenow) )) 
#                     |----------------- on minute 0, so every full hour
#                     |  |--------------- on hours 9 till 16
#                     |  |   | |-------- every day in month and every month
#                     V  V   V V  v------ on weekdays Monday till Friday
    if pycron.is_now('0 17-22 * * mon-fri'):
        sendClasificacion()
time.sleep(60)
