import asyncio
import asyncpg
import datetime
from dynaconf import settings

async def main():
	NETWORK_ID = settings.NETWORK_ID
	conn = await asyncpg.connect(settings.NETWORKS[NETWORK_ID].DB_URL)


	# await conn.execute('''
	#     DROP TABLE IF EXISTS NFTArticle
	# ''')
	await conn.execute('''
	    CREATE TABLE NFTArticle (
	    	id serial PRIMARY KEY,
	        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	        article varchar(256),
	        title varchar(256),
	        image varchar(256),
	        contents text,
	        activate bigint
	    )
	''')

	await conn.execute('''
	    INSERT INTO NFTArticle( article, title, image, contents) values($1, $2, $3, $4, $5)
	''', 'https://cicinfthub.medium.com/nft-nft-hub-the-first-nft-marketplace-powered-by-polkadot-f5b11a1d693a', 'NFT NFT Hub, the First NFT Marketplace Powered by Polkadot', 'https://miro.medium.com/max/3624/1*wOEAKpbRXCRF-Ie8u2VyKg.png', 'NFT (Non-fungible Token) is emerging as the biggest keyword in the blockchain industry in 2020. According to Nonfungible.com, the largest database platform of blockchain gaming &amp; crypto collectible markets, the total number of NFT sales in October 2020 was 4.9 million and reached $1.3 billion in transactions. This is a figure which has increased by 57% compared to 2019. In such a promising market, NFT Holdings is accelerating the development of a differentiated NFT Marketplace, the NFT NFT Hub.', 1)

	await conn.execute('''
	    INSERT INTO NFTArticle( article, title, image, contents) values($1, $2, $3, $4, $5)
	''', 'https://cicinfthub.medium.com/nft-nft-hub-vip-service-a-big-success-featuring-contemporary-artist-hiro-yamagata-and-z-pop-stars-b90ad415ff8b', 'NFT starts VIP NFT trading service and collaborates with contemporary artist Hiro Yamagata — Global Coin Report', 'https://miro.medium.com/max/1400/1*ZL_YlZ8F6XDSTSSR2UpYlA.png', 'The NFT NFT Hub (https://zenxhub.zenithx.co) will provide a crypto-powered digital items and collectables trading platform allowing users to create, buy, and sell NFTs. Additionally it will support auction based listings, governance and voting mechanisms, trade history tracking, user rating and other advanced features.', 1)

	await conn.execute('''
	    INSERT INTO NFTArticle( article, title, image, contents) values($1, $2, $3, $4, $5)
	''', 'https://cicinfthub.medium.com/nft-nft-hub-vip-service-a-big-success-featuring-contemporary-artist-hiro-yamagata-and-z-pop-stars-4f252f779cfd', 'NFT starts VIP NFT trading service and collaborates with contemporary artist Hiro Yamagata — Global Coin Report', 'https://miro.medium.com/max/1400/1*g72Dzk4DCKc0OCcQI3_Cog.png', 'NFT NFT Hub (https://zenxhub.zenithx.co) is a crypto-powered digital items and collectibles trading platform allowing users to create, buy, and sell NFTs. It supports auction-based listings, a governance and voting mechanism, trade history tracking, user rating, and other advanced features.', 1)


	await conn.close()
asyncio.get_event_loop().run_until_complete(main())
