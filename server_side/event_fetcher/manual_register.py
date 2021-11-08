# -*-coding utf-8-*-
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

    prepare_events(settings.NETWORKS[NETWORK_ID].MARKETPLACE_CONTRACT)
    prepare_events(settings.NETWORKS[NETWORK_ID].NFT_CONTRACT)
    return tracked_events


## DB Stuffs
async def fetch(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50,
                                   max_size=99) as pool:
        try:
            return await pool.fetch(query, *args)
        finally:
            await pool.close()


async def fetchrow(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50,
                                   max_size=99) as pool:
        try:
            return await pool.fetchrow(query, *args)
        finally:
            await pool.close()


async def fetchval(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50,
                                   max_size=99) as pool:
        try:
            return await pool.fetchval(query, *args)
        finally:
            await pool.close()


async def execute(query, *args):
    async with asyncpg.create_pool(settings.NETWORKS[NETWORK_ID].DB_URL, command_timeout=60, min_size=50,
                                   max_size=99) as pool:
        try:
            return await pool.execute(query, *args)
        finally:
            await pool.close()


async def processEvent(event, network_id, tracked_events):
    logger.info(f"\r\n{event.event}, {event.address}\r\n{pformat(dict(event.args))}")
    payload = {
        key.replace("_", ""): value.hex() if isinstance(value, bytes) else value
        for key, value in event.args.items()
    }

    CONN = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)
    CONTRACT = W3.eth.contract(address=addr_market, abi=market_abi)
    tx_receipt = W3.eth.getTransactionReceipt(event.transactionHash)
    blockData = W3.eth.getBlock(event.blockNumber)
    eventObj = dict(event.args)
    sTxHash = "0x" + "".join(["{:02X}".format(b) for b in event.transactionHash])

    result = await CONN.fetch("select nftaddr, type, flag from NFT_REGISTRATION where flag = 0")
    for i in result:
        if (i['type'] == 999):
            continue
        if (i['flag'] == 0):
            addr = W3.toChecksumAddress(i['nftaddr'])
            tracked_events = await addNFT(tracked_events, addr)
            await CONN.execute('''
                    update NFT_REGISTRATION set flag = 1 where nftaddr = $1
            ''', i['nftaddr'])
            tracked_events = await removeDuplicate(tracked_events)

    if event.event == "AuctionCreated":
        (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid,
         bidCount) = CONTRACT.functions.getAuction(payload['auctionId']).call()
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, auctionId, seller, itemAddress, itemId, auctionType, fromAddress, eventType, txHash, amount) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ''', blockData.timestamp, payload['auctionId'], payload['seller'], payload['itemAddress'], payload['itemId'],
                           payload['auctionType'], tx_receipt['from'], event.event, sTxHash, startingBid)
        await CONN.execute('''
            INSERT INTO AuctionStatus(seller, auctionid, status, itemAddress, itemId, txHash, auctionType, startingPrice) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
        ''', payload['seller'], payload['auctionId'], 0, payload['itemAddress'], payload['itemId'], sTxHash,
                           auctionType, startingBid)

        CONTRACT = W3.eth.contract(address=payload['itemAddress'], abi=nft_abi)
        name = CONTRACT.functions.name().call()
        symbol = CONTRACT.functions.symbol().call()
        uri = CONTRACT.functions.tokenURI(payload['itemId']).call()
        # if NETWORK_ID != 1:
        #     uri = 'https://ipfs.infura.io/ipfs/Qma8WdSPjC7HMCZd4qzfZVYkMu8JBQj1sgEzgY429dcjmr'
        ret = await CONN.fetchrow('''
            select count(id), owner from NFTInfo where nftId = $1 and nftAddress = $2 group by owner
        ''', payload['itemId'], payload['itemAddress'])

        if (ret == None):
            res = await requests.get(uri)
            data = res.json()
            if (data['name'] == None):
                data['name'] = "No title"
            if data['image'] != None:
                if data['image'].startswith('ipfs://ipfs/'):
                    data['image'] = 'https://ipfs.infura.io/ipfs/' + data['image'][12:]
            else:
                data['image'] = ""
            if (data['description'] == None):
                data['description'] = ""

            date = datetime.datetime.now()
            await CONN.execute('''
                INSERT INTO nftinfo(owner, nftId, nftAddress, nftName, nftsymbol, uri, title, image, description, category, collectionid, regDate) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            ''', seller, payload['itemId'], payload['itemAddress'], name, symbol, uri, data['name'], data['image'],
                               data['description'], data['category'], data['collection'], date)
        # else:
        #     if(seller.lower() != ret['owner'].lower()):
        #         await execute('''
        #             UPDATE NFTInfo SET owner = $1 where nftId = $2 and nftAddress = $3
        #         ''', seller, payload['itemId'], payload['itemAddress'])

    elif event.event == "AuctionClosed":
        (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid,
         bidCount) = CONTRACT.functions.getAuction(payload['auctionId']).call()
        # await execute('''
        #     INSERT INTO AuctionClosed(timestamp, auctionId, closedstate, fromAddress, txHash) VALUES($1, $2, $3, $4, $5)
        # ''', blockData.timestamp, payload['auctionId'], payload['closedstate'], tx_receipt['from'], sTxHash)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, auctionId, auctionState, fromAddress, eventType, txHash) VALUES($1, $2, $3, $4, $5, $6)
        ''', blockData.timestamp, payload['auctionId'], payload['closedState'], tx_receipt['from'], event.event,
                           sTxHash)

        amount = 0
        if (auctionType == 0):
            amount = startingBid
        else:
            if (highBid[2] == 0):
                amount = startingBid
            else:
                amount = highBid[2]

        await CONN.execute('''
            UPDATE AuctionStatus set status = $2, txHash=$3, amount = $4, timestamp = $5, buyer=$6 where auctionid = $1
        ''', payload['auctionId'], payload['closedState'], sTxHash, amount, blockData.timestamp, highBid[1])

        await CONN.execute('''
            UPDATE BidStatus set status = $2 where auctionid = $1
        ''', payload['auctionId'], 1)

    elif event.event == "MarketTTLUpdate":
        await CONN.execute('''
            INSERT INTO MarketTTLUpdate(timestamp, oldValue, newValue, fromAddress, txHash) VALUES($1, $2, $3, $4, $5)
        ''', blockData.timestamp, payload['oldValue'], payload['newValue'], tx_receipt['from'], sTxHash)
    elif event.event == "MarketFeeUpdate":
        await CONN.execute('''
            INSERT INTO MarketFeeUpdate(timestamp, param, oldValue, newValue, fromAddress, txHash) VALUES($1, $2, $3, $4, $5, $6)
        ''', blockData.timestamp, payload['param'], payload['oldValue'], payload['newValue'], tx_receipt['from'],
                           sTxHash)
    elif event.event == "MarketFeesCollected":
        await CONN.execute('''
            INSERT INTO MarketFeesCollected(timestamp, collectingManager, amountCollected, fromAddress, txHash) VALUES($1, $2, $3, $4, $5)
        ''', blockData.timestamp, payload['collectingManager'], payload['amountCollected'], tx_receipt['from'], sTxHash)

    elif event.event == "BidCreated":
        # await execute('''
        #     INSERT INTO BidCreated(timestamp, bidder, auctionId, bidId, amount, fromAddress, txHash) VALUES($1, $2, $3, $4, $5, $6, $7)
        # ''', blockData.timestamp, payload['bidder'], payload['auctionId'], payload['bidId'], payload['amount'], tx_receipt['from'], sTxHash)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, bidder, auctionId, bidId, amount, fromAddress, eventType, txHash) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
        ''', blockData.timestamp, payload['bidder'], payload['auctionId'], payload['bidId'], payload['amount'],
                           tx_receipt['from'], event.event, sTxHash)

    elif event.event == "BidActivated":
        (seller, auctionType, item, listingDeposit, ttl, safetyThreshold, startingBid, state, highBid,
         bidCount) = CONTRACT.functions.getAuction(payload['auctionId']).call()
        # await execute('''
        #     INSERT INTO BidActivated(timestamp, auctionId, bidId, fromAddress, txHash) VALUES($1, $2, $3, $4, $5)
        # ''', blockData.timestamp, payload['auctionId'], payload['bidId'], tx_receipt['from'], sTxHash)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, seller, auctionId, bidId, fromAddress, eventType, txHash, amount) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
        ''', blockData.timestamp, seller, payload['auctionId'], payload['bidId'], tx_receipt['from'], event.event,
                           sTxHash, highBid[2])
        _cnt = await CONN.fetchval('''
            SELECT count(*) from BidStatus where auctionid =  $1
        ''', payload['auctionId'])
        if (_cnt == 0):
            await CONN.execute('''
                INSERT INTO BidStatus(bidder, auctionid, bidId, bidAmount) VALUES($1, $2, $3, $4)
            ''', highBid[1], payload['auctionId'], payload['bidId'], highBid[2])
        else:
            await CONN.execute('''
                UPDATE BidStatus set bidder = $3, bidAmount = $4 where auctionid = $1 and bidid =$2
            ''', payload['auctionId'], payload['bidId'], highBid[1], highBid[2])

    elif event.event == "BidDeactivated":
        # await execute('''
        #     INSERT INTO BidDeactivated(timestamp, auctionId, bidId, newBidState, fromAddress, txHash) VALUES($1, $2, $3, $4, $5, $6)
        # ''', blockData.timestamp, payload['auctionId'], payload['bidId'], payload['newBidState'], tx_receipt['from'], sTxHash)
        await CONN.execute('''
            INSERT INTO AuctionLog(timestamp, auctionId, bidId, bidState, fromAddress, eventType, txHash) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['auctionId'], payload['bidId'], payload['newBidState'], tx_receipt['from'],
                           event.event, sTxHash)
    elif event.event == "NFTCreated":
        await CONN.execute('''
            INSERT INTO NFTCreated(timestamp, nftId, nftContract, creator, fromAddress, txHash) VALUES($1, $2, $3, $4, $5, $6)
        ''', blockData.timestamp, payload['nftId'], payload['nftContract'], payload['creator'], tx_receipt['from'],
                           sTxHash)

    elif event.event == "RoyaltyCollected":
        await CONN.execute('''
            INSERT INTO RoyaltyCollected(timestamp, beneficiary, amountCollected, fromAddress, txHash) VALUES($1, $2, $3, $4, $5)
        ''', blockData.timestamp, payload['beneficiary'], payload['amountCollected'], tx_receipt['from'], sTxHash)

    elif event.event == "Approval":
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, _from, _to, id, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['owner'], payload['approved'], payload['tokenId'], tx_receipt['from'],
                           sTxHash, event.event)

    elif event.event == "ApprovalForAll":
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, _from, _to, approved, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['owner'], payload['operator'], payload['approved'], tx_receipt['from'],
                           sTxHash, event.event)

    elif event.event == "Transfer":
        logger.info("line 249 Transfer!!!! ")
        logger.info(event)
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, _from, _to, id, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6, $7)
        ''', blockData.timestamp, payload['from'], payload['to'], payload['tokenId'], tx_receipt['from'], sTxHash,
                           event.event)

        ret = await CONN.fetchrow('''
            select count(id), owner from NFTInfo where nftId = $1 and nftAddress = $2 group by owner
        ''', payload['tokenId'], event.address)
        logger.info("line 257 ret : ")
        logger.info(str(ret))
        if ret is not None:
            if str(payload['to']).lower() != ret['owner'].lower():
                await CONN.execute('''
                    UPDATE NFTInfo set owner = $1 where nftaddress = $2 and nftid=$3
                ''', payload['to'], event.address, payload['tokenId'])
        else:
            CONTRACT = W3.eth.contract(address=event.address, abi=nft_abi)
            name = CONTRACT.functions.name().call()
            symbol = CONTRACT.functions.symbol().call()
            uri = CONTRACT.functions.tokenURI(payload['tokenId']).call()
            # if NETWORK_ID != 1:
            #     uri = 'https://ipfs.infura.io/ipfs/Qma8WdSPjC7HMCZd4qzfZVYkMu8JBQj1sgEzgY429dcjmr'
            _type = await CONN.fetchval('''
                select type from NFT_REGISTRATION where nftaddr = $1
            ''', event.address)
            logger.info(f'line 274 type :  {str(_type)} ')
            if _type == 0:
                res = await requests.get(uri)
                data = res.json()
                logger.info('data:')
                logger.info(data)
                if (data['name'] == None):
                    data['name'] = "No title"
                if data['image'] != None:
                    if data['image'].startswith('ipfs://ipfs/'):
                        data['image'] = 'https://ipfs.infura.io/ipfs/' + data['image'][12:]
                else:
                    data['image'] = ""
                if (data['description'] == None):
                    data['description'] = ""
                date = datetime.datetime.now()
                await CONN.execute('''
                    INSERT INTO nftinfo(owner, nftId, nftAddress, nftName, nftsymbol, uri, title, image, description, category, collectionid, regDate) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ''', seller, payload['itemId'], payload['itemAddress'], name, symbol, uri, data['name'], data['image'],
                                   data['description'], data['category'], data['collection'], date)
                #     INSERT INTO nftinfo(owner, nftId, nftAddress, nftName, nftSymbol, uri, title, image, description) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
                # ''', payload['to'], payload['tokenId'], event.address, name, symbol, uri, data['name'], data['image'],
                #                    data['description'])
                logger.info("line 292 NFTInfo exec ok!!!")

    elif event.event == "TokenURIUpdate":
        logger.info("line 294 TokenURIUpdate!!!! ")
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, id, uri, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6)
        ''', blockData.timestamp, payload['tokenId'], payload['uri'], tx_receipt['from'], sTxHash, event.event)

    elif event.event == "TokenURIUpdateRequest":
        await CONN.execute('''
            INSERT INTO NFTEvent(timestamp, id, uri, fromAddress, txHash, eventType) VALUES($1, $2, $3, $4, $5, $6)
        ''', blockData.timestamp, payload['tokenId'], payload['uri'], tx_receipt['from'], sTxHash, event.event)

    await CONN.close()
    return tracked_events


async def addNFT(tracked_events, address):
    tracked_events['0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925']['addresses'].append(address)
    tracked_events['0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31']['addresses'].append(address)
    tracked_events['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']['addresses'].append(address)
    tracked_events['0xc9e4a39d461f7a039fb05e3e4695cba6be812449c380b885df430abf38c19fe5']['addresses'].append(address)
    tracked_events['0xe1d45e0914845302a318f84a4b3f0a14865ddde15def23e9be78bb15fd1c628b']['addresses'].append(address)
    return tracked_events


async def removeDuplicate(tracked_events):
    tracked_events['0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925']['addresses'] = list(
        set(tracked_events['0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925']['addresses']))
    tracked_events['0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31']['addresses'] = list(
        set(tracked_events['0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31']['addresses']))
    tracked_events['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']['addresses'] = list(
        set(tracked_events['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']['addresses']))
    tracked_events['0xc9e4a39d461f7a039fb05e3e4695cba6be812449c380b885df430abf38c19fe5']['addresses'] = list(
        set(tracked_events['0xc9e4a39d461f7a039fb05e3e4695cba6be812449c380b885df430abf38c19fe5']['addresses']))
    tracked_events['0xe1d45e0914845302a318f84a4b3f0a14865ddde15def23e9be78bb15fd1c628b']['addresses'] = list(
        set(tracked_events['0xe1d45e0914845302a318f84a4b3f0a14865ddde15def23e9be78bb15fd1c628b']['addresses']))
    return tracked_events


async def eventHandler():
    global W3
    config = ConfigParser()
    config_filename = f'network_id_{NETWORK_ID}_ON.ini'
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
    result = await CONN.fetch("select nftaddr, type, flag from NFT_REGISTRATION where flag = 0")
    for i in result:
        if (i['type'] == 999):
            continue
        if (i['flag'] == 0):
            addr = W3.toChecksumAddress(i['nftaddr'])
            tracked_events = await addNFT(tracked_events, addr)
            await CONN.execute('''
                    update NFT_REGISTRATION set flag = 1 where nftaddr = $1
            ''', i['nftaddr'])
            tracked_events = await removeDuplicate(tracked_events)
    await CONN.close()

    # while True:
    try:
        latest_block = W3.eth.blockNumber
        if latest_block > last_block_number:
            network_id = W3.eth.chainId
            logger.info(f'Block {last_block_number + 1}')
            log_items = W3.eth.filter(
                {'fromBlock': last_block_number + 1, 'toBlock': last_block_number + 1}).get_all_entries()
            for log_item in log_items:
                print(log_item)
                for topic in log_item['topics']:
                    if topic.hex() in tracked_events:
                        try:
                            parsed_event = get_event_data(W3.codec, tracked_events[topic.hex()], log_item)
                            if parsed_event['address'] in tracked_events[topic.hex()]['addresses']:
                                tracked_events = await processEvent(parsed_event, network_id, tracked_events)
                        except LogTopicError:
                            continue

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


# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
asyncio.get_event_loop().run_until_complete(eventHandler())
# asyncio.get_event_loop().run_until_complete(process())