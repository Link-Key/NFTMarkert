// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;
pragma abicoder v2;

import "../interface/IERC721.sol";
import "../interface/INftERC721.sol";
import "../interface/INftMarket.sol";

import "../utils/SafeMath.sol";

import "../ERC721/ERC721Holder.sol";

import "../access/roles/ManagerRole.sol";

contract NftMarket is INftMarket, ERC721Holder, ManagerRole {
    using SafeMath for uint256;
    uint256 private constant SAFETY = 1209600; // 2 weeks
    uint256 private constant MAX_PERCENT = 10000; // 2 decimal precision for percentage (100.00%)
    uint256 private constant MAX_VALUE = 1157920892373161954235709850086879078532699846656405640394575840079131296; // = ((2^256)-1)/10000, since to avoid multiplication overflow we should satisfy X*10000<=(2^256-1)

    MarketData private _market;

    // auto incremeted to guarantee unique ID for all auctions
    uint256 private _auctionCount;

    // smaller set of ID tracking for active auctions, guaranteed unique but can grow or shrink
    uint256 private _activeCount;

    // map of auctionId to AuctionData, for lookup
    mapping(uint256 => AuctionData) private _auctions;

    mapping(address => mapping(uint256 => ItemData)) private _itemData; // track if item if in active auction


    uint256 public _feeBalance; // track the un-collected market fees

    mapping(address => uint256) private _royaltyBalances; // track un-collected royalties

    // constructor set intial market data
    constructor(MarketData memory marketData) public {
        require(marketData.buyNowPrimaryFee <= MAX_PERCENT , "NftMarket.constructor: INVALID_BUYNOW_FEE");
        require(marketData.bidPrimaryFee <= MAX_PERCENT , "NftMarket.constructor: INVALID_BID_FEE");
        require(marketData.makerFee <= MAX_PERCENT , "NftMarket.constructor: INVALID_MAKER_FEE");
        require(marketData.takerFee <= MAX_PERCENT , "NftMarket.constructor: INVALID_TAKER_FEE");
        require(marketData.royaltyFee <= MAX_PERCENT , "NftMarket.constructor: INVALID_ROYALTY_FEE");
        _market = marketData;         
    }

    // Marketplace public methods
    function create( Type auctionType, IERC721 token, uint256 tokenId, uint256 startingBid) payable external override {
        address owner = token.ownerOf(tokenId);
        require(token.isApprovedForAll(owner, address(this)), "NftMarket.create: NOT_APPROVED_OR_INVALID_TOKEN_ID");
        require(owner == _msgSender(), "NftMarket.create: NOT_OWNER");
        require(!isManager(_msgSender()), "NftMarket.create: IS_MANAGER"); // Manager Role cannot create Auctions
        // no zero value auctions
        require(startingBid > 0, "NftMarket.create: ZERO_STARTING_BID");
        // MAX_VALUE cannot be broken to avoid overflows
        require(startingBid <= MAX_VALUE, "NftMarket.create: INVALID_STARTING_BID");
        // require the minimum listing deposit as msg.value
        require(msg.value == _market.listingDeposit, "NftMarket.create: INVALID_LISTING_DEPOSIT");
        
        Item memory item = Item(token, tokenId, address(0));

        if (token.supportsInterface(bytes4(keccak256("NFT_ERC721_INTERFACE")))) {
            address minter = INftERC721(address(token)).getMinter(tokenId);
            item.minter = minter;
        }

        // get current auction counts
        uint256 auctionId = _auctionCount;
 
        _auctions[auctionId].id = auctionId;
        _auctions[auctionId].seller = _msgSender();
        _auctions[auctionId].auctionType = auctionType;
        _auctions[auctionId].item = item;
        _auctions[auctionId].listingDeposit = msg.value;
        _auctions[auctionId].ttl = block.timestamp.add(_market.ttl);
        _auctions[auctionId].safetyThreshold = block.timestamp.add(SAFETY);
        _auctions[auctionId].startingBid = startingBid;
        _auctions[auctionId].state = State.OPEN;
        
        // update auctions id counter
        _auctionCount++;

        _itemData[address(token)][tokenId].active = true;

        // transferFrom the token to this contract (to lock it)
        token.transferFrom(_msgSender(), address(this), tokenId);

        emit AuctionCreated(auctionId, _msgSender(), address(item.token), item.tokenId, auctionType);
    }

    function bid(uint256 auctionId, uint256 amount) payable external override {
        AuctionData storage auction = _auctions[auctionId]; // get auction data
        require(auction.seller != address(0) && auction.state == State.OPEN , "NftMarket.bid: INVALID_AUCTION_STATE"); // auction must be open, the additional seller requirement is because an unset 0 index could still return true for the OPEN case alone
        require(msg.value > 0, "NftMarket.bid: ZERO_VALUE"); // shouldn't accept zero value bids (even if the auction creator has a zero value startingBid) we have logic dependent on it
        require(_msgSender() != auction.seller, "NftMarket.bid: INVALID_BIDDER");
        require(block.timestamp >= auction.ttl, "NftMarket.bid: TTL_ACTIVE");

        uint256 bidFee = _calcTakerFee(amount);
        require(amount.add(bidFee) == msg.value, "NftMarket.bid: INVALID_FEE_AMOUNT");

        // create bid
        Bid memory newBid = _createBid(auction, _msgSender(), amount, bidFee);

        if(auction.auctionType == Type.BUYNOW) { // new BUYNOW bids instantly ACTIVATED and settled
            require(amount == auction.startingBid, "NftMarket.bid: BID_AMOUNT_NOT_SATISFIED");
            _activateBid(auction, newBid);
            _settle(auction);
            emit AuctionClosed(auction.id, auction.state); 
        } else { // new BID bids set to ACTIVE, added to active maps, and adjust highBid and activeBids accordingly
            Bid memory highBid = getHighBid(auctionId); // curent highBid data (if there is any)
            if(highBid.bidder == address(0)) { // no bids so far, require bid amount gte startingBid
                require(amount >= auction.startingBid, "NftMarket.bid: START_BID_NOT_SATISFIED");
            } else { // previous high bid already, require bidAmount gt previous highBid amount
                require(amount > highBid.amount, "NftMarket.bid: BID_AMOUNT_TOO_LOW");
            }
            _activateBid(auction, newBid);
        }
    }

    function cancelBid(uint256 auctionId, uint256 bidId) external override {
        AuctionData storage auction = _auctions[auctionId]; // get auction data
        require(auction.state == State.OPEN && auction.seller != address(0), "NftMarket.bid: INVALID_STATE");
        require(_msgSender() == auction.highBid.bidder, "NftMarket.bid: NOT_BIDDER");
        require(bidId == auction.highBid.id, "NftMarket.bid: NOT_HIGH_BID");
        
        _deactivateBid(auction.id, auction.highBid, BidState.CANCELLED);

        // re-activate most recent RETIRED bid
        for( uint256 i = bidId.sub(1); i >= 0; i--) {
            if (auction.bids[i].state == BidState.RETIRED) {
                _auctions[auction.id].bids[i].state == BidState.ACTIVE;
                _auctions[auction.id].highBid = auction.bids[i];
                return;
            }
        }
    }

    function accept(uint256 auctionId) external override {
        AuctionData storage auction = _auctions[auctionId]; // get auction data
        require(_msgSender() == auction.seller, "NftMarket.accept: NOT_SELLER");
        require(auction.state == State.OPEN, "NftMarket.accept: INVALID_STATE");
        _settle(auction);
        emit AuctionClosed(auction.id, auction.state);
    }

    function cancelAuction(uint256 auctionId) external override { // only auction creator or manager (creator before TTL and after safetyThreshold, manager only after safteyTreshold)
        AuctionData storage auction = _auctions[auctionId]; // get auction data
        require(_msgSender() == auction.seller || isManager(_msgSender()), "NftMarket.cancelAuction: INVALID_CALLER");
        require(auction.state == State.OPEN && auction.seller != address(0), "NftMarket.cancelAuction: INVALID_STATE");
        if (isManager(_msgSender())) {
            require(block.timestamp > auction.safetyThreshold, "NftMarket.cancelAuction: SAFTEY_NOT_EXPIRED");
        }
        // deactivate highBid
        if(auction.highBid.bidder != address(0)) {
            _deactivateBid(auction.id, auction.highBid, BidState.CANCELLED);
        }

        // auction state advance to CANCELLED
        _auctions[auction.id].state = State.CANCELLED;
        delete _itemData[address(auction.item.token)][auction.item.tokenId].active;

        // transfer NFT back to seller
        _auctions[auction.id].item.token.transferFrom(address(this), auction.seller, auction.item.tokenId);

        emit AuctionClosed(auction.id, auction.state);
    }

    function collectRoyalties(INftERC721 token) external override {
        uint256 amount;
        // require(token.supportsInterface(bytes4(keccak256("NFT_ERC721_INTERFACE"))), "NftMarket.collectRoyalties: NOT_NFT_ERC721");
        address minter = token.beneficiaryFor(_msgSender());
        if (minter != address(0)) {
            amount = _royaltyBalances[minter];
            delete _royaltyBalances[minter];
        } else {
            amount = _royaltyBalances[_msgSender()];
        }
        require(amount > 0, "NftMarket.collectRoyalties: NO_ROYALTY");
        emit RoyaltyCollected(_msgSender(), amount);
        _msgSender().transfer(amount);
    }

    // Marketplace public getters

    // returns all market parameter data
    function getMarketData() external view override returns (MarketData memory) {
        return _market;
    }

    // returns the total number of auctions that have been run, used to iterate through _auctions map if needed
    function totalAuctions() external view override returns (uint256) {
        return _auctionCount;
    }

    function getAuction(uint256 auctionId) external view override returns (BaseAuction memory) {
        AuctionData storage auction = _auctions[auctionId];
        return BaseAuction(
            auction.seller,
            auction.auctionType, 
            auction.item, 
            auction.listingDeposit, 
            auction.ttl, 
            auction.safetyThreshold,
            auction.startingBid,
            auction.state,
            auction.highBid,
            auction.bidCount
        );
    }

    // checks if an item is listed in an active auction
    function isActive(address token, uint256 tokenId) public view override returns (bool) {
        return  _itemData[address(token)][tokenId].active;
    }

    // returns the total number of bids by auctionId
    function totalBids(uint256 auctionId) external view override returns (uint256) {
        return _auctions[auctionId].bidCount;
    }
    
    // returns the highest active bid for an auction by auction id
    function getHighBid(uint256 auctionId) public view override returns (Bid memory) {
        return _auctions[auctionId].highBid;
    }

    function getBid(uint256 auctionId, uint256 bidId) external view override returns (Bid memory) {
        return _auctions[auctionId].bids[bidId];
    }

    // enum FeeParam { BUYNOW_FEE, BID_FEE, MAKER_FEE, TAKER_FEE, ROYALTY_FEE, DEPOSIT }
    function calcFee(FeeParam param, uint256 base) external view override returns (uint256) {
        require(uint8(param) < uint8(FeeParam.DEPOSIT), "NftMarket.setMarketFee: INVALID_FEE_PARAM");
        uint256 fee;
        if (param == FeeParam.BUYNOW_FEE) {
             fee = _calcPrimaryFee(base, Type.BUYNOW);
        } else if (param == FeeParam.BID_FEE) {
            fee = _calcPrimaryFee(base, Type.BID);
        } else if (param == FeeParam.MAKER_FEE) {
            fee = base.mul(_market.makerFee).div(MAX_PERCENT);
        } else if (param == FeeParam.TAKER_FEE) {
            fee = _calcTakerFee(base);
        } else if (param == FeeParam.ROYALTY_FEE) {
            fee = _calcRoyaltyFee(base);
        }
        return fee;
    }

    function checkFeeBalance() external view override returns (uint256) {
        return _feeBalance;
    }

    function checkRoyalty(address creator) external view override returns (uint256) {
        return _royaltyBalances[creator];
    }

    // Manager only
    // system param setters

    function setListingDeposit(uint256 newDeposit) external override onlyManager {
        uint256 oldDeposit = _market.listingDeposit;
        _market.listingDeposit = newDeposit;
        emit MarketFeeUpdate(FeeParam.DEPOSIT, oldDeposit, newDeposit);
    }

    function setMarketFee(FeeParam param, uint256 newFee) external override onlyManager {
        require(uint8(param) < uint8(FeeParam.DEPOSIT), "NftMarket.setMarketFee: INVALID_FEE_PARAM");
        require(newFee <= MAX_PERCENT , "NftMarket.setMarketFee: INVALID_FEE");
        uint256 oldFee;
        if (param == FeeParam.BUYNOW_FEE) {
             oldFee = _market.buyNowPrimaryFee;
            _market.buyNowPrimaryFee = newFee;
        } else if (param == FeeParam.BID_FEE) {
            oldFee = _market.bidPrimaryFee;
            _market.bidPrimaryFee = newFee;
        } else if (param == FeeParam.MAKER_FEE) {
            oldFee = _market.makerFee;
            _market.makerFee = newFee;
        } else if (param == FeeParam.TAKER_FEE) {
            oldFee = _market.takerFee;
            _market.takerFee = newFee;
        } else if (param == FeeParam.ROYALTY_FEE) {
            oldFee = _market.royaltyFee;
            _market.royaltyFee = newFee;
        }
        emit MarketFeeUpdate(param, oldFee, newFee);
    }

    function setTTL(uint256 newTime) external override onlyManager {
        require(newTime < SAFETY, "NftMarket.setTTL: INVALID_TIME");
        uint256 oldTime;
        oldTime = _market.ttl;
        _market.ttl = newTime;
        emit MarketTTLUpdate(oldTime, newTime);
    }
    
    // gather fees
    function collectFees() external override onlyManager {
        uint256 amount = _feeBalance;
        require(amount > 0, "NftMarket.collectFees: NO_FEES");
        _feeBalance = 0;
        _msgSender().transfer(amount);
        emit MarketFeesCollected(_msgSender(), amount);
    }

    function _isOwner(address tokenAddress, uint256 tokenId) internal view {
        IERC721 erc721 = IERC721(tokenAddress);
        require(erc721.ownerOf(tokenId) == _msgSender(), "NftMarket._isOwner: NOT_OWNER");
    }

    // internal settlement
    function _settle(AuctionData storage auction) internal {
        // _deactivate highBid to ACCEPTED
        _deactivateBid(auction.id, auction.highBid, BidState.ACCEPTED);
        // auction state advance to SOLD
        _auctions[auction.id].state = State.SOLD;

        uint256 fee;
        // calculate maker fees and add the takerfee (for total fee)
        fee = _calcMakerFee(auction).add(auction.highBid.fee);

        // mark this item as listed (for future makerFee calculation)
        if (_itemData[address(auction.item.token)][auction.item.tokenId].listed == false) {
            _itemData[address(auction.item.token)][auction.item.tokenId].listed = true;
        }
        
        uint256 royalty;
        // calculate royalty
        if (auction.item.minter != address(0)) {
            royalty = _calcRoyaltyFee(fee);
        }
        
        // transfer fee to marketplace (increase fee balance)
        _feeBalance = _feeBalance.add(fee).sub(royalty);
        
        // transfer royalty to creator (increase royalty balance)
        if (royalty > 0) {
            _royaltyBalances[auction.item.minter] = _royaltyBalances[auction.item.minter].add(royalty);
        }
        
        delete _itemData[address(auction.item.token)][auction.item.tokenId].active;
        
        // transfer NFT to bidder (actual transfer)
        auction.item.token.transferFrom(address(this), auction.highBid.bidder, auction.item.tokenId);
        
        // transfer remaining ETH balance to seller (actual transfer)
        auction.seller.transfer(auction.highBid.amount.add(auction.highBid.fee).add(auction.listingDeposit).sub(fee));
    }

    // internal fee helpers
    function _calcTakerFee(uint256 bidAmount) internal view returns (uint256) {
        return bidAmount.mul(_market.takerFee).div(MAX_PERCENT);
    }

    function _calcMakerFee(AuctionData storage auction) internal view returns (uint256) {
        uint256 fee;
        // if this is a BID auction, then fee = primary bid fee
        // or if this is the first BUYNOW listing, then fee = primary buy now fee
        if (auction.auctionType == Type.BID || !_itemData[address(auction.item.token)][auction.item.tokenId].listed) {
            fee = _calcPrimaryFee(auction.highBid.amount, auction.auctionType);
        } else { // else fee =  maker fee
            fee = auction.highBid.amount.mul(_market.makerFee).div(MAX_PERCENT);
        }  
        
        if (fee < auction.listingDeposit) { // if fee < deposit, then fee = deposit
            fee = auction.listingDeposit;
        }
        
        return fee;
    }

    function _calcPrimaryFee(uint256 amount, Type auctionType) internal view returns (uint256) {
        if(auctionType == Type.BID) {
            return amount.mul(_market.bidPrimaryFee).div(MAX_PERCENT);
        } else {
            return amount.mul(_market.buyNowPrimaryFee).div(MAX_PERCENT);
        }
    }

    function _calcRoyaltyFee(uint256 fee) internal view returns (uint256) {
        return fee.mul(_market.royaltyFee).div(MAX_PERCENT);
    }

    // internal bid management (defaults to RETIRED state)
    function _createBid(AuctionData storage auction, address payable bidder, uint256 bidAmount, uint256 bidFee) internal returns (Bid memory) {
        // require OPEN auction state
       require(auction.state == State.OPEN, "NftMarket._createBid: INVALID_AUCTION_STATE");

        uint256 bidId = auction.bidCount;
        auction.bidCount++;

        // create bid data
        Bid memory newBid = Bid(bidId, bidder, bidAmount, bidFee, BidState.RETIRED);

        // adjust bid map
        _auctions[auction.id].bids[newBid.id] = newBid;

        // BidCreated event
        emit BidCreated(bidder, auction.id, newBid.id, bidAmount);
        return (newBid);
    }

    function _activateBid(AuctionData storage auction, Bid memory activeBid) internal {
        // deactivate old highBid (if there is one)
        Bid memory oldBid = auction.highBid;
        if(oldBid.bidder != address(0)){
            _deactivateBid(auction.id, oldBid, BidState.RETIRED);
        }
        // activate new bid and make hgihBid
        _auctions[auction.id].bids[activeBid.id].state = BidState.ACTIVE;
        _auctions[auction.id].highBid = _auctions[auction.id].bids[activeBid.id];
        emit BidActivated(auction.id, activeBid.id);
    }

    function _deactivateBid(uint256 auctionId, Bid memory deactivateBid, BidState newBidState) internal {
        // require newState not ACTIVE
        require(newBidState != BidState.ACTIVE, "NftMarket._deactivateBid: INVALID_BID_STATE");
        require(deactivateBid.bidder != address(0) && deactivateBid.state == BidState.ACTIVE, "NftMarket._deactivateBid: NOT_ACTIVE");
        
        // deactivate
        _auctions[auctionId].bids[deactivateBid.id].state = newBidState;
        _auctions[auctionId].highBid.state = newBidState;
        emit BidDeactivated(auctionId, deactivateBid.id, newBidState);
        // send ETH funds back to bidder
        if (newBidState != BidState.ACCEPTED) {
            deactivateBid.bidder.transfer(deactivateBid.amount.add(deactivateBid.fee));
        }
    }

}