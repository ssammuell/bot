import telebot
import requests
import re
from bs4 import BeautifulSoup

BOT_TOKEN = '6880103592:AAGMSqaIM1gOGmvPEC52IiE50cTpS3v64Pc'
BOT_ID ='269014811'

def bot_send_text(bot_message):
    send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id='+BOT_ID+'&parse_mode=Markdown&text='+bot_message

    response = requests.get(send_text)
    print(response)
    return response

def miFuncion():
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
miFuncion()
#test_bot = bot_send_text('¡Hola, Telegram!')
