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

import requests_async as requests
import nest_asyncio

nest_asyncio.apply()

NETWORK_ID = settings.NETWORK_ID
# W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL))
W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL, {'max_size': 1_000_000_000}, 30))

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

## DB Stuffs
async def fetch(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.fetch(query, *args)
        finally:
            await pool.close()

async def fetchrow(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.fetchrow(query, *args)
        finally:
            await pool.close()

async def fetchval(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.fetchval(query, *args)
        finally:
            await pool.close()

async def execute(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50, max_size=99) as pool:
        try:
            return await pool.execute(query, *args)
        finally:
            await pool.close()

async def check_key_exist(_dict, key):
    try:
       value = _dict[key]
       return True
    except KeyError:
        return False

async def processEvent(event, network_id):
    logger.info(f"\r\n{event.event}, {event.address}\r\n{pformat(dict(event.args))}")
    payload = {
        key.replace("_", ""): value.hex() if isinstance(value, bytes) else value
        for key, value in event.args.items()
    }
    tx_receipt = W3.eth.getTransactionReceipt(event.transactionHash)
    blockData = W3.eth.getBlock(event.blockNumber)
    eventObj = dict(event.args)
    sTxHash = "0x" + "".join(["{:02X}".format(b) for b in event.transactionHash])
    
    if event.event == "Approval":
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, _from, _to, id, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['owner'], payload['approved'], payload['tokenId'], tx_receipt['from'],  sTxHash, event.event)
        await CONN.close()

    elif event.event == "ApprovalForAll":
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, _from, _to, approved, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['owner'], payload['operator'], payload['approved'], tx_receipt['from'],  sTxHash, event.event)
        await CONN.close()

    elif event.event == "Transfer":
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, _from, _to, id, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['from'], payload['to'], payload['tokenId'], tx_receipt['from'],  sTxHash, event.event)
        
        ret = await CONN.fetchrow('''
            select count(id), owner from NFTInfo where nftId = $1 and nftAddress = $2 group by owner
        ''', payload['tokenId'], event.address)

        # print(ret)
        if ret != None:
            if(str(payload['to']).lower() != ret['owner'].lower()):
                await CONN.execute('''
                    UPDATE NFTInfo set owner = $1 where nftaddress = $2 and nftid=$3
                ''', payload['to'], event.address, payload['tokenId'])
        else:
            NFT = W3.eth.contract(address=event.address, abi=nft_abi)
            name = NFT.functions.name().call()
            symbol= NFT.functions.symbol().call()
            uri = NFT.functions.tokenURI(payload['tokenId']).call()
            _type = await CONN.fetchval('''
                select type from NFT_REGISTRATION where nftaddr = $1
            ''', event.address)

            if(_type == 0):
                res = await requests.get(uri)
                data= res.json()
                print(data)
                if(data['name'] == None):
                    data['name'] = "No title"
                if data['image'] != None:
                    if data['image'].startswith('ipfs://ipfs/'):
                        data['image'] = 'https://ipfs.infura.io/ipfs/' + data['image'][12:]
                else:
                    data['image'] = ""
                if(data['description'] == None):
                    data['description'] = ""
                
                await CONN.execute('''
                    INSERT INTO NFTInfo(owner, nftId, nftAddress, nftName, nftSymbol, uri, title, image, description) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''', payload['to'], payload['tokenId'], event.address, name, symbol, uri, data['name'], data['image'], data['description'])
            elif (_type == 1):
                uri = "https://axieinfinity.com/api/axies/" + str(payload['tokenId'])
                res = await requests.get(uri)
                data= res.json()
                if(data['name'] == None):
                    data['name'] = "No title"
                if data['image'] != None:
                    if data['image'].startswith('ipfs://ipfs/'):
                        data['image'] = 'https://ipfs.infura.io/ipfs/' + data['image'][12:]
                else:
                    data['image'] = ""
                if(data['description'] == None):
                    data['description'] = ""
                
                await CONN.execute('''
                    INSERT INTO NFTInfo(owner, nftId, nftAddress, nftName, nftSymbol, uri, title, image, description) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''', payload['to'], payload['tokenId'], event.address, name, symbol, uri, data['name'], data['image'], data['description'])

            elif (_type == 2):
                uri = "https://api.niftygateway.com/beeple/" + str(tokenId)
                res = await requests.get(uri)
                data= res.json()
                print(data)
                if(data['name'] == None):
                    data['name'] = "No title"
                if data['image'] != None:
                    if data['image'].startswith('ipfs://ipfs/'):
                        data['image'] = 'https://ipfs.infura.io/ipfs/' + data['image'][12:]
                else:
                    data['image'] = ""
                if(data['description'] == None):
                    data['description'] = ""
                await CONN.execute('''
                    INSERT INTO NFTInfo(owner, nftId, nftAddress, nftName, nftSymbol, uri, title, image, description) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''', payload['to'], payload['tokenId'], event.address, name, symbol, uri, data['name'], data['image'], data['description'])
        await CONN.close()

async def addNFT(tracked_events, address):
    tracked_events['0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925']['addresses'].append(address)
    tracked_events['0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31']['addresses'].append(address)
    tracked_events['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']['addresses'].append(address)
    tracked_events['0xc9e4a39d461f7a039fb05e3e4695cba6be812449c380b885df430abf38c19fe5']['addresses'].append(address)
    tracked_events['0xe1d45e0914845302a318f84a4b3f0a14865ddde15def23e9be78bb15fd1c628b']['addresses'].append(address)
    return tracked_events

async def removeDuplicate(tracked_events):
    tracked_events['0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925']['addresses'] = list(set(tracked_events['0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925']['addresses']))
    tracked_events['0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31']['addresses'] = list(set(tracked_events['0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31']['addresses']))
    tracked_events['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']['addresses'] = list(set(tracked_events['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']['addresses']))
    tracked_events['0xc9e4a39d461f7a039fb05e3e4695cba6be812449c380b885df430abf38c19fe5']['addresses'] = list(set(tracked_events['0xc9e4a39d461f7a039fb05e3e4695cba6be812449c380b885df430abf38c19fe5']['addresses']))
    tracked_events['0xe1d45e0914845302a318f84a4b3f0a14865ddde15def23e9be78bb15fd1c628b']['addresses'] = list(set(tracked_events['0xe1d45e0914845302a318f84a4b3f0a14865ddde15def23e9be78bb15fd1c628b']['addresses']))
    return tracked_events

async def eventHandler():
    global W3
    # global CONTRACT
    config = ConfigParser()
    config_filename = f'network_id_{NETWORK_ID}_nft.ini'
    config.read(config_filename)
    if not config.has_section('default'):
        config.add_section('default')
    if not config.has_option('default', 'last_block_number'):
        config.set('default', 'last_block_number', str(W3.eth.blockNumber - 1))
    with open(config_filename, 'w') as f:
        config.write(f)
    last_block_number = int(config.get('default', 'last_block_number'))
    tracked_events = await processEventSignatures()

    CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
    result = await CONN.fetch("select nftaddr, type, flag from NFT_REGISTRATION")
    for i in result:
        if(i['type'] == 999):
            continue
        print(i['nftaddr'])
        tracked_events = await addNFT(tracked_events, i['nftaddr'])
        tracked_events = await removeDuplicate(tracked_events)
    await CONN.close()

    while True:
        try:
            if W3.isConnected() == False:
                W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL, {'max_size': 1_000_000_000}, 30))

            latest_block = W3.eth.blockNumber
            if latest_block > last_block_number:
                network_id = W3.eth.chainId
                logger.info(f'Block {last_block_number + 1}')
                log_items = W3.eth.filter({ 'fromBlock': last_block_number, 'toBlock': last_block_number}).get_all_entries()
                for log_item in log_items:
                    for topic in log_item['topics']:
                        if topic.hex() in tracked_events:
                            try:
                                parsed_event = get_event_data(W3.codec, tracked_events[topic.hex()], log_item)
                                if parsed_event['address'] in tracked_events[topic.hex()]['addresses']:
                                    await processEvent(parsed_event, network_id)
                            except LogTopicError as inst:
                                await asyncio.sleep(0.001)

                config.set('default', 'last_block_number', str(last_block_number + 1))
                with open(config_filename, 'w') as f:
                    config.write(f)
                last_block_number += 1
        except:
            logger.error(traceback.format_exc())
            W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL, {'max_size': 1_000_000_000}, 30))
            await asyncio.sleep(settings.DELAY)
        finally:
            if latest_block <= last_block_number:
                await asyncio.sleep(settings.DELAY)

asyncio.get_event_loop().run_until_complete(eventHandler())