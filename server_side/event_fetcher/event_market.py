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
W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL, {'max_size': 1_000_000_000}, 30))


addr_market = settings.NETWORKS[NETWORK_ID].MARKETPLACE_CONTRACT['address']
addr_market = W3.toChecksumAddress(addr_market)
abi_path = settings.NETWORKS[NETWORK_ID].MARKETPLACE_CONTRACT['abi']

with open(abi_path) as f:
    market_abi = json.load(f)


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
                        # print(topic)
                        # print(contract['address'])
    prepare_events(settings.NETWORKS[NETWORK_ID].MARKETPLACE_CONTRACT)

    return tracked_events

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
    
    if event.event == "AuctionCreated":
        CONTRACT = W3.eth.contract(address=addr_market, abi=market_abi)
        (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid, bidCount) = CONTRACT.functions.getAuction(payload['auctionId']).call()
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, auctionId, seller, itemAddress, itemId, auctionType, fromAddress, eventType, txHash, amount) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', blockData.timestamp, payload['auctionId'], payload['seller'], payload['itemAddress'], payload['itemId'], payload['auctionType'], tx_receipt['from'], event.event, sTxHash, startingBid)
        await CONN.execute('''
            INSERT INTO AuctionStatus(seller, auctionid, status, itemAddress, itemId, txHash, auctionType, startingPrice) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
        ''', payload['seller'], payload['auctionId'], 0, payload['itemAddress'], payload['itemId'], sTxHash, auctionType, startingBid)
        await CONN.close()


    elif event.event == "AuctionClosed":
        CONTRACT = W3.eth.contract(address=addr_market, abi=market_abi)
        (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid, bidCount) = CONTRACT.functions.getAuction(payload['auctionId']).call()
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, auctionId, auctionState, fromAddress, eventType, txHash) VALUES($1, $2, $3, $4, $5, $6)
        ''', blockData.timestamp, payload['auctionId'], payload['closedState'], tx_receipt['from'], event.event, sTxHash)
        
        amount = 0
        
        if(auctionType == 0):
            amount = startingBid
        else:
            if(highBid[2] == 0):
                amount = startingBid
            else:
                amount = highBid[2]
        await CONN.execute('''
            UPDATE AuctionStatus set status = $2, txHash=$3, amount = $4, timestamp = $5, buyer=$6 where auctionid = $1
        ''', payload['auctionId'], payload['closedState'], sTxHash, amount, blockData.timestamp, highBid[1])

        await CONN.execute('''
            UPDATE BidStatus set status = $2 where auctionid = $1
        ''', payload['auctionId'], 1)
        await CONN.close()
    
    elif event.event == "BidCreated":
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, bidder, auctionId, bidId, amount, fromAddress, eventType, txHash) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
        ''', blockData.timestamp, payload['bidder'], payload['auctionId'], payload['bidId'], payload['amount'], tx_receipt['from'], event.event, sTxHash)
        await CONN.close()
    
    elif event.event == "BidActivated": 
        CONTRACT = W3.eth.contract(address=addr_market, abi=market_abi)
        (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid, bidCount) = CONTRACT.functions.getAuction(payload['auctionId']).call()       
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, seller, auctionId, bidId, fromAddress, eventType, txHash, amount) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
        ''', blockData.timestamp, seller, payload['auctionId'], payload['bidId'], tx_receipt['from'], event.event, sTxHash, highBid[2])
        _cnt = await CONN.fetchval('''
            SELECT count(*) from BidStatus where auctionid =  $1
        ''', payload['auctionId'])
        if(_cnt == 0):
            await CONN.execute('''
                INSERT INTO BidStatus(bidder, auctionid, bidId, bidAmount) VALUES($1, $2, $3, $4)
            ''', highBid[1], payload['auctionId'], payload['bidId'], highBid[2])
        else :
            await CONN.execute('''
                UPDATE BidStatus set bidder = $2, bidAmount = $3 where auctionid = $1
            ''', payload['auctionId'], highBid[1], highBid[2])
        
        await CONN.close()

    elif event.event == "BidDeactivated":
        CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, auctionId, bidId, bidState, fromAddress, eventType, txHash) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['auctionId'], payload['bidId'], payload['newBidState'], tx_receipt['from'], event.event, sTxHash)
        await CONN.close()


async def eventHandler():
    global W3
    # global CONTRACT
    config = ConfigParser()
    config_filename = f'network_id_{NETWORK_ID}_market.ini'
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
                                print(inst.args)   

                config.set('default', 'last_block_number', str(last_block_number + 1))
                with open(config_filename, 'w') as f:
                    config.write(f)
                last_block_number += 1
        except:
            logger.error(traceback.format_exc())
            W3 = Web3(WebsocketProvider(settings.NETWORKS[NETWORK_ID].NODE_URL, {'max_size': 1_000_000_000}, 30))
            CONTRACT = W3.eth.contract(address=addr_market, abi=market_abi)
            await asyncio.sleep(settings.DELAY)
        finally:
            if latest_block <= last_block_number:
                await asyncio.sleep(settings.DELAY)

asyncio.get_event_loop().run_until_complete(eventHandler())
# asyncio.get_event_loop().run_until_complete(process())