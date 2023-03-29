import urllib.request, urllib.parse, urllib.error
import ssl
import json
import smtplib
import email.message
import time
import random
import ftradeups, fprice, fmail
from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions
from steampy.models import Currency
from unicodedata import normalize
import re

horason = int(input('Horas ON: '))

starttime = time.time()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

buyskins = fprice.pricechecker(ftradeups.tradeups)

endtime = time.time()
tiempo = endtime - starttime

hours, rem = divmod(tiempo, 3600)
minutes, seconds = divmod(rem, 60)
print('---------------------------------------------------------------------')
print('Tiempo ON: ' + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

a = '™'
b = urllib.parse.quote(a)

skinscompradas = []
errores = []

print('=====================================================================')
while True:
    try:
        print('Conectando cuenta Steam...')
        steam_client = SteamClient('*****************************')
        steam_client.login('User', 'Password', 'data.txt')
        print('Conectada!')
        break
    except Exception as e:
        print('ERROR!')
        print(e)
        errores.append({'error':e})
        time.sleep(10)
        continue

nciclos = 0

while True:
    nciclos = nciclos+1
    print('=====================================================================')
    print('Ciclo: ' + str(nciclos))
    print('=====================================================================')

    for skin in buyskins:
        link = skin['link']
        maxfloat = skin['maxfloat']
        skinname = skin['name']
        maxprice = skin['maxprice']
        tradeup = skin['tradeup']
        if a in link:
            link = link.replace(a, b)
        url0 = 'https://steamcommunity.com/market/listings/730/' + link
        url = url0 + '/render/?query=&start=0&count=10&country=AR&language=spanish&currency=34'
        while True:
            try:
                print('Buscando ' + skinname + '...')
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                uh = urllib.request.urlopen(req, context=ctx)
                data = uh.read()
                info = json.loads(data)
                listingids = dict.keys(info['listinginfo'])
                for listingid in listingids:
                    link2 = info['listinginfo'][listingid]['asset']['market_actions'][0]['link']
                    assetid = info['listinginfo'][listingid]['asset']['id']
                    marketname = info['assets']['730']['2'][assetid]['market_name']
                    convertedfee = info['listinginfo'][listingid]['converted_fee']
                    convertedprice = info['listinginfo'][listingid]['converted_price']
                break
            except Exception as e:
                print('ERROR!')
                print(e)
                errores.append({'error':e, 'ciclo':nciclos, 'skin':skinname})
                print('Buscando nuevamente...')
                time.sleep(13)
                continue


        n = 0

        for listingid in listingids:
            n = n + 1
            link2 = info['listinginfo'][listingid]['asset']['market_actions'][0]['link']
            assetid = info['listinginfo'][listingid]['asset']['id']
            marketname = info['assets']['730']['2'][assetid]['market_name']
            url1 = 'https://api.csgofloat.com/?url=' + link2
            url2 = url1.replace('%listingid%', listingid)
            url3 = url2.replace('%assetid%', assetid)
            if a in url3:
                url3 = url3.replace(a, b)
            while True:
                try:
                    print('Buscando float ' + str(n) + '...')
                    req = urllib.request.Request(url3, headers={'User-Agent': 'Mozilla/5.0'})
                    uh2 = urllib.request.urlopen(req, context=ctx)
                    data2 = uh2.read()
                    info2 = json.loads(data2)
                    floatValue = info2['iteminfo']['floatvalue']
                    break
                except Exception as e:
                    print('ERROR!')
                    print(e)
                    errores.append({'error':e, 'ciclo':nciclos, 'skin':skinname})
                    print('Buscando nuevamente...')
                    time.sleep(1.30)
                    continue

            if floatValue < maxfloat:
                print('Se encontro un skin de bajo float!')

                convertedfee = info['listinginfo'][listingid]['converted_fee']
                convertedprice = info['listinginfo'][listingid]['converted_price']
                totalconvertedprice = convertedprice + convertedfee

                pricefloat = str(totalconvertedprice)
                pricefloat = pricefloat[:len(pricefloat)-2] + '.' + pricefloat[len(pricefloat)-2:]
                pricefloat = float(pricefloat)

                if pricefloat < maxprice:
                    print('El precio es correcto!')
                    is_session_alive = steam_client.is_session_alive()
                    print('Session: ' + str(is_session_alive))
                    if is_session_alive is False:
                        print('Reconectando...')
                        while True:
                            try:
                                print('Conectando cuenta Steam...')
                                steam_client = SteamClient('*****************************')
                                steam_client.login('User', 'Password', 'data.txt')
                                print('Conectada!')
                                break
                            except Exception as e:
                                print('ERROR!')
                                print(e)
                                errores.append({'error':e, 'ciclo':nciclos})
                                continue
                    try:
                        print('Realizando compra...')
                        if a in marketname:
                            marketname2 = marketname.replace(a, b)
                        response = steam_client.market.buy_item(marketname2, listingid, totalconvertedprice, convertedfee, GameOptions.CS, Currency.AR)
                        wallet_balance = response["wallet_info"]["wallet_balance"]

                        print('Skin Comprada!')

                        walletbalance = str(wallet_balance)
                        walletbalance = walletbalance[:len(walletbalance)-2] + '.' + walletbalance[len(walletbalance)-2:]
                        walletbalance = float(walletbalance)

                        skinscompradas.append({'name':marketname,  'float':floatValue, 'maxfloat':maxfloat, 'price':pricefloat, 'maxprice':maxprice, 'tradeup':tradeup, 'walletbalance':walletbalance})

                        if a in marketname:
                            marketname = marketname.replace(a, '')
                        marketname = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", normalize( "NFD", marketname), 0, re.I)
                        marketname = normalize( 'NFC', marketname)

                        mailto = 'email'
                        body = f'Se compro una skin:\n Link: {url0}\n Name: {marketname}\n Float: {floatValue}\n Maxfloat: {maxfloat}\n Price: {pricefloat}\n Maxprice: {maxprice}\n Pos: {n}\n Tradeup: {tradeup}\n\n Wallet Balance: {walletbalance}'
                        subject = "Compra realizada!"
                        fmail.send_email_with_data(mailto, subject, body)
                        print('Email enviado!')

                    except Exception as e:
                        print('ERROR!')
                        print(e)
                        errores.append({'error':e, 'ciclo':nciclos, 'skin':skinname})
                        continue

                else:
                    print('Precio elevado!')

            time.sleep(1.30)

        t = random.uniform(0, 2)
        t = round(t, 3)
        time.sleep(t)

    t = random.uniform(0, 3)
    t = round(t, 3)
    time.sleep(t)

    endtime = time.time()
    tiempo = endtime - starttime

    hours, rem = divmod(tiempo, 3600)
    minutes, seconds = divmod(rem, 60)
    print('---------------------------------------------------------------------')
    print('Tiempo ON: ' + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))

    is_session_alive = steam_client.is_session_alive()
    print('Session: ' + str(is_session_alive))

    if tiempo > (60.00*60*horason):
        break

steam_client.logout()

print('=====================================================================')
print('Errores:')
print('=====================================================================')

for error in errores:
    print(error)
    print('---------------------------------------------------------------------')


print('=====================================================================')
print('Skins Compradas:')
print('=====================================================================')

for skincomprada in skinscompradas:
    print(skincomprada)
    print('---------------------------------------------------------------------')
