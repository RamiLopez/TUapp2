import urllib.request, urllib.parse, urllib.error
import ssl
import json
import re
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def pricechecker(tradeups):
    cajasagregar = {}
    for tradeup in tradeups:
        ncajaagregada = 0
        tnum = list(tradeup.keys())
        cajasagregar[tnum[0]] = []
        print('Configurando tradeup ' + str(tnum[0]) + ':')
        totalcajas = int(input('Cuantas cajas? '))
        while True:
            if totalcajas == 0:
                cajasagregar[tnum[0]].append(0)
            if ncajaagregada >= totalcajas:
                break
            cajaagregada = int(input('N de caja: '))
            cajasagregar[tnum[0]].append(cajaagregada)
            ncajaagregada = ncajaagregada + 1

    buyskins = []
    a = '™'
    b = urllib.parse.quote(a)
    archivo = open('datos.txt', 'w')

    for tradeup in tradeups:
        tnum = list(tradeup.keys())
        if 0 in cajasagregar[tnum[0]]:
            continue
        print('=====================================================================')
        print('Buscando tradeup ' + tnum[0] + '...')
        print('=====================================================================')
        cajas = tradeup[tnum[0]][0]['inputs']
        outputs = tradeup[tnum[0]][1]['outputs']
        porcmax = tradeup[tnum[0]][2]['porcmax']
        lototal =  0
        pcaja1 = []
        pcaja2 = []
        pcaja3 = []
        ncajas = 0

        print('Buscando outputs...')
        archivo.write('Tradeup ' + tnum[0] + ':\n')
        archivo.write('\n')
        archivo.write(' Outputs:\n')

        for output in outputs:
            outputname = output['name']
            print('Buscando precio ' + outputname + '...')
            archivo.write('  ' + outputname + ':\n')
            url = 'https://steamcommunity.com/market/priceoverview/?currency=34&appid=730&market_hash_name=' + output['link']
            if a in url:
                url = url.replace(a, b)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            uh = urllib.request.urlopen(req, context=ctx)
            data = uh.read()
            info = json.loads(data)
            if 'lowest_price' not in info:
                while True:
                    print('No se encontro!')
                    time.sleep(9)
                    print('Buscando denuevo...')
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    uh = urllib.request.urlopen(req, context=ctx)
                    data = uh.read()
                    info = json.loads(data)
                    if 'lowest_price' in info:
                        break

            lpo = re.findall(r'[0-9,.]+' ,info['lowest_price'])
            lo0 = float(lpo[0].replace('.', '').replace(',', '.'))
            lo1 = lo0*0.86956
            lo = lo1*output['prob']
            lototal = lototal+lo

            prob = output['prob']

            print('Encontrado!')
            archivo.write('   Low Price: ' + str('{:.2f}'.format(lo0)) + '  --  ' + 'Cartera Steam: ' + str('{:.2f}'.format(lo1)) + '\n')
            archivo.write('   Probabilidad: ' + str('{:.2f}'.format(prob)) + '  --  ' + 'Aporta por tradeup: ' + str('{:.2f}'.format(lo)) + '\n')

            time.sleep(9)

        archivo.write('\n')
        archivo.write('  Output total por tradeup(cartera steam): ' + str('{:.2f}'.format(lototal)) + '\n')
        archivo.write('\n')
        archivo.write(' Inputs:\n')

        for caja in cajas:
            ncajas = ncajas + 1
            cnum = list(caja.keys())
            print('---------------------------------------------------------------------')
            print('Buscando inputs ' + cnum[0] + '...')
            archivo.write('  ' + cnum[0] + ':\n')
            skins = caja[cnum[0]][0]['skins']
            cantidad = caja[cnum[0]][0]['cantidad']
            maxfloat = caja[cnum[0]][0]['maxfloat']

            for skin in skins:
                name = skin['name']
                print('Buscando precio ' + name + '...')
                archivo.write('   ' + name + ':\n')
                link = skin['link']
                url = 'https://steamcommunity.com/market/priceoverview/?currency=34&appid=730&market_hash_name=' + link
                if a in url:
                    url = url.replace(a, b)
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                uh = urllib.request.urlopen(req, context=ctx)
                data = uh.read()
                info = json.loads(data)
                if 'lowest_price' not in info:
                    while True:
                        print('No se encontro!')
                        time.sleep(9)
                        print('Buscando denuevo...')
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        uh = urllib.request.urlopen(req, context=ctx)
                        data = uh.read()
                        info = json.loads(data)
                        if 'lowest_price' in info:
                            break

                lpi = re.findall(r'[0-9,.]+' ,info['lowest_price'])
                li0 = float(lpi[0].replace('.', '').replace(',', '.'))
                li = li0*cantidad

                if ncajas == 1:
                    pcaja1.append(li)
                if ncajas == 2:
                    pcaja2.append(li)
                if ncajas == 3:
                    pcaja3.append(li)

                print('Encontrado!')
                archivo.write('    Low Price: ' + str('{:.2f}'.format(li0)) + '\n')
                archivo.write('    Cantidad: ' + str(cantidad) + '  --  ' + 'Precio total: ' + str('{:.2f}'.format(li)) + '\n')

                time.sleep(9)

        print('---------------------------------------------------------------------')
        print('Haciendo calculos...')

        sortedpcaja1 = sorted(pcaja1)
        sortedpcaja2 = sorted(pcaja2)
        sortedpcaja3 = sorted(pcaja3)

        if ncajas == 1:
            litotal = sortedpcaja1[0]
        if ncajas == 2:
            litotal = sortedpcaja1[0] + sortedpcaja2[0]
        if ncajas == 3:
            litotal = sortedpcaja1[0] + sortedpcaja2[0] + sortedpcaja3[0]

        lprofit = lototal - litotal
        lporcentaje = (100/litotal)*lototal

        archivo.write('\n')
        archivo.write('   Costo input total(low): ' + str('{:.2f}'.format(litotal)) + '\n')
        archivo.write('   Profit: ' + str('{:.2f}'.format(lprofit)) + '  --  ' + 'Porcentaje: ' + str('{:.2f}'.format(lporcentaje)) + '\n')

        if lporcentaje > porcmax:
            print('Tradeup rentable!')
            lilimit = 100/((porcmax-1.00)/lototal)
            multilimit = lilimit/litotal
            limax = 100/((porcmax-1.50)/lototal)
            multimax = limax/litotal
            archivo.write('\n')
            archivo.write('----------------------------------------------------------------------\n')
            archivo.write('\n')
            archivo.write(' Tradeup rentable:\n')

            if ncajas >= 1 and 1 in cajasagregar[tnum[0]]:
                print('---------------------------------------------------------------------')
                print('Agregando skins caja1...')
                archivo.write('  Caja1:\n')
                nskin = 0
                skins = tradeup[tnum[0]][0]['inputs'][0]['caja1'][0]['skins']
                cantidad = tradeup[tnum[0]][0]['inputs'][0]['caja1'][0]['cantidad']
                maxfloat = tradeup[tnum[0]][0]['inputs'][0]['caja1'][0]['maxfloat']
                maxprice = (sortedpcaja1[0]/cantidad)*multimax
                archivo.write('   Maxprice: ' + str('{:.2f}'.format(maxprice)) + '\n')
                archivo.write('\n')
                for price in pcaja1:
                    if price < (sortedpcaja1[0]*multilimit):
                        name = skins[nskin]['name']
                        print('Agregando ' + name + '...')
                        link = skins[nskin]['link']
                        buyskins.append({'name':name, 'link':link, 'maxfloat':maxfloat, 'maxprice':maxprice, 'tradeup':tnum[0]})
                        print('Listo!')
                        preciototallimite = (sortedpcaja1[0]*multilimit)
                        precioind = (price/cantidad)
                        precioindlim = (sortedpcaja1[0]/cantidad)*multilimit
                        archivo.write('   ' + name + ':\n')
                        archivo.write('    Precio individual: ' + str('{:.2f}'.format(precioind)) + '  --  ' + 'Precio ind limite: ' + str('{:.2f}'.format(precioindlim)) + '\n')
                        archivo.write('    Precio total: ' + str('{:.2f}'.format(price)) + '  --  ' + 'Precio total limite: ' + str('{:.2f}'.format(preciototallimite)) + '\n')
                        archivo.write('    Agregada!\n')

                    else:
                        name = skins[nskin]['name']
                        print('No se ha agregado ' + name + '...')
                        print('Precio alto!')
                        preciototallimite = (sortedpcaja1[0]*multilimit)
                        precioind = (price/cantidad)
                        precioindlim = (sortedpcaja1[0]/cantidad)*multilimit
                        archivo.write('   ' + name + ':\n')
                        archivo.write('    Precio individual: ' + str('{:.2f}'.format(precioind)) + '  --  ' + 'Precio ind limite: ' + str('{:.2f}'.format(precioindlim)) + '\n')
                        archivo.write('    Precio total: ' + str('{:.2f}'.format(price)) + '  --  ' + 'Precio total limite: ' + str('{:.2f}'.format(preciototallimite)) + '\n')
                        archivo.write('    No se agrego!\n')

                    nskin = nskin + 1

            if 1 not in cajasagregar[tnum[0]]:
                print('Usted selecciono no agregar las skins de caja1!')

            if ncajas >= 2 and 2 in cajasagregar[tnum[0]]:
                print('---------------------------------------------------------------------')
                print('Agregando skins caja2...')
                archivo.write('\n')
                archivo.write('  Caja2:\n')
                nskin = 0
                skins = tradeup[tnum[0]][0]['inputs'][1]['caja2'][0]['skins']
                cantidad = tradeup[tnum[0]][0]['inputs'][1]['caja2'][0]['cantidad']
                maxfloat = tradeup[tnum[0]][0]['inputs'][1]['caja2'][0]['maxfloat']
                maxprice = (sortedpcaja2[0]/cantidad)*multimax
                archivo.write('   Maxprice: ' + str('{:.2f}'.format(maxprice)) + '\n')
                archivo.write('\n')
                for price in pcaja2:
                    if price < (sortedpcaja2[0]*multilimit):
                        name = skins[nskin]['name']
                        print('Agregando ' + name + '...')
                        link = skins[nskin]['link']
                        buyskins.append({'name':name, 'link':link, 'maxfloat':maxfloat, 'maxprice':maxprice, 'tradeup':tnum[0]})
                        print('Listo!')
                        preciototallimite = (sortedpcaja2[0]*multilimit)
                        precioind = (price/cantidad)
                        precioindlim = (sortedpcaja2[0]/cantidad)*multilimit
                        archivo.write('   ' + name + ':\n')
                        archivo.write('    Precio individual: ' + str('{:.2f}'.format(precioind)) + '  --  ' + 'Precio ind limite: ' + str('{:.2f}'.format(precioindlim)) + '\n')
                        archivo.write('    Precio total: ' + str('{:.2f}'.format(price)) + '  --  ' + 'Precio total limite: ' + str('{:.2f}'.format(preciototallimite)) + '\n')
                        archivo.write('    Agregada!\n')

                    else:
                        name = skins[nskin]['name']
                        print('No se ha agregado ' + name + '...')
                        print('Precio alto!')
                        preciototallimite = (sortedpcaja2[0]*multilimit)
                        precioind = (price/cantidad)
                        precioindlim = (sortedpcaja2[0]/cantidad)*multilimit
                        archivo.write('   ' + name + ':\n')
                        archivo.write('    Precio individual: ' + str('{:.2f}'.format(precioind)) + '  --  ' + 'Precio ind limite: ' + str('{:.2f}'.format(precioindlim)) + '\n')
                        archivo.write('    Precio total: ' + str('{:.2f}'.format(price)) + '  --  ' + 'Precio total limite: ' + str('{:.2f}'.format(preciototallimite)) + '\n')
                        archivo.write('    No se agrego!\n')

                    nskin = nskin + 1

            if 2 not in cajasagregar[tnum[0]]:
                print('Usted selecciono no agregar las skins de caja2!')

            if ncajas >= 3 and 3 in cajasagregar[tnum[0]]:
                print('---------------------------------------------------------------------')
                print('Agregando skins caja3...')
                archivo.write('\n')
                archivo.write('  Caja3:\n')
                nskin = 0
                skins = tradeup[tnum[0]][0]['inputs'][2]['caja3'][0]['skins']
                cantidad = tradeup[tnum[0]][0]['inputs'][2]['caja3'][0]['cantidad']
                maxfloat = tradeup[tnum[0]][0]['inputs'][2]['caja3'][0]['maxfloat']
                maxprice = (sortedpcaja3[0]/cantidad)*multimax
                archivo.write('   Maxprice: ' + str('{:.2f}'.format(maxprice)) + '\n')
                archivo.write('\n')
                for price in pcaja3:
                    if price < (sortedpcaja3[0]*multilimit):
                        name = skins[nskin]['name']
                        print('Agregando ' + name + '...')
                        link = skins[nskin]['link']
                        buyskins.append({'name':name, 'link':link, 'maxfloat':maxfloat, 'maxprice':maxprice, 'tradeup':tnum[0]})
                        print('Listo!')
                        preciototallimite = (sortedpcaja3[0]*multilimit)
                        precioind = (price/cantidad)
                        precioindlim = (sortedpcaja3[0]/cantidad)*multilimit
                        archivo.write('   ' + name + ':\n')
                        archivo.write('    Precio individual: ' + str('{:.2f}'.format(precioind)) + '  --  ' + 'Precio ind limite: ' + str('{:.2f}'.format(precioindlim)) + '\n')
                        archivo.write('    Precio total: ' + str('{:.2f}'.format(price)) + '  --  ' + 'Precio total limite: ' + str('{:.2f}'.format(preciototallimite)) + '\n')
                        archivo.write('    Agregada!\n')

                    else:
                        name = skins[nskin]['name']
                        print('No se ha agregado ' + name + '...')
                        print('Precio alto!')
                        preciototallimite = (sortedpcaja3[0]*multilimit)
                        precioind = (price/cantidad)
                        precioindlim = (sortedpcaja3[0]/cantidad)*multilimit
                        archivo.write('   ' + name + ':\n')
                        archivo.write('    Precio individual: ' + str('{:.2f}'.format(precioind)) + '  --  ' + 'Precio ind limite: ' + str('{:.2f}'.format(precioindlim)) + '\n')
                        archivo.write('    Precio total: ' + str('{:.2f}'.format(price)) + '  --  ' + 'Precio total limite: ' + str('{:.2f}'.format(preciototallimite)) + '\n')
                        archivo.write('    No se agrego!\n')

                    nskin = nskin + 1

        print('---------------------------------------------------------------------')
        print('Tradeup ' + tnum[0] + ' finalizado!')
        archivo.write('\n')
        archivo.write('\n')
        archivo.write('========================================================================================================================\n')
        archivo.write('\n')
        archivo.write('\n')


    archivo.write('========================================================================================================================\n')
    archivo.write('LISTA BUYSKINS:\n')
    for buyskin in buyskins:
        archivo.write(json.dumps(buyskin))
        archivo.write('\n')

    archivo.close()

    return buyskins
