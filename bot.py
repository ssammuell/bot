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
CHANEL_ID='base_femenino_dinamo_guadalajara'
CHANEL_ID_TEST='testbotfutbol'
EQUIPOS=[['Alevín Femenino','Álvaro-?',10,1296],['Alevín-Infantil Femenino','Óscar-Julia',16,1309]]
EQUIPOS_WSP=[['Alevín-Infantil Femenino','Óscar-Julia',16,1309]]
TIEMPO_JORNADA=5
timenow = time.localtime()

def sendWSP(message):
    message=message.replace('<strong>','*')
    message=message.replace('</strong>','*')
    message=message.replace('%2B','+')
    message=message.replace('<i>','_')
    message=message.replace('</i>','_')
    apikey = "5e7278b8fbmshd2319df33124ad0p14b41fjsnd92a08001452"
    gid = "120363201248192030"
    url = "https://whin2.p.rapidapi.com/send"
    headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": apikey,
	"X-RapidAPI-Host": "whin2.p.rapidapi.com"}
    try:         
        url = "https://whin2.p.rapidapi.com/send2group"
        querystring = {"gid":gid}
        response = requests.request("POST", url, json={"text":message}, headers=headers, params=querystring) 
        print(response)
    except requests.ConnectionError:
        return("Error: Connection Error")

def bot_send_text(bot_message):
        
    #print(bot_message)
    #send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id='+BOT_ID+'&parse_mode=Markdown&text='+bot_message
    send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id=@'+CHANEL_ID_TEST+'&parse_mode=HTML&text='+bot_message
    #send_text = 'https://api.telegram.org/bot'+BOT_TOKEN+'/sendMessage?chat_id=@'+CHANEL_ID+'&parse_mode=HTML&text='+bot_message

    response = requests.get(send_text)
    print(response)
    return response    
    
def showGolaverage(valor):
    if valor>0:
        return '%2B'+str(valor)
    else:        
        return str(valor)
    

def sendClasificacion(categoria, grupo):
    response = requests.get('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat='+categoria+'&gru='+grupo+'&ver=C')
    
    if (response.status_code==200):
        cadena='\n🏃🏼‍♀️⚽🏃🏼‍♀️ <strong>CLASIFICACIÓN</strong> 🏃🏼‍♀️⚽🏃🏼‍♀️\n\n'       
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rows = soup.findAll('tr', attrs={'class': re.compile('fila.*')})    
        i=0
        for row in rows:
            posicion = row.find('td', attrs={'class': 'posicion'}).text
            equipo = row.find('td', attrs={'class': 'equipo'}).text
            puntos = row.find('td', attrs={'class': 'puntos'}).text
            golesfavor=int(row.findAll('td')[3].text)
            golescontra=int(row.findAll('td')[4].text)
            partidosjugados=row.findAll('td')[5].text
            #partidosganados=row.findAll('td')[6]
            #partidosempatados=row.findAll('td')[7]
            #partidosperdidos=row.findAll('td')[8]                        
            
            cadena+='<strong>'
            if i == 0 :
                cadena+='🥇'+str(posicion)+' .- '+str(equipo)+'</strong>\n  Puntos: '+str(puntos) +' ('+showGolaverage(golesfavor-golescontra)+')\n  Partidos Jugados: '+partidosjugados+"\n"
            else:
                if i==1:
                    cadena+='🥈'+str(posicion)+' .- '+str(equipo)+'</strong>\n  Puntos: '+str(puntos) +' ('+showGolaverage(golesfavor-golescontra)+')\n  Partidos Jugados: '+partidosjugados+"\n"
                else:
                    if i==2:
                        cadena+='🥉'+str(posicion)+' .- '+str(equipo)+'</strong>\n  Puntos: '+str(puntos) +' ('+showGolaverage(golesfavor-golescontra)+')\n  Partidos Jugados: '+partidosjugados+"\n"
                    else:
                        cadena+=str(posicion)+' .- '+str(equipo)+'</strong>\n  Puntos: '+str(puntos) +' ('+showGolaverage(golesfavor-golescontra)+')\n  Partidos Jugados: '+partidosjugados+"\n"
            i=i+1
        
        return(cadena)
    else:
        return ''
def isJornadaPasada(texto):        
    return (datetime.strptime(texto.split('-')[1],' %d/%m/%y') < datetime.now())

def diasHastaProximaJornada(texto):
    dateFinal=datetime.strptime(texto.split('-')[1],' %d/%m/%y')
    dateInicial= datetime.now()
    duration_in_s=(dateFinal-dateInicial).total_seconds() 
    return divmod(duration_in_s, 86400)[0] 

def getNombre(equipo):
    if (equipo.find_all('acronym')):
        return ('<strong>'+(equipo.find_all('acronym')[0].get('title')).strip())+'</strong>'
    else :
        return '<strong>'+(equipo.text.strip())[0:15]+'</strong>'

def getInfoJornada(numJornada,categoria,grupo):
    cadena=''    
    url=('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat='+categoria+'&gru='+grupo+'&ver=R&jor='+numJornada)
    myResponse = requests.get(url)
    if (myResponse.status_code == 200):
        soup = BeautifulSoup(myResponse.text, 'html.parser')
        tabla=(soup.find('tbody')).find_all('tr')
        for item in tabla:
            cadena+=getNombre(item.find(attrs={'class':'EquipoL'}))+'  VS  '+getNombre(item.find(attrs={'class':'EquipoV'}))
            ## Obtengo los resulados
            if len(item.find_all(attrs={'class':'puntos'}))>0 :
                cadena+=(' ('+ str(item.find_all(attrs={'class':'puntos'})[0].text)+' - '+str(item.find_all(attrs={'class':'puntos'})[1].text)+')')
            ## Obtengo la hora
            if len(item.find_all(attrs={'class':'hora'}))>0 :
                cadena+=('\n ⌚ '+ str(item.find_all(attrs={'class':'hora'})[0].text)+'')
                ##Obtengo la ubicacion
                if len(item.find_all(attrs={'class':'imgBandera'}))>0 :
                    tagBandera=item.find_all(attrs={'class':'imgBandera'})[0]
                    childrens= tagBandera.findChildren("img",recursive=False)
                    if (len(childrens)>0):
                        cadena+='\n 📌'+(((str(childrens[0].get('title'))).split('-'))[0])
                        cadena+='\n'
                else:
                    cadena+='\n ❓ <i>Pendiente</i>'
                    cadena+='\n'
            cadena+='\n'
    return cadena

def getResultadosJornada(numJornada,categoria,grupo):
    cadena=''    
    url=('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat='+categoria+'&gru='+grupo+'&ver=R&jor='+numJornada)
    myResponse = requests.get(url)
    if (myResponse.status_code == 200):
        soup = BeautifulSoup(myResponse.text, 'html.parser')
        lAvisos=soup.find_all(attrs={'class':'txtaviso'})
        for aviso in lAvisos:
            cadena+='\n 👀 <strong>INFORMACIÓN PROVISIONAL</strong>👀\n'
        tabla=(soup.find('tbody')).find_all('tr')
        for item in tabla:
            cadena+=(item.find(attrs={'class':'EquipoL'})).text.replace('[...]','').strip()[0:15]+'  VS  '+(item.find(attrs={'class':'EquipoV'})).text.replace('[...]','').strip()[0:15]
            ## Obtengo los resulados
            if len(item.find_all(attrs={'class':'puntos'}))>0 :
                cadena+=('\n'+ str(item.find_all(attrs={'class':'puntos'})[0].text)+' - '+str(item.find_all(attrs={'class':'puntos'})[1].text))            
            cadena+='\n'
        
    return cadena         
    

def getNumJornada(texto,categoria,grupo):    
    return getInfoJornada(texto.split(' ')[1],categoria,grupo)

def getJornadas(categoria, grupo):
    url=('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat='+categoria+'&gru='+grupo+'&ver=R')    
    response = requests.get(url)    
        
    if (response.status_code==200):            
            #cadena='<strong>🗓️ HORARIOS JORNADA 🗓️</strong>'  
            cadena=''           
            soup = BeautifulSoup(response.text, 'html.parser')
            jornadas = soup.find(attrs={'id':'jor'})
            checkJornada=False
            diasJornada=0            
            jornadaPasada=False
            for item in jornadas.find_all('option'):   
                             
                if '-' in item.text:                     
                     if isJornadaPasada(item.text) :                         
                        ## cadena+=('<i>'+item.text+ '</i> \n')
                        ## cadena+=(getNumJornada(item.text,categoria,grupo))                                               
                        jornadaPasada=True
                     else:
                         if not checkJornada: #primera jornada
                             checkJornada=True
                             diasJornada=diasHastaProximaJornada(item.text)                             
                         
                         #Sólo pinto la jornada actual
                         if (diasHastaProximaJornada(item.text)<5):
                             cadena='<strong>🗓️ '+(item.text)+' 🗓️</strong>'  
                                #cadena+=(item.text)
                         
                         if jornadaPasada:
                            jornadaPasada=False
                            if ((diasHastaProximaJornada(item.text)<5)): #Sólo pinto la jornada actual
                                cadena+='\n'
                                cadena+=(getNumJornada(item.text,categoria,grupo)) 
                            
                cadena+='\n'

            if (diasJornada>TIEMPO_JORNADA):
                return 'SEMANA DE DESCANSO 🎄 🎄 .\n A disfrutar del Fin de Semana!!\n'    
                
            else:                
                return cadena
                #publica la clasificacion
                #sendClasificacion(categoria,grupo)
               
# Listado de las Jornadas del Calendario
def getArrayJorandas(categoria,grupo):
    url=('http://deportesclm.educa.jccm.es/index.php?prov=19&tipo=&fase=11&dep=FT&cat='+categoria+'&gru='+grupo+'&ver=R')        
    response = requests.get(url)
    res=[]    
    
    if (response.status_code==200):   
        soup = BeautifulSoup(response.text, 'html.parser')        
        lJornadas = soup.find(attrs={'id':'jor'})                 
        for item in lJornadas:                    
            try:
               if item.text and ('-' in item.text): 
                numero = (item.text.split('-')[0].strip()).split(' ')[1]
                fechaText = item.text.split('-')[1].strip()
                fecha=datetime.strptime(fechaText,'%d/%m/%y')                 
                res.append([numero,fecha])  
            except:
                print('error: '+str(item))                                             
    
    return res    

#Última jorndada disputada, si no hubira habido jornada no se devuelve nada
def getUltimaJornadaDisputada(categoria,grupo):
    lJornadas=getArrayJorandas(categoria,grupo)    
    res='0'    
    for item in lJornadas:        
        duration_in_s=(datetime.now()-item[1]).total_seconds() 
        tiempo=(divmod(duration_in_s, 86400)[0] )
        if tiempo >0 and tiempo < 5:
            res=item[0]
    
    return res;
    
        
        

weekDay=datetime.now().weekday()
hourDay=datetime.now().hour
print('Telegram Bot Start! Day:'+str(weekDay)+' - Hour :'+str(hourDay)) 

#publica la proxima jornada TELEGRAM
for item in EQUIPOS:    
    
    
    if True:
        ## Lunes entre 12H-15h Resultados/Jornada + Clasificación    
        if weekDay == 0 and hourDay < 14:                      
        #and hourDay > 12:
            cadenaBot='👇💚🖤 ⚽<strong>'+item[0]+'</strong>⚽🖤💚👇\n'+item[1]+'\n'
            jornadaDisputada=getUltimaJornadaDisputada(str(item[2]),str(item[3]))                        
            cadenaBot+=('\n\n<strong>⚽ RESULTADOS Jornada '+jornadaDisputada+' ⚽</strong>\n\n') 
            cadenaBot+=getResultadosJornada(jornadaDisputada,str(item[2]),str(item[3]))            
            cadenaBot+=sendClasificacion(str(item[2]),str(item[3]))            
            bot_send_text(cadenaBot)
        
        ## Miercoles antes de las 12h Resultados/Jornada 
        if weekDay==2 and hourDay < 12:                        
            bot_send_text('👇💚🖤 ⚽<strong>'+item[0]+'</strong> ⚽🖤💚👇\n'+item[1])            
            bot_send_text(getJornadas(str(item[2]),str(item[3])))
            

#publica la proxima jornada WHATSAPP
for item in EQUIPOS_WSP:    
    
    
    if True:
        ## Lunes entre 12H-15h Resultados/Jornada + Clasificación    
        if weekDay == 0 and hourDay < 14:                        
            jornadaDisputada=getUltimaJornadaDisputada(str(item[2]),str(item[3]))                        
            cadenaBot=('\n⚽<strong>RESULTADOS Jornada '+jornadaDisputada+'</strong>⚽\n') 
            cadenaBot+=getResultadosJornada(jornadaDisputada,str(item[2]),str(item[3]))            
            cadenaBot+=sendClasificacion(str(item[2]),str(item[3]))            
            sendWSP(cadenaBot)
        
        ## Miercoles antes de las 12h Resultados/Jornada 
        if weekDay==2 and hourDay < 12:                                                                  
            sendWSP(getJornadas(str(item[2]),str(item[3])))   
            
