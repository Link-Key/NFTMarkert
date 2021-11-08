// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;
pragma abicoder v2;

import "./IERC721.sol";
import "./INftERC721.sol";

/**
 * @dev Interface for NftMarketplace
 */
interface INftMarket {
    enum Type{ BUYNOW, BID }

    enum State { OPEN, SOLD, CANCELLED }

    enum BidState { ACTIVE, RETIRED, ACCEPTED, CANCELLED }

    enum FeeParam { BUYNOW_FEE, BID_FEE, MAKER_FEE, TAKER_FEE, ROYALTY_FEE, DEPOSIT }

    struct MarketData {
        uint256 listingDeposit;
        uint256 buyNowPrimaryFee;
        uint256 bidPrimaryFee;
        uint256 makerFee;
        uint256 takerFee;
        uint256 royaltyFee;
        uint256 ttl;
    }

    struct Bid {
        uint256 id; // track bid id internally so can use in internal funitions easily
        address payable bidder;
        uint256 amount; // bid amount
        uint256 fee; // calculated takerFee for this bid amount
        BidState state;
        // escrowed amount is amount + fee
    }

    struct Item {
        IERC721 token;
        uint256 tokenId;
        address minter; // track the item minter for royalties, if there is one
    }

    struct ItemData {
        bool listed;
        bool active;
    }

    struct AuctionData {
        uint256 id; // track AuctionData id inside of struct so cna pass the object to internal functions without having to lookup again
        address payable seller; // track seller of auction, creator of auction and owner of item
        Type auctionType; // track auction type BUYNOW, BID
        Item item; // track what item is for auction by token address and tokenId
        uint256 listingDeposit; // track the deposit given when created
        uint256 ttl; // Time To Live - amount of time before bidding can begin, creator can cancel before this timestamp
        uint256 safetyThreshold; // timestamp to pass before Manager could cancel auction
        uint256 startingBid; // for BUYNOW - is the exact price ACCEPTED, for BID - is the minimum price ACCEPTED
        State state; // track auction state OPEN, SOLD, CANCELLED
        Bid highBid; // track current high bid activeId, to avoid lookup costs
        uint256 bidCount; // used to assign a bid id to each bid and track total bids, starts at index 0
        mapping(uint256 => Bid) bids; // record of all bids fo this auction
    }

    struct BaseAuction {
        address seller; // track seller of auction, creator of auction and owner of item
        Type auctionType; // track auction type BUYNOW, BID
        Item auctionItem; // track what item is for auction by token address and tokenId
        uint256 listingDeposit; // track the deposit given when created
        uint256 ttl; // Time To Live - amount of time before bidding can begin, creator can cancel before this timestamp
        uint256 safetyThreshold; // timestamp to pass before Manager could cancel auction
        uint256 startingBid; // for BUYNOW - is the exact price ACCEPTED, for BID - is the minimum price ACCEPTED
        State state; // track auction state OPEN, SOLD, CANCELLED
        Bid highBid; // track current high bid activeId, to avoid lookup costs
        uint256 bidCount; // used to assign a bid id to each bid and track total bids, starts at index 0
    }

    // events
    event AuctionCreated(uint256 auctionId, address seller, address itemAddress, uint256 itemId, Type auctionType);
    event AuctionClosed(uint256 auctionId, State closedState);
    event MarketTTLUpdate(uint256 oldValue, uint256 newValue);
    event MarketFeeUpdate(FeeParam param, uint256 oldValue, uint256 newValue);
    event MarketFeesCollected(address collectingManager, uint256 amountCollected);
    event BidCreated(address bidder, uint256 auctionId, uint256 bidId, uint256 amount);
    event BidActivated(uint256 auctionId, uint256 bidId);
    event BidDeactivated(uint256 auctionId, uint256 bidId, BidState newBidState);
    event RoyaltyCollected(address beneficiary, uint256 amountCollected);

    function create( Type auctionType, IERC721 token, uint256 tokenId, uint256 startingBid) payable external;

    function bid(uint256 auctionId, uint256 amount) payable external;

    function cancelBid(uint256 auctionId, uint256 bidId) external;

    function accept(uint256 auctionId) external;

    function cancelAuction(uint256 auctionId) external;

    function collectRoyalties(INftERC721 token ) external;

    // returns all market parameter data
    function getMarketData() external view returns (MarketData memory);

    // returns the total number of auctions that have been run, used to iterate through _auctions map if needed
    function totalAuctions() external view returns (uint256);

    // checks if an item is listed in an active auction
    function isActive(address token, uint256 tokenId) external view returns (bool);

    // returns auction data by auction id
    function getAuction(uint256 auctionId) external view returns (BaseAuction memory);

    // returns the total number of bids by auctionId
    function totalBids(uint256 auctionId) external view returns (uint256);
    
    // returns the highest active bid for an auction by auction id
    function getHighBid(uint256 auctionId) external view returns (Bid memory);

    function getBid(uint256 auctionId, uint256 bidId) external view returns (Bid memory);

    // Manager only

    function setListingDeposit(uint256 newDeposit) external;

    function setMarketFee(FeeParam param, uint256 newFee) external;

    function setTTL(uint256 newTime) external;
    
    function calcFee(FeeParam param, uint256 base) external view returns (uint256);

    // gather fees
    function collectFees() external;

    function checkFeeBalance() external view returns (uint256);

    function checkRoyalty(address creator) external view returns (uint256);
}
