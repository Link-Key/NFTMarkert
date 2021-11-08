import asyncio
import asyncpg
import datetime
from dynaconf import settings

async def main():
	NETWORK_ID = settings.NETWORK_ID
	conn = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)

	await conn.execute('''
	    DROP TABLE IF EXISTS AuctionCreated;
	''')
	await conn.execute('''
	    CREATE TABLE AuctionCreated(
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        auctionId bigint,
	        seller varchar(66),
	        itemAddress varchar(66),
	        itemId bigint,
	        auctionType bigint,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')

	# event AuctionClosed(uint256 auctionId, State closedstate);
	await conn.execute('''
	    DROP TABLE IF EXISTS AuctionClosed
	''')
	await conn.execute('''
	    CREATE TABLE AuctionClosed (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        auctionId bigint,
	        closedstate bigint,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')


	# event MarketTTLUpdate(uint256 oldValue, uint256 newValue);
	await conn.execute('''
	    DROP TABLE IF EXISTS MarketTTLUpdate
	''')
	await conn.execute('''
	    CREATE TABLE MarketTTLUpdate (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        oldValue bigint,
	        newValue bigint,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')

	# event MarketFeeUpdate(FeeParam param, uint256 oldValue, uint256 newValue);
	await conn.execute('''
	    DROP TABLE IF EXISTS MarketFeeUpdate
	''')
	await conn.execute('''
	    CREATE TABLE MarketFeeUpdate (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        param bigint,
	        oldValue bigint,
	        newValue bigint,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')

	# event MarketFeesCollected(address collectingManager, uint256 amountCollected);
	await conn.execute('''
	    DROP TABLE IF EXISTS MarketFeesCollected
	''')
	await conn.execute('''
	    CREATE TABLE MarketFeesCollected (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        collectingManager varchar(66),
	        amountCollected NUMERIC DEFAULT 0,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')

	# event BidCreated(address bidder, uint256 auctionId, uint256 bidId);
	await conn.execute('''
	    DROP TABLE IF EXISTS BidCreated
	''')

	await conn.execute('''
	    CREATE TABLE BidCreated (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        bidder varchar(66),
	        auctionId bigint,
	        bidId bigint,
	        amount NUMERIC DEFAULT 0,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')

	await conn.execute('''
	    DROP TABLE IF EXISTS BidActivated
	''')
	await conn.execute('''
	    CREATE TABLE BidActivated (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        auctionId bigint,
	        bidId bigint,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')

	await conn.execute('''
	    DROP TABLE IF EXISTS BidDeactivated
	''')

	await conn.execute('''
	    CREATE TABLE BidDeactivated (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        auctionId bigint,
	        bidId bigint,
	        newBidState bigint,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')


	await conn.execute('''
	    DROP TABLE IF EXISTS NFTCreated
	''')
	await conn.execute('''
	    CREATE TABLE NFTCreated (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        nftId bigint,
	        nftContract varchar(66),
	        creator varchar(66),
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')


	await conn.execute('''
	    DROP TABLE IF EXISTS RoyaltyCollected
	''')
	await conn.execute('''
	    CREATE TABLE RoyaltyCollected (
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        beneficiary varchar(66),
	        amountCollected NUMERIC DEFAULT 0,
	        fromAddress varchar(66),
	        txHash varchar(66)
	    )
	''')

	await conn.execute('''
	    DROP TABLE IF EXISTS AuctionLog
	''')
	await conn.execute('''
	    CREATE TABLE AuctionLog(
	        id serial PRIMARY KEY,
	        timestamp bigint,
	        seller varchar(66),
	        itemAddress varchar(66),
	        itemId bigint,
	        auctionType bigint,
	        auctionId bigint,
	        bidder varchar(66),
	        bidId bigint,
	        amount NUMERIC DEFAULT 0,
	        auctionState bigint default 0,
	        bidState bigint default 0,
	        fromAddress varchar(66),
	        eventType varchar(66),
	        txHash varchar(66)
	    )
	''')

	await conn.execute('''
	    DROP TABLE IF EXISTS NFTEvent
	''')

	await conn.execute('''
	    CREATE TABLE NFTEvent(
	    	timestamp bigint,
	        _from varchar(66),
	        _to varchar(66),
	        id bigint,
	        approved boolean,
	        uri varchar(256),
	        fromAddress varchar(66),
	        txHash varchar(66),
	        eventType varchar(66)
	    )
	''')

	await conn.execute('''
	    DROP TABLE IF EXISTS NFT_REGISTRATION
	''')

	await conn.execute('''
	    CREATE TABLE NFT_REGISTRATION (
	        nftAddr varchar(66) PRIMARY KEY,
	        type bigint default 0,
	        confirmed bigint default 0,
	        flag bigint default 0,
	        category bigint default 0,
	        description varchar(256)
	    )
	''')

	await conn.execute('''
		DROP TABLE IF EXISTS NFTInfo
	''')

	await conn.execute('''
	    CREATE TABLE NFTInfo(
	        id serial PRIMARY KEY,
	        owner varchar(66),
	        nftName varchar(128),     
	        nftSymbol varchar(64),     
	        nftAddress varchar(66),
	        nftId bigint,
	        title varchar(128),
	        category varchar(128),
	        uri varchar(256),
	        image varchar(256),
	        description text,
	        metadata text, 
	        regDate timestamp
	    )
	''')

	await conn.execute('''
	    DROP TABLE IF EXISTS UserInfo
	''')
	await conn.execute('''
	    CREATE TABLE UserInfo (
	        account varchar(66) PRIMARY KEY,
	        name varchar(64) NOT NULL DEFAULT 'Unnamed',
	        email varchar(64),
	        introduction text, 
	        signature varchar(256),
	        logindate timestamp,
	        regDate timestamp,
	        updateDate timestamp
	    )
	''')


	await conn.execute('''
	    DROP TABLE IF EXISTS AuctionStatus
	''')
	await conn.execute('''
	    CREATE TABLE AuctionStatus (
	    	timestamp bigint,
	        id serial PRIMARY KEY,
	        auctionType bigint,
	        seller varchar(64),
	        buyer varchar(64),
	        itemAddress varchar(66),
	        itemId bigint,
	        startingPrice NUMERIC DEFAULT 0, 
	        amount NUMERIC DEFAULT 0, 
	        auctionId bigint,		
	        status bigint,
	        txHash varchar(66)
	    )
	''')

	await conn.execute('''
	    DROP TABLE IF EXISTS BidStatus
	''')
	await conn.execute('''
	    CREATE TABLE BidStatus (
	        id serial PRIMARY KEY,
	        bidder varchar(64),
	        auctionId bigint,
	        bidId bigint,
	        bidAmount NUMERIC DEFAULT 0,
	        status bigint DEFAULT 0
	    )
	''')


	await conn.execute('''
	    DROP TABLE IF EXISTS Featured;
	''')
	await conn.execute('''
	    CREATE TABLE Featured(
	        id serial PRIMARY KEY,
	        itemAddress varchar(66),
	        title varchar(256),
	        name varchar(256),
	        image varchar(256),
	        description text,
	        activate bigint DEFAULT 0
	    )
	''')

	await conn.execute('''
	    INSERT INTO Featured( itemaddress, title, name, image, description, activate) values($1, $2, $3, $4, $5, $6)
	''', '0xf9DA22988D9645d89E3fE2f4ae6DaF5594aE6014', 'Zenx Hub X Hiro Yamagata Part #1', 'Hiro Yamagata', 'https://ipfs.infura.io/ipfs/QmX2rsSmJpFNFm8bk1YK9fDT5yTiNDwG5cFpMN3wBMT1Jq', 'Buy the ownership of Hiro Yamagata’s artwork as NFT', 1)

	await conn.execute('''
	    INSERT INTO Featured( itemaddress, title, name, image, description, activate) values($1, $2, $3, $4, $5, $6)
	''', '0xf9DA22988D9645d89E3fE2f4ae6DaF5594aE6014', 'Zenx Hub X Hiro Yamagata Part #2', 'Hiro Yamagata', 'https://ipfs.infura.io/ipfs/QmX2rsSmJpFNFm8bk1YK9fDT5yTiNDwG5cFpMN3wBMT1Jq', 'Buy the ownership of Hiro Yamagata’s artwork as NFT', 1)



	await conn.close()

if __name__ == '__main__':
	asyncio.get_event_loop().run_until_complete(main())
