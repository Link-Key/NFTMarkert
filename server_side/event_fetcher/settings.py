DELAY = 10
DELAY_NFT = 10

NETWORK_ID = 1
NETWORKS = {
    4: {
        "NODE_URL": "wss://ropsten.infura.io/ws/v3/4a3ccc321c044cc69b9b2a4548af83b9",
        "MARKETPLACE_CONTRACT": {
            "abi": "./contracts/Marketplace.json",
            "address": "0x1b76C05E150F48d2495522FB04dDa24339402F73",
            "tracked_event_names": ['Sold', 'CreateOrder', 'Bid', 'AcceptBid', 'CancelBid', 'CancelOrder', 'ForceClose', 'MarketplaceFeeSet']
        }
    },

    1: {
        "NODE_URL": "wss://mainnet.infura.io/ws/v3/4a3ccc321c044cc69b9b2a4548af83b9",
        "DB_URL": "postgresql://postgres:nft584427169@127.0.0.1:2052/nft",
        "MARKETPLACE_CONTRACT": {
            "abi": "./contracts/nft_market_abi.json",
            "address": "0xe04cA7DD6f34fDD5F1D7C4247D1723c033E65F1F",
            "tracked_event_names": ['AuctionCreated', 'AuctionClosed', 'BidCreated', 'BidActivated', 'BidDeactivated']
        },

        "NFT_CONTRACT": {
            "abi": "./contracts/nft_erc721_abi.json",
            "address": "0xA10527125088f2d033Afa3A98B256d844f7dD864",
            "tracked_event_names": ['TokenURIUpdateRequest', 'TokenURIUpdate', 'Transfer', 'Approval', 'ApprovalForAll']
        },
    }
}

