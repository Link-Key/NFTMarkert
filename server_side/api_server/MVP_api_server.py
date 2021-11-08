# Lee
import configparser
import json
from datetime import datetime

import aiohttp_cors
import asyncpg
from aiohttp import web
# sfrom asycpg.exceptions import UndefinedColumnError
from web3.middleware import geth_poa_middleware

routes = web.RouteTableDef()
config = configparser.ConfigParser()
config.read('conf/config.ini')
import random
from web3 import Web3
import requests_async as requests

import re

email = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
addr = '^0x[a-fA-F0-9]{40}$'
name = '[a-fA-F0-9]'


def checkEmail(param):
    if (re.search(email, param)):
        return True
    else:
        return False


def checkAddr(param):
    if (re.search(addr, param)):
        return True
    else:
        return False


def checkString(param):
    if (re.search(name, param)):
        return True
    else:
        return False


def checkNumber(param):
    if param and param.isdigit():
        return True
    else:
        return False


sellerNames = {}

mode = 'ONLINE'

paging = config[mode]['paging']
web3 = Web3(Web3.WebsocketProvider(config[mode]['node']))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

print(config[mode]['node'])

addr_market = config[mode]['market']
addr_erc721 = config[mode]['erc721']
_abi_path = config[mode]['abi']
_erc_abi_path = config[mode]['erc_abi']

namedb = []


def get_name(filename):
    selected = random.random() * 90
    name = []
    with open(filename) as name_file:
        for line in name_file:
            name.append(line.split())
    return name


namedb = get_name("./assets/userName.db")

with open(_abi_path) as f:
    nft_abi = json.load(f)

with open(_erc_abi_path) as f:
    nft_erc_abi = json.load(f)

contract = web3.eth.contract(address=addr_market, abi=nft_abi)
contract_erc721 = web3.eth.contract(address=addr_erc721, abi=nft_erc_abi)


## DB Stuffs
async def fetch(query, *args):
    async with asyncpg.create_pool(config[mode]['db'], command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.fetch(query, *args)
        finally:
            await pool.close()


async def fetchrow(query, *args):
    async with asyncpg.create_pool(config[mode]['db'], command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.fetchrow(query, *args)
        finally:
            await pool.close()


async def fetchval(query, *args):
    async with asyncpg.create_pool(config[mode]['db'], command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.fetchval(query, *args)
        finally:
            await pool.close()


async def execute(query, *args):
    async with asyncpg.create_pool(config[mode]['db'], command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.execute(query, *args)
        finally:
            await pool.close()


async def checkStatus(saleType):
    if saleType == 0:
        return "OPEN"
    if saleType == 1:
        return "SOLD"
    if saleType == 2:
        return "CANCELLED"


import datetime


# date = datetime.datetime.now()
@routes.post('/post')
async def item_handler(request):
    global web3
    if request.body_exists:
        # read params
        data = await request.json()
        method = data['method']
        param = data['param']
        print(param)
        if method == "RegisterNFT":
            rdata = {}

            res_data = {}
            if param['uri'] is not None:
                res = await requests.get(param['uri'])
                res_data = res.json()
            if res_data['name'] is None:
                res_data['name'] = "No title"
            if res_data['image'] is not None:
                if res_data['image'].startswith('ipfs://ipfs/'):
                    res_data['image'] = 'https://ipfs.infura.io/ipfs/' + res_data['image'][12:]
            else:
                res_data['image'] = ""
            if res_data['description'] is None:
                res_data['description'] = ""

            try:
                date = datetime.datetime.now()

                # validate params.
                print(param['owner'])
                print(param['name'])
                print(param['address'])
                print(param['id'])
                print(param['title'])
                print(param['category'])
                # print(param['collection'])
                print(param['uri'])
                print(param['description'])
                try:
                    collectionid = param['collection']
                except Exception as inst:
                    collectionid = ''

                symbol = contract_erc721.functions.symbol().call()

                CONN = await asyncpg.connect(config[mode]['db'])
                await CONN.execute("""
					INSERT INTO 
					nftinfo(owner, nftName, nftAddress, nftId, title, category, uri, description, regDate, image, nftsymbol, collectionid) 
					VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
				""", param['owner'], param['name'], param['address'],
                     param['id'], param['title'], param['category'],
                   param['uri'], param['description'], date, res_data['image'], symbol, collectionid)
                await CONN.close()
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                rdata['status'] = 500
                # await CONN.close()
                return web.json_response(rdata)
            rdata['status'] = 200
            return web.json_response(rdata)
        elif method == "UpdateNFT":
            rdata = {}
            try:
                date = datetime.datetime.now()
                print(param['name'])
                print(param['address'])
                print(param['id'])
                print(param['title'])
                print(param['category'])
                print(param['uri'])
                print(param['description'])
                try:
                    collectionid = param['collection']
                except Exception as inst:
                    collectionid = ''
                CONN = await asyncpg.connect(config[mode]['db'])
                await CONN.execute("""
					UPDATE nftinfo SET nftName=$2, nftId=$3, title=$4,  category=$5, uri=$6, description=$7, regDate=$8, collectionid=$9 where nftAddress=$1
				""", param['address'], param['name'], param['id'], param['title'], param['category'], param['uri'],
                                   param['description'], date, collectionid)
                await CONN.close()
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                # await CONN.close()
                rdata['status'] = 500
                return web.json_response(rdata)
            rdata['status'] = 200
            return web.json_response(rdata)
        else:
            rdata.append("{status:'Bad request'}")
            rdata = web.json_response(rdata)
            return rdata


@routes.post('/post')
async def banner_handler(request):
    global rfeat
    print("banner_handler")
    if request.body_exists:
        # read params
        rdata = {}
        data = await request.json()
        method = data['method']
        param = data['param']
        if method == "ListBanner":
            rdata = {}

            CONN = await asyncpg.connect(config[mode]['db'])
            ret  = await CONN.fetch("select * from banner order by id desc")

            ssuper = []
            for d in ret:
                subrdata = {}
                subrdata['uri'] = d['uri']
                subrdata['id'] = d['id']
                subrdata['type'] = d['type']
                subrdata['adddate'] = str(d["adddate"])
                ssuper.append(subrdata)
            await CONN.close()
            rdata['status'] = 200
            rdata['data'] = ssuper
            return web.json_response(rdata)
        if method == "Add":
            rdata = {}

            owner = web3.toChecksumAddress(param['owner'])

            if await check_admin(param['owner']) != 1:
                rdata['status'] = 500
                rdata['msg'] = 'No permission'
                return web.json_response(rdata)

            CONN = await asyncpg.connect(config[mode]['db'])

            date = datetime.datetime.now()
            await CONN.execute("""
                insert into banner(uri, adddate, type) VALUES($1, $2, $3)
               """, param['uri'], date, "left")
            await CONN.close()

            rdata['status'] = 200
            rdata['msg'] = ' Add OK!'
            return web.json_response(rdata)
        if method == "Update":
            rdata = {}

            owner = web3.toChecksumAddress(param['owner'])

            if await check_admin(param['owner']) != 1:
                rdata['status'] = 500
                rdata['msg'] = 'No permission'
                return web.json_response(rdata)

            CONN = await asyncpg.connect(config[mode]['db'])

            await CONN.execute("""
                UPDATE banner SET type=$2 WHERE id=$1
               """, param['id'], param['type'])
            await CONN.close()

            rdata['status'] = 200
            rdata['msg'] = ' Update OK!'
            return web.json_response(rdata)
        if method == "Delete":
            rdata = {}

            owner = web3.toChecksumAddress(param['owner'])

            if await check_admin(param['owner']) != 1:
                rdata['status'] = 500
                rdata['msg'] = 'No permission'
                return web.json_response(rdata)

            CONN = await asyncpg.connect(config[mode]['db'])

            await CONN.execute("""
                DELETE FROM banner WHERE id=$1
               """, param['id'])
            await CONN.close()

            rdata['status'] = 200
            rdata['msg'] = ' Delete OK!'
            return web.json_response(rdata)


@routes.post('/post')
async def adminlist_handler(request):
    global rfeat
    print("adminlist_handler")
    if request.body_exists:
        # read params
        rdata = {}
        data = await request.json()
        method = data['method']
        param = data['param']
        if method == "UpdateIsAdmin":
            rdata = {}

            owner = web3.toChecksumAddress(param['owner'])

            if await check_admin(param['owner']) != 1:
                rdata['status'] = 500
                rdata['msg'] = 'No permission'
                return web.json_response(rdata)

            CONN = await asyncpg.connect(config[mode]['db'])

            await CONN.execute("""
                UPDATE userinfo SET isadmin = $2 where account =$1
               """, param['account'], param['isadmin'])
            await CONN.close()

            rdata['status'] = 200
            rdata['msg'] = ' Update OK!'
            return web.json_response(rdata)
        if method == "GetAdminList":
            rdata = {}

            if await check_admin(param['owner']) != 1:
                rdata['status'] = 500
                rdata['msg'] = 'No permission'
                return web.json_response(rdata)

            CONN = await asyncpg.connect(config[mode]['db'])
            ret  = await CONN.fetch("select * from userinfo order by regdate desc")

            ssuper = []
            for d in ret:
                subrdata = {}
                subrdata['registered'] = 1
                subrdata['account'] = d['account']
                subrdata['email'] = d['email']
                subrdata['name'] = d['name']
                subrdata['isadmin'] = d['isadmin']
                subrdata['introduction'] = d['introduction']
                subrdata['date'] = str(d["regdate"])
                ssuper.append(subrdata)
            await CONN.close()
            rdata['status'] = 200
            rdata['data'] = ssuper
            return web.json_response(rdata)


@routes.post('/post')
async def collection_handler(request):
    global rfeat
    print("collection_handler")
    if request.body_exists:
        # read params
        rdata = {}
        data = await request.json()
        method = data['method']
        param = data['param']
        if method == "UpdateCollection":
            rdata = {}

            owner = web3.toChecksumAddress(param['owner'])

            if await check_admin(param['owner']) != 1:
                rdata['status'] = 500
                rdata['msg'] = 'No permission'
                return web.json_response(rdata)

            CONN = await asyncpg.connect(config[mode]['db'])

            await CONN.execute("""
                UPDATE collectioninfo SET status = $2 where id =$1
               """, param['id'], param['status'])
            await CONN.close()

            rdata['status'] = 200
            rdata['msg'] = ' Update OK!'
            return web.json_response(rdata)
        if method == "GetCollectionByShortUri":
            rdata = {}

            CONN = await asyncpg.connect(config[mode]['db'])
            ret = await CONN.fetchrow('''
                   select * from collectioninfo where shorturi = $1
            ''', param['shortUri'])
            rfeat = {}
            if ret is not None:
                if ret['status'] == 1:
                    rdata['status'] = 200
                    rfeat = {'id': ret['id'], 'owner': ret['owner'], 'title': ret['title'],
                         'description': ret['description'], 'status': ret['status'], 'uri': ret['uri'],
                         'shorturi': ret['shorturi']}
                else:
                    rdata['status'] = 500
            await CONN.close()
            rdata['data'] = rfeat
            return web.json_response(rdata)
        if method == "GetCollectionListAdmin":
            rdata = {}

            if await check_admin(param['owner']) != 1:
                rdata['status'] = 500
                rdata['msg'] = 'No permission'
                return web.json_response(rdata)

            CONN = await asyncpg.connect(config[mode]['db'])
            ret = await CONN.fetch("select * from collectioninfo order by createdate DESC,id desc")
            ssuper = []
            for i in ret:
                rfeat = {}
                rfeat['id'] = i['id']
                rfeat['owner'] = i['owner']
                rfeat['title'] = i['title']
                rfeat['description'] = i['description']
                rfeat['status'] = i['status']
                rfeat['uri'] = i['uri']
                rfeat['shorturi'] = i['shorturi']
                ssuper.append(rfeat)
            await CONN.close()
            rdata['status'] = 200
            rdata['data'] = ssuper
            return web.json_response(rdata)
        if method == "GetCollectionListGuest":
            rdata = {}

            CONN = await asyncpg.connect(config[mode]['db'])
            ret = await CONN.fetch("select * from collectioninfo where status = 1 order by createdate DESC,id asc")
            ssuper = []
            for i in ret:
                rfeat = {}
                rfeat['id'] = i['id']
                rfeat['owner'] = i['owner']
                rfeat['title'] = i['title']
                rfeat['description'] = i['description']
                rfeat['status'] = i['status']
                rfeat['uri'] = i['uri']
                rfeat['shorturi'] = i['shorturi']
                ssuper.append(rfeat)
            await CONN.close()
            rdata['status'] = 200
            rdata['data'] = ssuper
            return web.json_response(rdata)
        if method == "GetCollectionList":
            rdata = {}

            CONN = await asyncpg.connect(config[mode]['db'])
            owner = web3.toChecksumAddress(param['owner'])
            ret = await CONN.fetch('''
                   select * from collectioninfo where owner = $1 order by createdate DESC,id asc
            ''', owner)
            ssuper = []
            for i in ret:
                rfeat = {}
                rfeat['id'] = i['id']
                rfeat['owner'] = i['owner']
                rfeat['title'] = i['title']
                rfeat['description'] = i['description']
                rfeat['status'] = i['status']
                rfeat['uri'] = i['uri']
                rfeat['shorturi'] = i['shorturi']
                ssuper.append(rfeat)
            await CONN.close()
            rdata['status'] = 200
            rdata['data'] = ssuper
            return web.json_response(rdata)
        if method == "ShortUriCheck":
            rdata = {}
            if await check_short_uri(param['uri']) != -1:
                rdata['status'] = 1001
                rdata['msg'] = 'It has been registered by others'
                return web.json_response(rdata)
            else:
                rdata['status'] = 200
                return web.json_response(rdata)
        if method == "RegisterCollection":
            try:
                date = datetime.datetime.now()
                owner = web3.toChecksumAddress(param['owner'])
                CONN = await asyncpg.connect(config[mode]['db'])
                if await check_short_uri(param['shorturi']) != -1:
                    rdata['status'] = 1001
                    await CONN.close()
                    return web.json_response(rdata)
                else:
                    await CONN.execute("""
                            INSERT INTO collectioninfo(owner, title, description, createdate, uri, status, shorturi) 
                            VALUES($1, $2, $3, $4, $5, $6, $7)
                        """, owner, param['title'], param['description'], date, param['uri'], 0, param['shorturi'])
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)
            rdata['status'] = 200
            return web.json_response(rdata)


async def check_short_uri(shorturi):
    try:
        CONN = await asyncpg.connect(config[mode]['db'])
        qry = "select * from collectioninfo where shorturi = '"+shorturi+"'"
        ret = await CONN.fetchrow(qry)
        # print(ret)
        if ret is not None:
            if ret['id'] is not None:
                return ret
            else:
                return -1
        else:
            return -1
    except Exception as inst:
        return -1


async def check_admin(addr):
    try:
        CONN = await asyncpg.connect(config[mode]['db'])
        qry = "select * from userinfo where account = '" + addr + "'"
        ret = await CONN.fetchrow(qry)
        print(ret)
        if ret is not None:
            if ret['isadmin'] == 1:
                return 1
            else:
                return -1
        else:
            return -1
    except Exception as inst:
        return -1


@routes.post('/post')
async def account_handler(request):
    print("account_handler")
    global web3
    if request.body_exists:
        # read params
        rdata = {}
        data = await request.json()
        method = data['method']
        param = data['param']
        print(param)
        if method == "RegisterUser":
            try:
                date = datetime.datetime.now()
                addr = web3.toChecksumAddress(param['account'])
                CONN = await asyncpg.connect(config[mode]['db'])
                await CONN.execute("""
					INSERT INTO userinfo(account, name, email, signature, regdate, introduction, isadmin) VALUES($1, $2, $3, $4, $5, $6, $7) ON CONFLICT (account) DO NOTHING
				""", addr, param['name'], param['email'], param['signature'], date, param['introduction'], 0)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)
            rdata['status'] = 200
            return web.json_response(rdata)
        if method == "RegisterNFT":
            try:
                param_addr = str(param['address'])
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')
                CONN = await asyncpg.connect(config[mode]['db'])
                val = await CONN.fetchval('''
					select confirmed from NFT_REGISTRATION where nftAddr = $1
				''', param_addr)

                if (val == None):
                    rdata['ret'] = 0
                    rdata['status'] = 'not listed.'
                    await CONN.execute("""
						INSERT into NFT_REGISTRATION(nftaddr,type,confirmed,flag,category,description) values($1, 999, 0, 0, $2, $3) ON CONFLICT (nftaddr) DO NOTHING
					""", param['address'], param['category'], param['description'])
                if (val == 0):
                    rdata['ret'] = 1
                    rdata['status'] = 'under confirmed.'
                if (val == 1):
                    rdata['ret'] = 2
                    rdata['status'] = 'listed'
                await CONN.close()
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                rdata = {}
                await CONN.close()
                rdata['status'] = 500
                return web.json_response(rdata)
            return web.json_response(rdata)
        elif method == "UpdateUserInfo":
            try:
                date = datetime.datetime.now()
                CONN = await asyncpg.connect(config[mode]['db'])
                addr = web3.toChecksumAddress(param['account'])
                await CONN.execute("""
					UPDATE userinfo SET name=$2, email=$3, updatedate=$4,  signature=$5, introduction=$6 where account=$1
				""", addr, param['name'], param['email'], date, param['signature'], param['introduction'])
                await CONN.close()
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata['status'] = 500
                return web.json_response(rdata)
            rdata['status'] = 200
            return web.json_response(rdata)
        elif method == "GetUserInfo":
            try:
                date = datetime.datetime.now()
                CONN = await asyncpg.connect(config[mode]['db'])
                param_addr = str(web3.toChecksumAddress(param['account']))
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')
                # qry = "select * from userinfo where account ='"  + param_addr + "'"
                # d = await CONN.fetchrow(qry)
                d = await CONN.fetchrow('''
					select * from userinfo where account = $1
				''', param_addr)
                if (d != None):
                    subrdata = {}
                    subrdata['registered'] = 1
                    subrdata['account'] = d['account']
                    subrdata['email'] = d['email']
                    subrdata['name'] = d['name']
                    subrdata['isadmin'] = d['isadmin']
                    subrdata['introduction'] = d['introduction']
                    subrdata['date'] = str(d["regdate"])
                    await CONN.execute('''
						UPDATE userinfo SET logindate = $1 where account = $2
					''', date, param_addr)
                    await CONN.close()
                    return web.json_response(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata['status'] = 500
                return web.json_response(rdata)
            subrdata = {}
            subrdata['registered'] = 0
            subrdata['account'] = str(param['account'])
            subrdata['email'] = ""
            subrdata['name'] = ""
            subrdata['introduction'] = ""
            subrdata['date'] = ""
            return web.json_response(subrdata)
        else:
            rdata['status'] = 500
            return web.json_response(rdata)


async def getUserName(addr):
    val = int(addr, 0)
    return namedb[val % 5494][0]


@routes.post('/post')
async def auction_handler(request):
    global web3
    if request.body_exists:
        data = await request.json()
        method = data['method']
        param = data['param']
        if method == "GetHistoryByAuctionID":
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                param_id = str(param['id'])
                if checkNumber(param_id) == False:
                    raise Exception('param', 'invalid param')
                result = await CONN.fetch('''
					select * from auctionlog where auctionid = $1 and (eventtype='AuctionCreated' or eventtype ='AuctionClosed' or eventtype='BidActivated') order by id DESC limit $2
				''', int(param_id), paging)

                rdata = []
                (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid,
                 bidCount) = contract.functions.getAuction(param['id']).call()
                bidder = None
                for d in result:
                    subrdata = {}
                    if (d["eventtype"] == 'AuctionCreated'):
                        bidder = 0x0000000000000000000000000000000000000000
                        subrdata['event'] = 'OPEN'
                        subrdata['price'] = startingBid
                        subrdata['by'] = seller
                        subrdata['to'] = 0x0000000000000000000000000000000000000000
                        subrdata['date'] = d["timestamp"]
                        subrdata['tx'] = d["txhash"]
                        rdata.append(subrdata)
                    elif (d["eventtype"] == 'BidActivated'):
                        (_, bidder, _amount, _, _) = contract.functions.getBid(d['auctionid'], d['bidid']).call()
                        subrdata['event'] = 'BID'
                        subrdata['price'] = _amount
                        subrdata['by'] = seller
                        subrdata['to'] = bidder
                        subrdata['tx'] = d["txhash"]
                        subrdata['date'] = d["timestamp"]
                        rdata.append(subrdata)
                    elif (d["eventtype"] == 'AuctionClosed'):
                        subrdata['event'] = await checkStatus(d['auctionstate'])
                        subrdata['price'] = highBid[2]
                        subrdata['by'] = seller
                        subrdata['to'] = highBid[1]
                        subrdata['tx'] = d["txhash"]
                        subrdata['date'] = d["timestamp"]
                        rdata.append(subrdata)
                await CONN.close()
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                edata = {}
                edata['status'] = 500
                return web.json_response(edata)
            return web.json_response(rdata)

        elif method == "GetBidHistoryByAuctionID":
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                param_id = str(param['id'])
                if checkNumber(param_id) == False:
                    raise Exception('param', 'invalid param')

                result = await CONN.fetch('''
					select distinct a.seller, a.txhash, a.amount, a.id, a.timestamp from auctionlog a left join auctionlog b on a.auctionid=b.auctionid where a.auctionid=$1 and (a.eventtype='BidActivated' and b.eventtype = 'BidCreated') order by a.id desc
				''', int(param_id))

                bids = await CONN.fetch('''
					select bidder from auctionlog where auctionid = $1 and eventtype = 'BidCreated'
				''', int(param_id))

                rdata = []
                i = 0
                for d in result:
                    subrdata = {}
                    subrdata['event'] = 'BID'
                    subrdata['price'] = format(float(d['amount']), '.0f')
                    subrdata['by'] = bids[i]['bidder']
                    subrdata['to'] = await getUserName(bids[i]['bidder'])
                    subrdata['toAddr'] = bids[i]['bidder']
                    subrdata['tx'] = d["txhash"]
                    subrdata['date'] = d["timestamp"]
                    rdata.append(subrdata)
                    i = i + 1
                await CONN.close()
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                edata = {}
                edata['status'] = 500
                return web.json_response(edata)

            return web.json_response(rdata)

        elif method == 'GetHistoryByNftId':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                param_addr = str(param['address'])
                param_id = str(param['id'])
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')
                if checkNumber(param_id) == False:
                    raise Exception('param', 'invalid param')

                result = await CONN.fetch('''
					select * from auctionstatus where status > 0 and itemaddress=$1 and itemid=$2 order by id DESC limit $3
				''', param_addr, int(param_id), int(paging))

                rdata = []
                if result != None:
                    for d in result:
                        auctionid = d['auctionid']
                        subrdata = {}
                        subrdata['event'] = await checkStatus(d['status'])
                        if (d['auctiontype'] == 1):
                            subrdata['price'] = format(float(d['amount']), '.0f')
                        else:
                            subrdata['price'] = format(float(d['startingprice']), '.0f')

                        subrdata['by'] = d["seller"]
                        subrdata['to'] = d["buyer"]
                        subrdata['tx'] = d["txhash"]
                        subrdata['date'] = d["timestamp"]
                        rdata.append(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)
            await CONN.close()
            return web.json_response(rdata)

        elif method == 'GetSellerInfo':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                param_addr = str(param['address'])
                param_id = str(param['id'])
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')
                if checkNumber(param_id) == False:
                    raise Exception('param', 'invalid param')

                d = await CONN.fetchrow('''
					select * from auctionstatus where status = 0 and itemaddress=$1 and itemid=$2
				''', param_addr, int(param_id))

                if d != None:
                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    subrdata = {}
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['auctiontype'] = d['auctiontype']
                    subrdata['seller'] = d['seller']
                    # subrdata['sellerName'] = await getUserName(d['seller'])

                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    if (name == None):
                        subrdata['sellerName'] = await getUserName(d['seller'])
                    else:
                        subrdata['sellerName'] = name

                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']

                    subrdata['startPrice'] = format(float(d['startingprice']), '.0f')
                    if (d['auctiontype'] == 1):
                        qry = "select amount from auctionlog where auctionid = " + str(
                            d['auctionid']) + " and eventtype='BidActivated' order by id desc limit 1"
                        print(qry)
                        amount = await CONN.fetchval(qry)
                        print(amount)
                        if amount != None:
                            subrdata['currentPrice'] = format(float(amount), '.0f')
                        else:
                            subrdata['currentPrice'] = 0
                    else:
                        subrdata['currentPrice'] = format(float(d['startingprice']), '.0f')

                    f = await CONN.fetchrow('''
						select * from nftinfo where nftaddress=$1 and nftid=$2 limit 1
					''', param_addr, int(param_id))

                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    print(subrdata)
                    await CONN.close()
                    return web.json_response(subrdata)
                else:
                    subrdata = {}
                    subrdata['type'] = 2
                    subrdata['auctiontype'] = -1
                    subrdata['auctionid'] = -1
                    subrdata['seller'] = 0x0000000000000000000000000000000000000000
                    subrdata['sellerName'] = ""
                    subrdata['itemaddress'] = param['address']
                    subrdata['itemid'] = param['id']
                    subrdata['startPrice'] = 0
                    subrdata['currentPrice'] = 0
                    f = await CONN.fetchrow('''
						select * from nftinfo where nftaddress=$1 and nftid=$2 limit 1
					''', param_addr, int(param_id))

                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    await CONN.close()
                    return web.json_response(subrdata)

            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata


        elif method == 'GetActivity':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                qry = "select * from auctionstatus where status = 1 order by id desc"
                print(qry)
                result = await CONN.fetch(qry)
                rdata = []
                for d in result:
                    subrdata = {}
                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    if (name == None):
                        subrdata['sellerName'] = await getUserName(d['seller'])
                    else:
                        subrdata['sellerName'] = name
                    qry = "select name from userinfo where account = '" + d['buyer'] + "'"
                    name = await CONN.fetchval(qry)
                    if (name == None):
                        subrdata['buyerName'] = await getUserName(d['buyer'])
                    else:
                        subrdata['buyerName'] = name
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['seller'] = d['seller']
                    subrdata['buyer'] = d['buyer']
                    subrdata['price'] = format(float(d['amount']), '.0f')
                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']
                    subrdata['tx'] = d['txhash']

                    qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                        d['itemid']) + ' limit 1'
                    f = await CONN.fetchrow(qry)
                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    rdata.append(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata
            await CONN.close()
            rdata = web.json_response(rdata)
            print(rdata)
            return rdata


        elif method == 'GetDetailActivity':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])

                param_addr = str(param['address'])
                param_id = str(param['id'])
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')
                if checkNumber(param_id) == False:
                    raise Exception('param', 'invalid param')

                d = await CONN.fetchrow('''
					select * from auctionstatus where status = 1 and itemaddress=$1 and itemid=$2
				''', param_addr, int(param_id))

                if d != None:
                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    subrdata = {}
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['auctiontype'] = d['auctiontype']
                    subrdata['seller'] = d['seller']

                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    if (name == None):
                        subrdata['sellerName'] = await getUserName(d['seller'])
                    else:
                        subrdata['sellerName'] = name

                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']

                    # subrdata['startPrice'] = str(d['startingprice'])
                    subrdata['startPrice'] = format(float(d['startingprice']), '.0f')
                    # format(float('1.00E+18'), '.0f')
                    subrdata['currentPrice'] = format(float(d['amount']), '.0f')

                    f = await CONN.fetchrow('''
						select * from nftinfo where nftaddress=$1 and nftid=$2 limit 1
					''', param_addr, int(param_id))

                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    print(subrdata)
                    await CONN.close()
                    return web.json_response(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata

        elif method == 'GetHistoryByUserAddress':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                param_addr = str(param['address'])
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')
                result = await CONN.fetch('''
					select * from auctionstatus where status > 0 and seller=$1 or buyer = $2 order by id DESC limit $3
				''', param_addr, param_addr, int(paging))

                rdata = []
                for d in result:
                    auctionid = d['auctionid']
                    subrdata = {}
                    subrdata['event'] = await checkStatus(d['status'])

                    if (d['auctiontype'] == 1):
                        subrdata['price'] = format(float(d['amount']), '.0f')
                    else:
                        subrdata['price'] = format(float(d['startingprice']), '.0f')
                    subrdata['by'] = d['seller']
                    subrdata['to'] = d['buyer']
                    subrdata['tx'] = d["txhash"]
                    subrdata['date'] = d["timestamp"]
                    rdata.append(subrdata)

            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata
            await CONN.close()
            rdata = web.json_response(rdata)
            print(rdata)
            return rdata
        elif method == 'GetBrandPageList':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                qry = "select * from featured where activate=1 order by id desc"
                ret = await CONN.fetch(qry)
                ssuper = []
                for i in ret:
                    rfeat = {}
                    rfeat['id'] = i['id']
                    rfeat['image'] = i['image']
                    rfeat['title'] = i['title']
                    rfeat['description'] = i['description']
                    ssuper.append(rfeat)
                await CONN.close()
                return web.json_response(ssuper)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)

        elif method == 'GetDetailedBrandPage':
            try:
                param_id = str(param['id'])
                if checkNumber(param_id) == False:
                    raise Exception('param', 'invalid param')

                CONN = await asyncpg.connect(config[mode]['db'])
                ret = await CONN.fetchrow('''
					select * from featured where activate=1 and id = $1
				''', int(param_id))
                rfeat = {}
                rfeat['id'] = ret['id']
                rfeat['image'] = ret['image']
                rfeat['title'] = ret['title']
                rfeat['description'] = ret['description']
                rfeat['contents'] = ret['page']

                if ret['itemaddress'] == '0xE4218895E979ca7db2624b74604509FdD60C8d75':
                    zpop = []
                    yama = []
                    qry = "select * from auctionstatus where status = 0 and itemaddress = '" + ret[
                        'itemaddress'] + "' order by id desc limit " + paging
                    result = await CONN.fetch(qry)
                    for d in result:
                        subrdata = {}
                        subrdata['auctiontype'] = d['auctiontype']
                        subrdata['auctionid'] = d['auctionid']
                        subrdata['itemaddress'] = d['itemaddress']
                        subrdata['itemid'] = d['itemid']
                        subrdata['seller'] = d['seller']
                        # subrdata['sellerName'] = await getUserName(d['seller'])
                        qry = "select name from userinfo where account = '" + d['seller'] + "'"
                        name = await CONN.fetchval(qry)
                        if (name == None):
                            subrdata['sellerName'] = await getUserName(d['seller'])
                        else:
                            subrdata['sellerName'] = name

                        if (d['auctiontype'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            if (d['amount'] == 0):
                                subrdata['price'] = format(float(d['startingprice']), '.0f')
                            else:
                                subrdata['price'] = format(float(d['amount']), '.0f')
                        qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                            d['itemid']) + ' limit 1'
                        f = await CONN.fetchrow(qry)
                        # print(str(f['nftname']))
                        subrdata['name'] = f['title']
                        subrdata['image'] = f['image']
                        subrdata['description'] = f['description']
                        if str(f['description']).startswith('Hiro Yamagata.'):
                            yama.append(subrdata)
                        elif str(f['description']).startswith('Z-'):
                            zpop.append(subrdata)
                    if rfeat['title'] == 'Zenx Hub X Hiro Yamagata':
                        rfeat['items'] = yama
                    elif rfeat['title'] == 'Zenx Hub X Z-POP Dream':
                        rfeat['items'] = zpop
                else:
                    yama = []
                    qry = "select * from auctionstatus where status = 0 and itemaddress = '" + ret[
                        'itemaddress'] + "' order by id desc limit " + paging
                    result = await CONN.fetch(qry)
                    for d in result:
                        subrdata = {}
                        subrdata['auctiontype'] = d['auctiontype']
                        subrdata['auctionid'] = d['auctionid']
                        subrdata['itemaddress'] = d['itemaddress']
                        subrdata['itemid'] = d['itemid']
                        subrdata['seller'] = d['seller']
                        # subrdata['sellerName'] = await getUserName(d['seller'])
                        qry = "select name from userinfo where account = '" + d['seller'] + "'"
                        name = await CONN.fetchval(qry)
                        if (name == None):
                            subrdata['sellerName'] = await getUserName(d['seller'])
                        else:
                            subrdata['sellerName'] = name

                        if (d['auctiontype'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            if (d['amount'] == 0):
                                subrdata['price'] = format(float(d['startingprice']), '.0f')
                            else:
                                subrdata['price'] = format(float(d['amount']), '.0f')
                        qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                            d['itemid']) + ' limit 1'
                        f = await CONN.fetchrow(qry)
                        # print(str(f['nftname']))
                        subrdata['name'] = f['title']
                        subrdata['image'] = f['image']
                        subrdata['description'] = f['description']
                        yama.append(subrdata)
                    rfeat['items'] = yama

                result = await CONN.fetch(qry)

                await CONN.close()
                return web.json_response(rfeat)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)


        elif method == 'GetListingInfo':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                result = await CONN.fetch('''
					select description from nft_registration where type < 999
				''')
                rdata = []
                for d in result:
                    rdata.append(d['description'])
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata
            await CONN.close()
            rdata = web.json_response(rdata)
            print(rdata)
            return rdata

        elif method == 'GetItemsByCatetory':
            try:
                param_category = str(param['category'])
                if checkNumber(param_category) == False:
                    raise Exception('param_category', 'invalid param')

                param_sellType = str(param['sellType'])
                if checkNumber(param_sellType) == False:
                    raise Exception('param_sellType', 'invalid param')

                param_orderBy = str(param['orderBy'])
                if checkNumber(param_orderBy) == False:
                    raise Exception('param_orderBy', 'invalid param')

                ###
                ### for BT listing, just dummy codes, someone has to re-implelents all.
                qry = ""
                if param_category == '0':
                    if param_sellType == '0':
                        if param_orderBy == '0':
                            qry = "select * from auctionstatus where status = 0 order by id desc"
                        elif param_orderBy == '1':
                            qry = "select * from auctionstatus where status = 0 order by id asc"
                        elif param_orderBy == '2':
                            qry = "select * from auctionstatus where status = 0 order by startingprice desc"
                        elif param_orderBy == '3':
                            qry = "select * from auctionstatus where status = 0 order by startingprice asc"
                    elif param_sellType == '1':
                        if param_orderBy == '0':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 0 order by id desc"
                        elif param_orderBy == '1':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 0 order by id asc"
                        elif param_orderBy == '2':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 0 order by startingprice desc"
                        elif param_orderBy == '3':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 0 order by startingprice asc"
                    elif param_sellType == '2':
                        if param_orderBy == '0':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 1 order by id desc"
                        elif param_orderBy == '1':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 1 order by id asc"
                        elif param_orderBy == '2':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 1 order by startingprice desc"
                        elif param_orderBy == '3':
                            qry = "select * from auctionstatus where status = 0 and auctiontype = 1 order by startingprice asc"
                else:
                    if param_sellType == '0':
                        if param_orderBy == '0':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 order by id desc"
                        elif param_orderBy == '1':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 order by id asc"
                        elif param_orderBy == '2':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 order by startingprice desc"
                        elif param_orderBy == '3':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 order by startingprice asc"
                    elif param_sellType == '1':
                        if param_orderBy == '0':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 0 order by id desc"
                        elif param_orderBy == '1':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 0 order by id asc"
                        elif param_orderBy == '2':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 0 order by startingprice desc"
                        elif param_orderBy == '3':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 0 order by startingprice asc"
                    elif param_sellType == '2':
                        if param_orderBy == '0':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 1 order by id desc"
                        elif param_orderBy == '1':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 1 order by id asc"
                        elif param_orderBy == '2':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 1 order by startingprice desc"
                        elif param_orderBy == '3':
                            qry = "select * from auctionstatus where itemaddress in (select nftaddr from nft_registration where category =" + param_category + " and type = 999) and status = 0 and auctiontype = 1 order by startingprice asc"

                # print(qry)
                CONN = await asyncpg.connect(config[mode]['db'])
                result = await CONN.fetch(qry)
                rdata = []
                for d in result:
                    subrdata = {}
                    subrdata['auctiontype'] = d['auctiontype']
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']
                    subrdata['seller'] = d['seller']

                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    if (name == None):
                        subrdata['sellerName'] = await getUserName(d['seller'])
                    else:
                        subrdata['sellerName'] = name

                    if (d['auctiontype'] == 0):
                        subrdata['price'] = format(float(d['startingprice']), '.0f')
                    else:
                        if (d['amount'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            subrdata['price'] = format(float(d['amount']), '.0f')
                    qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                        d['itemid']) + ' limit 1'
                    f = await CONN.fetchrow(qry)
                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    rdata.append(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata
            await CONN.close()
            rdata = web.json_response(rdata)
            return rdata


        elif method == 'GetLatestOrders':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                qry = "select * from auctionstatus where status = 0 order by id desc"
                result = await CONN.fetch(qry)
                rdata = []
                for d in result:
                    subrdata = {}
                    subrdata['auctiontype'] = d['auctiontype']
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']
                    subrdata['seller'] = d['seller']

                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    if (name == None):
                        subrdata['sellerName'] = await getUserName(d['seller'])
                    else:
                        subrdata['sellerName'] = name

                    if (d['auctiontype'] == 0):
                        subrdata['price'] = format(float(d['startingprice']), '.0f')
                    else:
                        if (d['amount'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            subrdata['price'] = format(float(d['amount']), '.0f')
                    qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                        d['itemid']) + ' limit 1'
                    f = await CONN.fetchrow(qry)
                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    rdata.append(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata
            await CONN.close()
            rdata = web.json_response(rdata)
            print(rdata)
            return rdata
        elif method == 'GetFeaturedOrders':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                qry = "select * from featured where activate=1 order by id desc"
                ret = await CONN.fetch(qry)
                ssuper = []
                for i in ret:
                    rfeat = {}
                    rfeat['id'] = i['id']
                    rfeat['image'] = i['image']
                    rfeat['title'] = i['title']
                    rfeat['description'] = i['description']
                    rfeat['name'] = i['name']
                    addr = i['itemaddress']
                    qry = "select * from auctionstatus where status = 0 and itemaddress = '" + addr + "' order by id desc limit " + paging
                    print(qry)
                    result = await CONN.fetch(qry)
                    # rdata = []
                    zpop = []
                    yama = []
                    axie = []
                    lok = []
                    eggr = []
                    gt = []
                    comic = []

                    for d in result:
                        subrdata = {}
                        subrdata['auctiontype'] = d['auctiontype']
                        subrdata['auctionid'] = d['auctionid']
                        subrdata['itemaddress'] = d['itemaddress']
                        subrdata['itemid'] = d['itemid']
                        subrdata['seller'] = d['seller']
                        # subrdata['sellerName'] = await getUserName(d['seller'])
                        qry = "select name from userinfo where account = '" + d['seller'] + "'"
                        name = await CONN.fetchval(qry)
                        if (name == None):
                            subrdata['sellerName'] = await getUserName(d['seller'])
                        else:
                            subrdata['sellerName'] = name

                        if (d['auctiontype'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            if (d['amount'] == 0):
                                subrdata['price'] = format(float(d['startingprice']), '.0f')
                            else:
                                subrdata['price'] = format(float(d['amount']), '.0f')
                        qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                            d['itemid']) + ' limit 1'
                        f = await CONN.fetchrow(qry)

                        # print(str(f['nftname']))
                        subrdata['name'] = f['title']
                        subrdata['image'] = f['image']
                        subrdata['description'] = f['description']
                        if str(f['description']).startswith('Hiro Yamagata.'):
                            yama.append(subrdata)
                        elif str(f['description']).startswith('Z-'):
                            zpop.append(subrdata)
                        elif str(f['nftname']).startswith('Axie'):
                            axie.append(subrdata)
                        elif str(f['nftname']).startswith('League of Kingdoms'):
                            lok.append(subrdata)
                        elif str(f['nftname']).startswith('EGGRYPTO:Monster'):
                            eggr.append(subrdata)
                        elif str(f['nftname']).startswith('MotoGP NinjaStickers'):
                            gt.append(subrdata)
                        elif str(f['nftname']).startswith('Golden Age Comics'):
                            comic.append(subrdata)

                    if rfeat['title'] == 'Zenx Hub X Hiro Yamagata':
                        rfeat['items'] = yama
                    elif rfeat['title'] == 'Zenx Hub X Z-POP Dream':
                        rfeat['items'] = zpop
                    elif rfeat['title'] == 'AXIE INFINITY Collection is Open':
                        rfeat['items'] = axie
                    elif rfeat['title'] == 'League of Kingdoms Collection is Open':
                        rfeat['items'] = lok
                    elif rfeat['title'] == "Eggrypto's Collection is Open":
                        rfeat['items'] = eggr
                    elif rfeat['title'] == "MotoGP Ninja Stickers’ Collection is Open":
                        rfeat['items'] = gt
                    elif rfeat['title'] == "Golden Age Comics’ Collection is Open":
                        rfeat['items'] = comic

                    ssuper.append(rfeat)

                await CONN.close()
                return web.json_response(ssuper)

            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)

        elif method == 'GetOldestOrders':
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                qry = "select * from auctionstatus where status = 0 order by startingprice desc limit " + paging
                result = await CONN.fetch(qry)
                rdata = []
                for d in result:
                    subrdata = {}
                    subrdata['auctiontype'] = d['auctiontype']
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']
                    subrdata['seller'] = d['seller']
                    qry = "select name from userinfo where account = '" + d['seller'] + "'"
                    name = await CONN.fetchval(qry)
                    if (name == None):
                        subrdata['sellerName'] = await getUserName(d['seller'])
                    else:
                        subrdata['sellerName'] = name

                    if (d['auctiontype'] == 0):
                        subrdata['price'] = format(float(d['startingprice']), '.0f')
                    else:
                        if (d['amount'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            subrdata['price'] = format(float(d['amount']), '.0f')
                    qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                        d['itemid']) + ' limit 1'
                    f = await CONN.fetchrow(qry)
                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    rdata.append(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                rdata = web.json_response(rdata)
                return rdata
            await CONN.close()
            rdata = web.json_response(rdata)
            print(rdata)
            return rdata

        elif method == 'GetUserOrders':
            try:
                ## Auction
                CONN = await asyncpg.connect(config[mode]['db'])
                param_addr = str(param['address'])
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')

                try:
                    collection_id = param['collection_id']
                except Exception as inst:
                    collection_id = None

                result = await CONN.fetch('''
                    select * from auctionstatus where status = 0 and seller = $1 order by id asc
                ''', param_addr)

                curUserName = None

                name = await CONN.fetchval('''
					select name from userinfo where account = $1
				''', param_addr)

                if (name == None):
                    curUserName = 'No Name'
                else:
                    curUserName = name

                rdata = []
                for d in result:
                    subrdata = {}
                    subrdata['type'] = 0
                    subrdata['auctiontype'] = d['auctiontype']
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']
                    subrdata['seller'] = d['seller']
                    # subrdata['sellerName'] = await getUserName(d['seller'])
                    subrdata['sellerName'] = curUserName

                    if (d['auctiontype'] == 0):
                        subrdata['price'] = format(float(d['startingprice']), '.0f')
                    else:
                        if (d['amount'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            subrdata['price'] = format(float(d['amount']), '.0f')
                    if collection_id is not None:
                        qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and collectionid=" + str(
                            collection_id) + " and nftid=" + str(
                        d['itemid']) + ' limit 1'
                    else:
                        qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                        d['itemid']) + ' limit 1'
                    f = await CONN.fetchrow(qry)
                    if f is None:
                        continue
                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    rdata.append(subrdata)

                ## BID 
                qry = "select a.auctiontype, a.seller, a.buyer, a.itemaddress, a.itemid, a.startingprice, b.bidamount, a.auctionid, a.status, a.txhash from auctionstatus a, bidstatus b where a.auctionid = b.auctionid and b.status = 0 and a.status = 0 and b.bidder = '" + param_addr + "' order by a.id desc"
                result = await CONN.fetch(qry)
                for d in result:
                    subrdata = {}
                    subrdata['type'] = 1
                    subrdata['auctiontype'] = d['auctiontype']
                    subrdata['auctionid'] = d['auctionid']
                    subrdata['itemaddress'] = d['itemaddress']
                    subrdata['itemid'] = d['itemid']
                    subrdata['seller'] = d['seller']
                    # subrdata['sellerName'] = await getUserName(d['seller'])
                    subrdata['sellerName'] = curUserName

                    if (d['auctiontype'] == 0):
                        subrdata['price'] = format(float(d['startingprice']), '.0f')
                    else:
                        if (d['bidamount'] == 0):
                            subrdata['price'] = format(float(d['startingprice']), '.0f')
                        else:
                            subrdata['price'] = format(float(d['bidamount']), '.0f')
                    if collection_id is not None:
                        qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and collectionid=" + str(
                            collection_id) + " and nftid=" + str(
                            d['itemid']) + ' limit 1'
                    else:
                        qry = "select * from nftinfo where nftaddress='" + d['itemaddress'] + "' and nftid=" + str(
                            d['itemid']) + ' limit 1'
                    f = await CONN.fetchrow(qry)
                    if f is None:
                        continue
                    subrdata['name'] = f['title']
                    subrdata['image'] = f['image']
                    subrdata['description'] = f['description']
                    rdata.append(subrdata)
                ## OTHERS
                if collection_id is not None:
                    qry = "select * from nftinfo where owner = '" + param_addr + "' and collectionid = " + str(
                        collection_id)
                else:
                    qry = "select * from nftinfo where owner = '" + param_addr + "'"
                result = await CONN.fetch(qry)
                if result is not None:
                    for d in result:
                        subrdata = {}
                        subrdata['type'] = 2
                        subrdata['auctiontype'] = -1
                        subrdata['auctionid'] = -1
                        subrdata['itemaddress'] = d['nftaddress']
                        subrdata['itemid'] = d['nftid']
                        subrdata['seller'] = param_addr
                        subrdata['sellerName'] = curUserName
                        subrdata['price'] = 0
                        if collection_id is not None:
                            qry = "select * from nftinfo where nftaddress='" + d['nftaddress'] + "' and collectionid=" + str(
                                collection_id) + " and nftid=" + str(
                                d['nftid']) + ' limit 1'
                        else:
                            qry = "select * from nftinfo where nftaddress='" + d['nftaddress'] + "' and nftid=" + str(
                                d['nftid']) + ' limit 1'
                        f = await CONN.fetchrow(qry)
                        if f is None:
                            continue
                        subrdata['name'] = f['title']
                        subrdata['image'] = f['image']
                        subrdata['description'] = f['description']
                        rdata.append(subrdata)

                # await regNfts(param_addr)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)
            await CONN.close()
            rdata = web.json_response(rdata)
            print(rdata)
            return rdata

        elif method == 'GetUserBids':
            try:
                param_addr = str(param['address'])
                param_id = str(param['id'])
                if checkAddr(param_addr) == False:
                    raise Exception('param', 'invalid param')

                CONN = await asyncpg.connect(config[mode]['db'])
                qry = "select distinct(A.auctionid) from ( select auctionid, max(bidid) as maxbid from auctionlog where auctionid in (select distinct auctionid from auctionlog where auctionid not in (select auctionid from auctionlog where eventtype='AuctionClosed') and eventtype='BidActivated' group by auctionid ) group by auctionid) A, auctionlog B where A.auctionid=B.auctionid and A.maxbid = B.bidid and B.eventtype = 'BidCreated' and B.bidder = '" + param_addr + "'"
                result = await CONN.fetch(qry)
                rdata = []
                for d in result:
                    auctionid = d['auctionid']
                    subrdata = {}
                    (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid,
                     bidCount) = contract.functions.getAuction(auctionid).call()
                    subrdata['bidderName'] = await getUserName(param_addr)
                    subrdata['auctionid'] = auctionid
                    subrdata['itemaddress'] = item[0]
                    subrdata['itemid'] = item[1]
                    rdata.append(subrdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                rdata = {}
                rdata['status'] = 500
                return web.json_response(rdata)
            await CONN.close()
            rdata = web.json_response(rdata)
            print(rdata)
            return rdata

        else:
            rdata = {}
            print("Can't catch...")
            rdata['status'] = 500
            return web.json_response(rdata)


@routes.post('/post')
async def contents_handler(request):
    if request.body_exists:
        data = await request.json()
        method = data['method']
        param = data['param']
        if method == "GetArticles":
            try:
                CONN = await asyncpg.connect(config[mode]['db'])
                qry = "select * from nftarticle order by created_at desc limit 3"
                ret = await CONN.fetch(qry)
                rdata = []
                for d in ret:
                    sdata = {}
                    sdata['url'] = d['article']
                    sdata['title'] = d['title']
                    sdata['image'] = d['image']
                    sdata['contents'] = d['contents']
                    rdata.append(sdata)
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)
                await CONN.close()
                edata = {}
                edata['status'] = 500
                return web.json_response(edata)
            await CONN.close()
            return web.json_response(rdata)


@routes.post('/post')
async def ping(request):
    response_obj = {'status': 'success'}
    return web.Response(text=json.dumps(response_obj))


app = web.Application()
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(allow_methods=["GET", 'POST'], allow_credentials=True, expose_headers="*",
                                      allow_headers="*"),
})

cors.add(app.router.add_post('/v1/item', item_handler))
cors.add(app.router.add_post('/v1/adminlist', adminlist_handler))
cors.add(app.router.add_post('/v1/banner', banner_handler))
cors.add(app.router.add_post('/v1/collection', collection_handler))
cors.add(app.router.add_post('/v1/account', account_handler))
cors.add(app.router.add_post('/v1/auction', auction_handler))
cors.add(app.router.add_post('/v1/contents', contents_handler))
cors.add(app.router.add_post('/', ping))

if __name__ == '__main__':
    web.run_app(app, port=config[mode]['port'])
