# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Kodi Add-on for http://avezy.xyz
# Version 1.4.1
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#------------------------------------------------------------

import os
import sys
import urllib
import urllib2
import ssl
import json
from datetime import date
from datetime import time
from datetime import datetime
import plugintools
import tools
import xbmcgui
import xbmcaddon
import xbmcplugin

addon         = xbmcaddon.Addon('plugin.video.avezy')
addon_id      = addon.getAddonInfo('id')
addon_name    = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')

# Servidor origen
parserJsonUrl = "https://avezy.xyz/json.php"

# Devel
#parserJsonUrl = "http://localhost/arena/json.php"

# Debug servidor seleccionado
tools.debug("avezy Servidor: " + addon.getSetting('av_source_server'))
tools.debug("avezy Json: " + parserJsonUrl)

# Entry point
def run():
    #plugintools.log("avezy.run")

    # Get params
    params = plugintools.get_params()
    plugintools.log("avezy.run " + repr(params))

    if params.get("action") is None:
        plugintools.log("avezy.run No hay accion")
        listado_categorias(params)
    else:
        action = params.get("action")
        plugintools.log("avezy.run Accion: " + action)
        exec action+"(params)"
    
    plugintools.close_item_list()

# Main menu
def listado_categorias(params):
  plugintools.log("avezy.listado_categorias "+repr(params))

  # Definir URL del JSON
  jsonUrl = parserJsonUrl
  plugintools.log("avezy.listado_categorias Parsing: " + jsonUrl)
  
  # Peticion del JSON
  jsonSrc = makeRequest(jsonUrl)
  plugintools.log("avezy.listado_eventos Recibido jsonSrc: " + jsonSrc)

  # Comprobar formato respuesta
  if(is_json(jsonSrc) == False):
    errorTitle = 'Respuesta no JSON'
    errorMsg   = "La respuesta recibida no tiene formato JSON"
    mostrar_errores(errorTitle, errorMsg, jsonSrc)
    return

  # Cargar respuesta en json
  datos = json.loads(jsonSrc)

  # Comprobar error en la respuesta
  if('error' in datos):
    errorTitle = 'Error procesando categorias'
    errorMsg   = datos['msg']
    mostrar_errores(errorTitle, errorMsg)
    return
  
  categorias  = datos['categories']
  last_update = datos['last_update']
  
  # Informacion del evento
  titulo01 = "                    [COLOR skyblue]ArenaVision EZY[/COLOR] Version "+addon_version+" (Wazzu)"
  titulo02 = "                    [COLOR deepskyblue]Ultima actualizacion: "+last_update+"[/COLOR]"
  plugintools.add_item( title = titulo01 , thumbnail = generar_miniatura('default'), folder = False )
  plugintools.add_item( title = titulo02 , thumbnail = generar_miniatura('default'), folder = False )

  # Todos los eventos
  plugintools.add_item(
    action     = "mostrar_agenda" ,
    title      = "[COLOR deepskyblue][VER AGENDA COMPLETA][/COLOR]",
    plot       = '' ,
    url        = "plugin://plugin.video.avezy/?action=mostrar_agenda",
    thumbnail  = generar_miniatura('calendar'),
    isPlayable = True,
    folder     = True
  )

  # Todos los canales
  plugintools.add_item(
    action     = "mostrar_canales" ,
    title      = "[COLOR deepskyblue][TODOS LOS CANALES][/COLOR]",
    plot       = '' ,
    url        = "plugin://plugin.video.avezy/?action=mostrar_canales",
    thumbnail  = generar_miniatura('calendar'),
    isPlayable = True,
    folder     = True
  )

  # Listado de categorias
  for categoria in categorias:
      
      # Miniatura
      category_thumb = generar_miniatura(categoria['categoria'])
      plugintools.log("avezy.category_thumb "+category_thumb)
      
      # Items
      plugintools.add_item(
        action     = "listado_eventos" , 
        title      = "[UPPERCASE]" + categoria['categoria'] + "[/UPPERCASE]" + " (" +  categoria['items'] + " eventos)", 
        plot       = '' , 
        url        = "plugin://plugin.video.avezy/?action=listado_eventos&cat="+urllib.quote(categoria['categoria']),
        thumbnail  = category_thumb,
        isPlayable = True, 
        folder     = True
      )

# Listado de toda la agenda
def mostrar_agenda(params):
  plugintools.log("avezy.mostrar_agenda "+repr(params))

  # Parse json
  jsonUrl = parserJsonUrl + '?cat=all'
  plugintools.log("avezy.mostrar_agenda Parsing: " + jsonUrl)
  jsonSrc     = urllib2.urlopen(jsonUrl)
  datos       = json.load(jsonSrc)
  eventos     = datos['eventos']
  last_update = datos['last_update']

  # Titulo de la categoria
  titulo01 = "                [COLOR skyblue]AGENDA COMPLETA[/COLOR] (actualizado: "+last_update+")"
  plugintools.add_item( title = titulo01 , thumbnail = generar_miniatura('calendar'), action='', url='', isPlayable = False, folder = False )

  # Para cada evento
  for evento in eventos:
    title     = "[COLOR skyblue]" + evento['fecha'] + " [B]" + evento['hora'] + "[/B][/COLOR] " + evento['titulo']
    plot      = ""
    thumbnail = generar_miniatura(evento['categoria'])
    url       = "plugin://plugin.video.avezy/?action=listado_canales&evento="+evento['id']
    plugintools.add_item(
      action="listado_canales" ,
      title=title ,
      plot=plot ,
      url=url ,
      thumbnail=thumbnail ,
      isPlayable=True,
      folder=True
    )

# Listado de todos los canales
def mostrar_canales(params):
  plugintools.log("avezy.mostrar_canales "+repr(params))

  # Parse json
  jsonUrl = parserJsonUrl + '?cat=channels'
  plugintools.log("avezy.mostrar_canales Parsing: " + jsonUrl)
  jsonSrc     = urllib2.urlopen(jsonUrl)
  datos       = json.load(jsonSrc)
  canales     = datos['canales']
  last_update = datos['last_update']

  # Titulo de la categoria
  titulo01 = "[COLOR skyblue]CANALES ARENAVISION[/COLOR] (actualizado: "+last_update+")"
  plugintools.add_item( title = titulo01 , thumbnail = generar_miniatura('calendar'), action='', url='', isPlayable = False, folder = False )

  # Canales del evento
  for canal in canales:
    canal_nombre = canal['canal']
    canal_enlace = canal['enlace']
    canal_type   = canal['type']
    canal_mode   = canal['mode']

    etiqueta = "[B]" + canal_nombre + "[/B]"

    enlace   = "plugin://program.plexus/?url=" + canal_enlace + "&mode="+canal_mode+"&name=" + canal_nombre
    plugintools.add_item( 
      title      = "Arenavision " + canal['canal'] , 
      url        = enlace , 
      thumbnail  = generar_miniatura('default') , 
      isPlayable = True, 
      folder     = False 
    )

# Listado de eventos de una categoria
def listado_eventos(params):
  plugintools.log("Python Version: " + (sys.version))
  plugintools.log("avezy.listado_eventos "+repr(params))
  categoria = params['cat']
  
  # Parse json
  jsonUrl = parserJsonUrl + '?cat='+urllib.quote(categoria)
  plugintools.log("avezy.listado_eventos Parsing: " + jsonUrl)
  jsonSrc = makeRequest(jsonUrl)
  plugintools.log("avezy.listado_eventos Recibido jsonSrc: " + jsonSrc)

  # Cargar respuesta en json
  datos = json.loads(jsonSrc)

  # Comprobar error en la respuesta
  if('error' in datos):
    errorTitle = 'Error procesando eventos'
    errorMsg   = datos['msg']
    mostrar_errores(errorTitle, errorMsg)
    return

  eventos     = datos['eventos']
  last_update = datos['last_update']

  # Titulo de la categoria
  titulo01 = "                [COLOR skyblue][UPPERCASE]"+categoria+"[/UPPERCASE][/COLOR] (actualizado: "+last_update+")"
  plugintools.add_item( title = titulo01 , thumbnail = generar_miniatura('calendar'), action='', url='', isPlayable = False, folder = False )
  
  # Para cada evento
  for evento in eventos:
    # ToDo eventos del pasado
    #plugintools.log("Fecha: " + fecha_hora)
    #showDate = datetime.strptime(fecha_hora, "%d/%m/%y %H:%M:%S").date()
    #todayDate = datetime.today().date()
    #if(showDate < todayDate):
    #  color = 'grey'
    #else:
    #  color = 'skyblue'
    color = 'skyblue'
    title     = "[COLOR "+color+"]" + evento['fecha'] + " [B]" + evento['hora'] + "[/B][/COLOR] " + evento['titulo']
    plot      = ""
    thumbnail = generar_miniatura(categoria)
    url       = "plugin://plugin.video.avezy/?action=listado_canales&evento="+evento['id']
    plugintools.log("avezy.listado_eventos add_item:" + evento['id'])
    plugintools.add_item(
      action="listado_canales" , 
      title=title , 
      plot=plot , 
      url=url ,
      thumbnail=thumbnail , 
      isPlayable=True, 
      folder=True
    )

# Listado de canales de un evento
def listado_canales(params):
  plugintools.log("avezy.listado_canales "+repr(params))
  evento = params['evento']
  
  # Parse json
  jsonUrl = parserJsonUrl + '?evento='+evento
  plugintools.log("avezy.listado_canales Parsing: " + jsonUrl)
  jsonSrc = makeRequest(jsonUrl)
  plugintools.log("avezy.listado_eventos Recibido jsonSrc: " + jsonSrc)

  # Cargar respuesta en json
  evento = json.loads(jsonSrc)

  # Comprobar error en la respuesta
  if('error' in evento):
    errorTitle = 'Error procesando canales'
    errorMsg   = evento['msg']
    mostrar_errores(errorTitle, errorMsg)
    return
    return
  
  # Datos del evento
  categoria = evento['categoria']
  titulo    = evento['titulo']
  fecha     = evento['fecha']
  canales   = evento['canales']

  # Informacion del evento (categoria, fecha)
  titulo01 = "[COLOR skyblue] " + categoria + " - " + fecha + "[/COLOR]"
  plugintools.add_item( title = titulo01 , thumbnail = generar_miniatura('calendar'), isPlayable = False, folder = False )
  
  # Informacion del evento (titulo)
  titulo01 = "[COLOR skyblue] " + titulo + "[/COLOR]"
  plugintools.add_item( title = titulo01 , thumbnail = generar_miniatura(categoria), isPlayable = False, folder = False )

  # Canales del evento
  for canal in canales:
    canal_nombre = canal['canal']
    canal_enlace = canal['enlace']
    canal_idioma = canal['idioma']
    canal_mode   = canal['mode']
  
    etiqueta = "["+canal_idioma+"] [B][COLOR red]" + canal_nombre + "[/COLOR][/B]"

    enlace   = "plugin://program.plexus/?url=" + canal_enlace + "&mode="+canal_mode+"&name=" + titulo
    plugintools.add_item( 
      title      = etiqueta , 
      url        = enlace , 
      thumbnail  = generar_miniatura('default') , 
      isPlayable = True, 
      folder     = False 
    )

# Ruta de la miniatura
def generar_miniatura(categoria):
  thumb = categoria.lower().replace(" ", "_")
  thumb_path = os.path.dirname(__file__) + "/resources/media/" + thumb + ".png"
  if(os.path.isfile(thumb_path)):
    # Miniatura especifica
    category_thumb = "special://home/addons/" + addon_id + "/resources/media/" + thumb + ".png"
  else:
    # Miniatura generica
    category_thumb = "special://home/addons/" + addon_id + "/resources/media/default.png"
  return category_thumb

# Mostrar errores
def mostrar_errores(titulo, mensaje, debug=""):
    plugintools.log("ERROR: " + titulo)

    errTitle = "[COLOR red][UPPERCASE]ERROR: " + titulo + "[/UPPERCASE][/COLOR]"
    errMsg   = mensaje + "[CR]Para mas informacion, por favor, consulta el registro."
    
    plugintools.add_item( title = errTitle, thumbnail = generar_miniatura('default'), action='', url='', isPlayable = False, folder = False )
    plugintools.add_item( title = errMsg, thumbnail = generar_miniatura('default'), action='', url='', isPlayable = False, folder = False )
    return

# Realizar peticion HTTP
def makeRequest(url):
  plugintools.log("makeRequest: " + url)

  # Verificacion SSL
  ctx = ssl.create_default_context()
  ctx.check_hostname = False
  ctx.verify_mode = ssl.CERT_NONE

  try:
    req      = urllib2.Request(url)
    response = urllib2.urlopen(req, context=ctx)
    data     = response.read()
    response.close()
    return data
  except urllib2.URLError, e:
    errorMsg = str(e)
    plugintools.log(errorMsg);
    xbmc.executebuiltin("Notification(avezy,"+errorMsg+")")
    data_err = []
    data_err.append(['error', True])
    data_err.append(['msg', errorMsg])
    data_err = json.dumps(data_err)
    data_err = "{\"error\":\"true\", \"msg\":\""+errorMsg+"\"}"
    return data_err

# Comprobar si la cadena es json
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False
    return True

# Main loop
run()