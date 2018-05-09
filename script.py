#!/usr/bin/python

import urllib
import urllib2
import os
import re
import sys
import xbmc
import xbmcgui
import xbmcaddon
import time
from datetime import datetime
import json

############################
#PVR.EPG.Cast		OK
#PVR.EPG.ChannelName    OK
#PVR.EPG.Director	OK
#PVR.EPG.Duration
#PVR.EPG.EndTime	OK
#PVR.EPG.Episode
#PVR.EPG.EpisodeName
#PVR.EPG.Genre		OK
#PVR.EPG.Label
#PVR.EPG.Plot		OK
#PVR.EPG.Season
#PVR.EPG.StartDate	OK
#PVR.EPG.StartTime	OK
#PVR.EPG.Title		OK
#PVR.EPG.Writer		OK
############################

__addon__ = xbmcaddon.Addon()
__addonID__ = __addon__.getAddonInfo('id')
__addonDir__            = __addon__.getAddonInfo("path")
__settings__   = xbmcaddon.Addon(id='script.pvrepg')
__addonname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__path__ = __addon__.getAddonInfo('path')
__LS__ = __addon__.getLocalizedString
__icon__ = xbmc.translatePath(os.path.join(__path__, 'icon.png'))


def writeLog(message, level=xbmc.LOGNOTICE):
        try:
            xbmc.log('[%s %s]: %s' % (__addonID__, __version__, message.encode('utf-8')), level)
        except Exception:
            xbmc.log('[%s %s]: Fatal: Message could not displayed' % (__addonID__, __version__), xbmc.LOGERROR)

################################################
# Gather current player ID
################################################
def currentplayer():
    query = {
            "jsonrpc": "2.0",
            "method": "Player.GetActivePlayers",
            "id": 1
            }
    res = json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))
    playerid = res['result'][0]['playerid']
    return playerid


################################################
# Gather current player Type (1->Video,2->Audio)
################################################
def get_player_type(playerid):
    query = {
            "jsonrpc": "2.0",
            "method": "Player.GetItem",
            "id": 1,
            "params": { "playerid" : playerid, "properties":["title", "album", "artist", "season", "episode", "showtitle", "tvshowid", "description"]}
            }
    res = json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))
    result = res['result']['item']['type']
    return result



################################################
# Get Logo for Channel
################################################
def pvrchannelid2logo(channelid):
    query = {
            "jsonrpc": "2.0",
            "method": "PVR.GetChannelDetails",
            "params": {"channelid": channelid, "properties": ["thumbnail"]},
            "id": 1
            }
    res = json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))
    if 'result' in res and 'channeldetails' in res['result'] and 'thumbnail' in res['result']['channeldetails']:
        return res['result']['channeldetails']['thumbnail']
    else:
        return False



################################################
# Gather what plays at the moment
################################################
def get_player_channel_id(playerid):
    query = {
            "jsonrpc": "2.0",
            "method": "Player.GetItem",
            "id": 1,
            "params": { "playerid" : playerid, "properties":["title", "album", "artist", "season", "episode", "showtitle", "tvshowid", "description"]}
            }
    res = json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))
    return res['result']['item']


################################################
# Aquire EPG Data for current playing channel
################################################
def get_broadcasts(chanid):
    query = {
            "jsonrpc": "2.0",
            "method": "PVR.GetBroadcasts",
            "id": 1,
            "params": { "channelid" : chanid }
            }
    res = json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))
    playerid = res['result']['broadcasts']
    for bc in playerid:
        query = {
                "id":1,
                "jsonrpc":"2.0",
                "params": { "broadcastid":bc['broadcastid'], 
                            "properties": [ "plot","title","plotoutline","starttime","endtime","runtime","progress","progresspercentage","genre","episodename","episodenum","episodepart","firstaired","hastimer","isactive","parentalrating","wasactive","thumbnail","rating","originaltitle","cast","director","writer","year","imdbnumber","hastimerrule","hasrecording","recording","isseries" ]
                          }, 
                "method":"PVR.GetBroadcastDetails"
                }
        res = json.loads(xbmc.executeJSONRPC(json.dumps(query, encoding='utf-8')))
        if res['result']['broadcastdetails']['isactive'] == True:
            playerid = res['result']['broadcastdetails']['isactive']
            return res['result']['broadcastdetails']



################################################
# Main funktion for getting EPG Data and set 
# Window Properties  
################################################
def set_current_infostrings():
    playerid = currentplayer()
    get_player_type(playerid)
    playerinfo = get_player_channel_id(playerid)
    channelid = playerinfo['id']
    channellabel = playerinfo['label']
    title = playerinfo['title']
    channeltype = playerinfo['type']

    res=get_broadcasts(channelid)
    writeLog("BroadCasts %s %s %s %s %s" % (playerinfo, channellabel,title,channelid,res),level=xbmc.LOGDEBUG)
    writeLog("BroadCastsInfo: [ Channel: %s Title: %s ChannelID: %s]" % (channellabel,title,channelid),level=xbmc.LOGNOTICE)
    try:
      genre=', '.join(res['genre'])
    except:
      genre=""
    channellogo=pvrchannelid2logo(channelid)
    starttime=res['starttime'].split(" ")[1]
    endtime=res['endtime'].split(" ")[1]
    startdate=res['starttime'].split(" ")[0]

    startstrftime = time.strptime(res['starttime'], "%Y-%m-%d %H:%M:%S")
    endstrftime = time.strptime(res['endtime'], "%Y-%m-%d %H:%M:%S")
    
    deltatime = (datetime.fromtimestamp(time.mktime(endstrftime))-datetime.fromtimestamp(time.mktime(startstrftime))) 

    WINDOW                  = xbmcgui.Window( 10000 )

    WINDOW.setProperty( "PVR.EPG.Title", res['title'] )
    if res['plot'] == '':
	WINDOW.setProperty( "PVR.EPG.Plot", res['plotoutline'] )
    else:
    	WINDOW.setProperty( "PVR.EPG.Plot", res['plot'] )
    WINDOW.setProperty( "PVR.EPG.Genre", genre )
    WINDOW.setProperty( "PVR.EPG.StartTime", starttime )
    WINDOW.setProperty( "PVR.EPG.StartDate", startdate )
    WINDOW.setProperty( "PVR.EPG.EndTime", endtime )
    WINDOW.setProperty( "PVR.EPG.Cast", res['cast'] )
    WINDOW.setProperty( "PVR.EPG.Director", res['director'] )
    WINDOW.setProperty( "PVR.EPG.Writer", res['writer'] )
    WINDOW.setProperty( "PVR.EPG.ChannelName", channellabel )
    WINDOW.setProperty( "PVR.EPG.ChannelLogo", channellogo )
    WINDOW.setProperty( "PVR.EPG.Duration", str(deltatime) )


################################################
#                   M A I N
################################################
set_current_infostrings()


