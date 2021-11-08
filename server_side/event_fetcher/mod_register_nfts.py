#-*-coding utf-8-*-
import asyncio
import json
import traceback
from pprint import pformat
from configparser import ConfigParser
from dynaconf import settings
from loguru import logger
from web3 import Web3, WebsocketProvider
from web3._utils.events import construct_event_topic_set, get_event_data
from web3.exceptions import LogTopicError

import asyncio
import asyncpg
import datetime
import uvloop
import random
from urllib.parse import urljoin
import requests_async as requests
import nest_asyncio

NETWORK_ID = settings.NETWORK_ID
nest_asyncio.apply()

W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL, {'max_size': 1_000_000_000}, 30))

addr_market = settings.NETWORKS[NETWORK_ID].MARKETPLACE_CONTRACT['address']
addr_market = W3.toChecksumAddress(addr_market)
abi_path = settings.NETWORKS[NETWORK_ID].MARKETPLACE_CONTRACT['abi']

with open(abi_path) as f:
    market_abi = json.load(f)

addr_nft = settings.NETWORKS[NETWORK_ID].NFT_CONTRACT['address']
addr_nft = W3.toChecksumAddress(addr_nft)
abi_path = settings.NETWORKS[NETWORK_ID].NFT_CONTRACT['abi']

with open(abi_path) as f:
    nft_abi = json.load(f)

async def processEventSignatures():
    tracked_events = {}
    def prepare_events(contract):
        with open(contract['abi'], 'r') as file:
            abi = json.loads(file.read())
            for element in abi:
                if element['type'] == 'event':
                    topic = construct_event_topic_set(element, W3.codec)[0]
                    if element['name'] in contract['tracked_event_names']:
                        if topic not in tracked_events:
                            tracked_events[topic] = element
                            logger.info(f'ADD EVENT {contract["abi"]} - {element["name"]}')
                        if 'addresses' not in tracked_events[topic]:
                            tracked_events[topic]['addresses'] = []
                        tracked_events[topic]['addresses'].append(contract['address'])
    prepare_events(settings.NETWORKS[NETWORK_ID].NFT_CONTRACT)
    return tracked_events

async def regNfts(blockNumber):
    logger.info(f'Block {blockNumber + 1}')
    conn = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
    qry = "select * from nft_registration where type < 999"
    result = await conn.fetch(qry)
    for r in result:
        NFT_ADDR = W3.toChecksumAddress(r['nftaddr'])
        NFT_OBJ = W3.eth.contract(address=NFT_ADDR, abi=nft_abi)
        name = NFT_OBJ.functions.name().call()
        symbol= NFT_OBJ.functions.symbol().call()

        qry = "select account from userinfo"
        result = await conn.fetch(qry)
        for s in result:
            owner = W3.toChecksumAddress(s['account'])
            total = NFT_OBJ.functions.balanceOf(owner).call()
            for i in range(total):
                tokenId = NFT_OBJ.functions.tokenOfOwnerByIndex(owner, i).call()
                ret = await conn.fetchrow('''
                    select count(id), owner from NFTInfo where nftId = $1 and nftAddress = $2 group by owner
                ''', tokenId, r['nftaddr'])

                if(ret == None):
                    print('not registered')
                    _type = await conn.fetchval('''
                        select type from NFT_REGISTRATION where nftaddr = $1
                    ''', r['nftaddr'])
                    if(_type == 0):
                        uri = NFT_OBJ.functions.tokenURI(tokenId).call()
                    elif _type ==  1:
                        uri = "https://axieinfinity.com/api/axies/" + str(tokenId)
                    elif _type == 2:
                        uri = "https://api.niftygateway.com/beeple/" + str(tokenId)

                    # print(uri)
                    res = await requests.get(uri)
                    data= res.json()
                    if(data['name'] == None):
                        data['name'] = "No title"
                    if data['image'].startswith('ipfs://ipfs/'):
                        data['image'] = 'https://ipfs.infura.io/ipfs/' + data['image'][12:]
                    if(data['description'] == None):
                        data['description'] = ""
                    await execute('''
                        INSERT INTO NFTInfo(owner, nftId, nftAddress, nftName, nftSymbol, uri, title, image, description) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ''', owner, tokenId, r['nftaddr'], name, symbol, uri, data['name'], data['image'], data['description'])
                else:
                    print('already registered')
                    if(owner.lower() != ret['owner'].lower()):
                        await conn.execute('''
                            UPDATE NFTInfo SET owner = $1 where nftId = $2 and nftAddress = $3
                        ''', owner, tokenId, r['nftaddr'])
    await conn.close()


async def eventHandler():
    global W3
    config = ConfigParser()
    config_filename = f'network_id_reg_{NETWORK_ID}.ini'
    config.read(config_filename)
    if not config.has_section('default'):
        config.add_section('default')
    if not config.has_option('default', 'last_block_number'):
        config.set('default', 'last_block_number', str(W3.eth.blockNumber - 1))
    with open(config_filename, 'w') as f:
        config.write(f)
    last_block_number = int(config.get('default', 'last_block_number'))
    tracked_events = await processEventSignatures()

    while True:
        try:
            await regNfts(last_block_number)
        except:
            logger.error(traceback.format_exc())
            W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL, {'max_size': 1_000_000_000}, 30))
            await asyncio.sleep(settings.DELAY)
        finally:
            await asyncio.sleep(settings.DELAY_NFT)

asyncio.get_event_loop().run_until_complete(eventHandler())
