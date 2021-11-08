const { ZERO_ADDRESS, MAX_UINT256 } = require('./helpers/constants');
const { setUpUnitTest } = require('./helpers/setUpUnitTest');

const {
    BN,           // Big Number support
    constants,    // Common constants, like the zero address and largest integers
    expectEvent,  // Assertions for emitted events
    expectRevert, // Assertions for transactions that should fail
    time,
    } = require('@openzeppelin/test-helpers');

const NftERC721_ABI = require('../build/contracts/NftERC721.json').abi;

const name = "TEST NFT 0";
const symbol = "TNFT0";
const uri = 'https://s3.ap-northeast-2.amazonaws.com/nft.yamagata/1608269120318-0.jpg';
const maxSupply = new BN(3);

contract('NftMarket', function (accounts) {
    require('@openzeppelin/test-helpers/configure')({
        provider: web3.currentProvider,
    });

    const [manager, minter, beneficiary, seller, bidder, ...others] = accounts;

    const users = others.slice(0,);
    
    let factory;
    let market;
    let listingDeposit;
    let startingBid;

    beforeEach(async function () {
        const { instances } = await setUpUnitTest(accounts);

        factory = instances.NFTFactory;
        market = instances.NftMarket;
        erc721 = instances.NftERC721;
        test721 = instances.TestERC721;

        listingDeposit = web3.utils.toWei('0.001', 'ether'); // about .65 cents
        startingBid = web3.utils.toWei('1', 'ether');
    });

    // manager role
    describe('roles', function(){

        it('set the contract deployer as Manager role', async function () {
            (await market.isManager(manager)).should.be.equal(true);
        });

        it('set the Manager role', async function () {
            const { logs } = await market.addManager(users[0], { from: manager });

            (await market.isManager(users[0], { from: manager })).should.be.equal(true);

            expectEvent.inLogs(logs, 'ManagerAdded', {
                account: users[0],
            });
        });

        it('fails to set the Manager role if not called by a Manager', async function () {
            await expectRevert(market.addManager(users[0], { from: users[0] }), "ManageRole.onlyManager: NOT_MANAGER");
        });

        it('renounce the Manager role', async function () {
            await market.addManager(users[0], { from: manager });
            const { logs } = await market.renounceManager({ from: manager });

            (await market.isManager(manager, { from: manager })).should.be.equal(false);

            expectEvent.inLogs(logs, 'ManagerRemoved', {
                account: manager,
            });
        });

        it('fails to renounce the Manager role if there are no other Manager accounts', async function () {
            await expectRevert(market.renounceManager({ from: manager }), "Roles: there must be at least one account assigned to this role");
        });
    });

    // function create(Type auctionType, IERC721 token, uint256 tokenId, uint256 startingBid) payable external;
    describe('create', function(){
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
        });

        // reverts if token is not approved for the market
        // require( erc721.isApprovedForAll(owner, address(this)), "NftMarket._isApproved: NOT_APPROVED_OR_INVALID_TOKEN_ID");
        it('reverts if token is not approved for the market', async function () {
            await expectRevert(market.create(new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) }), "NftMarket.create: NOT_APPROVED_OR_INVALID_TOKEN_ID");
        });

        // reverts if caller is not owner
        // require( erc721.ownerOf(tokenId) == _msgSender(), "NftMarket._isOwner: NOT_OWNER");
        it('reverts if caller is not owner', async function () {
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await expectRevert(market.create(new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: minter, value: new BN(listingDeposit) }), "NftMarket.create: NOT_OWNER");
        });

        // reverts if manager is caller
        // require(!isManager(_msgSender()), "NftMarket.create: IS_MANAGER");
        it('reverts if caller is a manager', async function () {
            await erc721.transferFrom(seller, manager, new BN(0), {from: seller});
            await erc721.setApprovalForAll(market.address, true, { from: manager});
            await expectRevert(market.create(new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: manager, value: new BN(listingDeposit) }), "NftMarket.create: IS_MANAGER");
        });

        it('reverts for zero value', async function () {
            startingBid = new BN(0);
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await expectRevert(market.create(new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) }), "NftMarket.create: ZERO_STARTING_BID");
        });

        // reverts if value is too big
        // require(startingBid <= MAX_VALUE, "NftMarket.create: INVALID_STARTING_BID");
        it('reverts if value is too big', async function () {
            startingBid = MAX_UINT256;
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await expectRevert(market.create(new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) }), "NftMarket.create: INVALID_STARTING_BID");
        });

        // reverts if the listingDeposit is worng or not paid
        // require(msg.value == _market.listingDeposit, "NftMarket.create: INVALID_LISTING_DEPOSIT");
        it('reverts if the listingDeposit is wrong or not paid', async function () {
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await expectRevert(market.create(new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: seller }), "NftMarket.create: INVALID_LISTING_DEPOSIT");
        });

        // success
        // function create(type, nft, tokenId, startingBid) - success
        describe('create() success', function(){
        
            let log;
            let timestamp;
            beforeEach( async function () {
                await erc721.setApprovalForAll(market.address, true, { from: seller});
                log = await market.create(new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
                timestamp = await time.latest();
            });

            it('creates an auction entry with proper state', async function () {
                const auction = await market.getAuction(new BN(0));
                (auction[0]).should.be.equal(seller);
                (auction[1]).should.be.bignumber.equal(new BN(0));

                (auction[2][0]).should.be.equal(erc721.address);
                (auction[2][1]).should.be.bignumber.equal(new BN(0));
                // assigns creator if from our factory
                (auction[2][2]).should.be.equal(minter);

                (auction[3]).should.be.bignumber.equal(new BN(listingDeposit));
                (auction[4]).should.be.bignumber.equal(timestamp.add(new BN(180)));

                (auction[5]).should.be.bignumber.equal(timestamp.add(new BN(1209600)));
                (auction[6]).should.be.bignumber.equal(new BN(startingBid));
                (auction[7]).should.be.bignumber.equal(new BN(0));

                (auction[8][0]).should.be.bignumber.equal(new BN(0));
                (auction[8][1]).should.be.equal(ZERO_ADDRESS);
                (auction[8][2]).should.be.bignumber.equal(new BN(0));
                (auction[8][3]).should.be.bignumber.equal(new BN(0));
                (auction[8][4]).should.be.bignumber.equal(new BN(0));

                (auction[9]).should.be.bignumber.equal(new BN(0));
            });

            it('doesnt assign creator if independent ERC721 is used', async function () {
                await test721.mint(minter, uri, {from: minter});
                await test721.setApprovalForAll(market.address, true, { from: minter});
                await market.create( new BN(1), test721.address, new BN(0), startingBid, { from: minter, value: listingDeposit });

                const auction = await market.getAuction(new BN(1));

                (auction[2][2]).should.be.equal(ZERO_ADDRESS);

            });

            it('increments the number of auctions', async function () {
                (await market.totalAuctions()).should.be.bignumber.equal(new BN(1));
            });

            it('itransfers the NFT to the market address', async function () {
                (await erc721.ownerOf(new BN(0))).should.be.equal(market.address);
            });

           // event AuctionCreated(uint256 auctionId, address seller, address itemAddress, uint256 itemId, Type auctionType);
            it('produces a AuctionCreated event log', async function () {
                expectEvent.inLogs(log.logs, 'AuctionCreated', {
                    auctionId: new BN(0).toString(),
                    seller: seller,
                    itemAddress: erc721.address,
                    itemId: new BN(0).toString(),
                    auctionType: new BN(0).toString()
                });
            });

        });

    });
 
    // function cancelAuction(uint256 auctionId) external;
    describe('cancelAuction', function(){
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await market.create(new BN(1), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
        });

        // require(_msgSender() == auction.seller || isManager(_msgSender()), "NftMarket.cancelAuction: INVALID_CALLER");
        it('reverts if not called by seller or manager', async function () {
            await expectRevert(market.cancelAuction(new BN(0), { from: minter }), "NftMarket.cancelAuction: INVALID_CALLER");
        });

        // require(auction.state == State.OPEN && auction.seller != address(0), "NftMarket.cancelAuction: INVALID_STATE");
        it('reverts if not valid state', async function () {
            await time.increase(182);
            let fee = await market.calcFee(new BN(3), startingBid);
            let totalBid = new BN(startingBid).add(fee);
            await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            await market.accept(new BN(0), { from: seller});
            await expectRevert(market.cancelAuction(new BN(0), { from: seller }), "NftMarket.cancelAuction: INVALID_STATE");
        });

        // if (isManager(_msgSender())) {
        //     require(block.timestamp > auction.safetyThreshold, "NftMarket.cancelAuction: SAFTEY_NOT_EXPIRED");
        // }
        it('if manager called, reverts if SAFTEY has NOT expired', async function () {
            await time.increase(182);
            await expectRevert(market.cancelAuction(new BN(0), { from: manager }), "NftMarket.cancelAuction: SAFTEY_NOT_EXPIRED");
        });

        // success
        // function cancelAuction(auctionId) - success
        describe('cancelAuction() success', function(){
            let log;
            let fee;
            beforeEach( async function () {
                // call contract to calc fee given the bid amount, enum order for fee checking BUYNOW_FEE, BID_FEE, MAKER_FEE, TAKER_FEE, ROYALTY_FEE
                fee = await market.calcFee(new BN(3), startingBid);
                let totalBid = new BN(startingBid).add(fee);
                await time.increase(1209601);
                await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
                log = await market.cancelAuction(new BN(0), { from: manager });
            });
            
            // deactivate highBid
            it('deactivates the highBid', async function () {
                const bid = await market.getBid(new BN(0), new BN(0));
                (bid[0]).should.be.bignumber.equal(new BN(0));
                (bid[1]).should.be.equal(bidder);
                (bid[2]).should.be.bignumber.equal(new BN(startingBid));
                (bid[3]).should.be.bignumber.equal(new BN(fee));
                (bid[4]).should.be.bignumber.equal(new BN(3));
            });

            // auction state advance to CANCELLED
            it('advances the auction state to CANCELLED', async function () {
                const auction = await market.getAuction(new BN(0));
                (auction[7]).should.be.bignumber.equal(new BN(2));
            });

            // transfer NFT back to seller
            it('transfers the NFT item back to the seller', async function () {
                (await erc721.ownerOf(new BN(0))).should.be.equal(seller);
            });

           // event AuctionClosed(uint256 auctionId, State closedstate);
            it('produces a AuctionClosed event log', async function () {
                expectEvent.inLogs(log.logs, 'AuctionClosed', {
                    auctionId: new BN(0).toString(),
                    closedState: new BN(2).toString()
                });
            });

        });

    });

    // function bid(uint256 auctionId, uint256 amount) external;
    describe('bid', function(){
        let nftAddr;
        let nft;
        let totalBid;
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await market.create(new BN(1), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
            fee = await market.calcFee(new BN(3), startingBid);
            totalBid = new BN(startingBid).add(fee);
        });

        // require(msg.value > 0, "NftMarket.bid: ZERO_VALUE");
        it('reverts if the bid amount is zero', async function () {
            await time.increase(182);
            await expectRevert(market.bid(new BN(0), startingBid, { from: bidder }), "NftMarket.bid: ZERO_VALUE");
        });

        // require(_msgSender() != auction.seller, "NftMarket.bid: INVALID_BIDDER");
        it('reverts if bidder is the seller', async function () {
            await time.increase(182);
            await expectRevert(market.bid(new BN(0), startingBid, { from: seller, value: totalBid}), "NftMarket.bid: INVALID_BIDDER");
        });

        // require(auction.seller != address(0) && auction.state == State.OPEN , "NftMarket.bid: INVALID_AUCTION_STATE");
        it('reverts if auction is not OPEN', async function () {
            await time.increase(182);
            await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            await market.accept(new BN(0), { from: seller});
            await expectRevert(market.bid(new BN(0), new BN(startingBid), { from: bidder, value: totalBid}), "NftMarket.bid: INVALID_AUCTION_STATE");
        });

         // require(block.timestamp >= auction.ttl, "NftMarket.bid: TTL_ACTIVE");
        it('reverts if TTL NOT expired', async function () {
            await expectRevert(market.bid(new BN(0), startingBid, { from: bidder, value: totalBid}), "NftMarket.bid: TTL_ACTIVE");
        });

        // require(amount.add(bidFee) == msg.value, "NftMarket.bid: INVALID_FEE_AMOUNT");
        it('reverts if incorrect bid fee sent', async function () {
            await time.increase(182);
            await expectRevert(market.bid(new BN(0), startingBid, { from: bidder, value: totalBid.add(new BN(1))}), "NftMarket.bid: INVALID_FEE_AMOUNT");
        });

        it('reverts if BUYNOW and incorrect bid amount sent', async function () {
            fee = await market.calcFee(new BN(3), new BN(startingBid).add(new BN(1)));
            totalBid = new BN(startingBid).add(fee).add(new BN(1));
            await erc721.mint(seller, uri, {from: minter});
            // await erc721.setApprovalForAll(market.address, true, { from: seller});
            await market.create(new BN(0), erc721.address, new BN(1), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
            await time.increase(182);
            await expectRevert(market.bid(new BN(1), startingBid, { from: bidder, value: totalBid}), "NftMarket.bid: INVALID_FEE_AMOUNT");
        });

        it('reverts if BID and too low bid amount sent', async function () {
            await time.increase(182);
            await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            await expectRevert(market.bid(new BN(0), startingBid, { from: bidder, value: totalBid}), "NftMarket.bid: BID_AMOUNT_TOO_LOW");
        });

        // success
        // function bid(auctionId, amount) - success
        describe('bid() success', function(){
        
            let log;
            beforeEach( async function () {
                await time.increase(182);
                log = await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            });

            it('adds the auction item to the active items map', async function () {
                const active = await market.isActive(erc721.address, new BN(0)) ;
                (active).should.be.equal(true);
            });

            // increase the bidTotal
            it('increases the total number of bids', async function () {
                (await market.totalBids(new BN(0))).should.be.bignumber.equal(new BN(1));
            });

            // create a bid entry
            it('creates a bid entry', async function () {
                const bid = await market.getBid(new BN(0), new BN(0));
                (bid[0]).should.be.bignumber.equal(new BN(0));
                (bid[1]).should.be.equal(bidder);
                (bid[2]).should.be.bignumber.equal(new BN(startingBid));
                (bid[3]).should.be.bignumber.equal(new BN(fee));
                (bid[4]).should.be.bignumber.equal(new BN(0));
            });

            // activate bid
            it('activates the new bid', async function () {
                const highBid = await market.getHighBid(new BN(0));
                (highBid[0]).should.be.bignumber.equal(new BN(0));
            });

            it('deactivates the old high bid', async function () {
                fee = await market.calcFee(new BN(3), new BN(startingBid).mul(new BN(2)));
                totalBid = new BN(startingBid).mul(new BN(2)).add(fee);
                await market.bid(new BN(0), new BN(startingBid).mul(new BN(2)), { from: bidder, value: totalBid});
                const oldBid = await market.getBid(new BN(0), new BN(0));
                (oldBid[4]).should.be.bignumber.equal(new BN(1));
            });

            // if BUYNOW, settle
            it('if BUYNOW, it settles', async function () {
                await erc721.mint(seller, uri, {from: minter });
                await erc721.setApprovalForAll(market.address, true, { from: seller});
                await market.create(new BN(0), erc721.address, new BN(1), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
                await time.increase(182);
                await market.bid(new BN(1), startingBid, { from: bidder, value: totalBid});
                const auction = await market.getAuction(new BN(1));
                (auction[7]).should.be.bignumber.equal(new BN(1));
            });

           // event BidCreated(address bidder, uint256 auctionId, uint256 bidId, uint256 amount);
            it('produces a BidCreated event log', async function () {
                expectEvent.inLogs(log.logs, 'BidCreated', {
                    bidder: bidder,
                    auctionId: new BN(0).toString(),
                    bidId: new BN(0).toString(),
                    amount: startingBid
                });
            });

        });

    });


    // function cancelBid(uint256 auctionId, uint256 bidId) external;
    describe('cancelBid', function(){
 
        let totalBid;
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await market.create(new BN(1), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
            fee = await market.calcFee(new BN(3), startingBid);
            totalBid = new BN(startingBid).add(fee);
            await time.increase(182);
            await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            fee = await market.calcFee(new BN(3), new BN(startingBid).mul(new BN(2)));
            totalBid = new BN(startingBid).mul(new BN(2)).add(fee);
            await market.bid(new BN(0), new BN(startingBid).mul(new BN(2)), { from: bidder, value: totalBid});
        });

        // require(auction.state == State.OPEN && auction.seller != address(0), "NftMarket.bid: INVALID_STATE");
        it('reverts if not valid state', async function () {
            await market.accept(new BN(0), { from: seller});
            await expectRevert(market.cancelBid(new BN(0), new BN(1), { from: bidder }), "NftMarket.bid: INVALID_STATE");
        });

        // require(_msgSender() == auction.highBid.bidder, "NftMarket.bid: NOT_BIDDER");
        it('reverts if caller is not bidder', async function () {
            await expectRevert(market.cancelBid(new BN(0), new BN(1), { from: manager }), "NftMarket.bid: NOT_BIDDER");
        });

        // require(bidId == auction.highBid.id, "NftMarket.bid: NOT_HIGH_BID");
        it('reverts if the bid is not the high bid', async function () {
            await expectRevert(market.cancelBid(new BN(0), new BN(0), { from: bidder }), "NftMarket.bid: NOT_HIGH_BID");
        });

        // success
        // function cancelBid(auctionId,) - success
        describe('cancelBid() success', function(){
        
            let log;
            beforeEach( async function () {
                log = await market.cancelBid(new BN(0), new BN(1), { from: bidder })
            });

            // decativates the bid
            it('decativates the bid to CANCELLED', async function () {
                const bid = await market.getBid(new BN(0), new BN(1));
                (bid[4]).should.be.bignumber.equal(new BN(3));
            });

            // reactivates the old high bid if there is one
            it('deactivates the old highBid', async function () {
                const bid = await market.getBid(new BN(0), new BN(0));
                (bid[4]).should.be.bignumber.equal(new BN(1));
            });

           //  event BidDeactivated(uint256 auctionId, uint256 bidId, BidState newBidState);
            it('produces a BidDeactivated event log', async function () {
                expectEvent.inLogs(log.logs, 'BidDeactivated', {
                    auctionId: new BN(0).toString(),
                    bidId: new BN(1).toString(),
                    newBidState: new BN(3)
                });
            });

        });

    });

    // function accept(uint256 auctionId) external;
    describe('accept', function(){
        let totalBid;
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
            await erc721.setApprovalForAll(market.address, true, { from: seller});
            await market.create(new BN(1), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
            fee = await market.calcFee(new BN(3), startingBid);
            totalBid = new BN(startingBid).add(fee);
            await time.increase(182);
            await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            fee = await market.calcFee(new BN(3), new BN(startingBid).mul(new BN(2)));
            totalBid = new BN(startingBid).mul(new BN(2)).add(fee);
            await market.bid(new BN(0), new BN(startingBid).mul(new BN(2)), { from: bidder, value: totalBid});
        });

        // require(auction.state == State.OPEN, "NftMarket.accept: INVALID_STATE");
        it('reverts if not valid state', async function () {
            await market.accept(new BN(0), { from: seller});
            await expectRevert(market.accept(new BN(0), { from: seller}), "NftMarket.accept: INVALID_STATE");
        });

        // require(_msgSender() == auction.seller, "NftMarket.accept: NOT_SELLER");
        it('reverts if caller is not seller', async function () {
            await expectRevert(market.accept(new BN(0), { from: manager}), "NftMarket.accept: NOT_SELLER");
        });

        // success
        // function accept(auctionId) - success
        describe('accept() success', function(){
        
            let oldBalance;
            let log;
            beforeEach( async function () {
                oldBalance = await web3.eth.getBalance(seller);
                log = await market.accept(new BN(0), { from: seller });
            });

            // settles the auction
            it('settles the auction to SOLD', async function () {
                const auction = await market.getAuction(new BN(0));
                (auction[7]).should.be.bignumber.equal(new BN(1));
            });

            // decativates the bid to ACCEPTED
            it('decativates the high bid to ACCEPTED', async function () {
                const highBid = await market.getHighBid(new BN(0));
                (highBid[4]).should.be.bignumber.equal(new BN(2));
            });

            it('removes the auction item from active items map', async function () {
                const active = await market.isActive(erc721.address, new BN(0));
                (active).should.be.equal(false);
            });

            // allocate proper royalty fees
            it('allocates proper royalty fees', async function () {
                const calcPrimaryFee = await market.calcFee(new BN(1), new BN(startingBid).mul(new BN(2)));
                const makerTakerFee = fee.add(calcPrimaryFee);
                const calcRoyaltyFee = await market.calcFee(new BN(4), new BN(makerTakerFee));
                const royaltyBalance = await market.checkRoyalty(minter);
                (calcRoyaltyFee).should.be.bignumber.equal(royaltyBalance);
            });

            // allocates proper market fees
            it('allocates proper market fees for first sale (primary fees)', async function () {
                const calcPrimaryFee = await market.calcFee(new BN(1), new BN(startingBid).mul(new BN(2)));
                const makerTakerFee = fee.add(calcPrimaryFee);
                const calcRoyaltyFee = await market.calcFee(new BN(4), new BN(makerTakerFee));
                const marketFee = new BN(makerTakerFee).sub(new BN(calcRoyaltyFee));
                const feeBalance = await market.checkFeeBalance();
                (marketFee).should.be.bignumber.equal(feeBalance);
            });

            // properly account for BUYNOW primary sale
            it('properly accounts for a BUYNOW primary sale', async function () {
                await market.collectFees({from: manager});
                await market.collectRoyalties(erc721.address, {from: minter});

                await erc721.mint(seller, uri, {from: minter});
                await erc721.setApprovalForAll(market.address, true, { from: seller});
                await market.create(new BN(0), erc721.address, new BN(1), new BN(startingBid), {from: seller, value: new BN(listingDeposit) });
                
                fee = await market.calcFee(new BN(3), startingBid);
                totalBid = new BN(startingBid).add(fee);

                await time.increase(182);
                await market.bid(new BN(1), startingBid, { from: bidder, value: totalBid});
                const calcMakerFee = await market.calcFee(new BN(0), startingBid);
                const makerTakerFee = fee.add(calcMakerFee);
                const calcRoyaltyFee = await market.calcFee(new BN(4), new BN(makerTakerFee));
                const roylatyFee = await market.checkRoyalty(minter);
                const marketFee = new BN(makerTakerFee).sub(new BN(calcRoyaltyFee));
                const feeBalance = await market.checkFeeBalance();
                (marketFee).should.be.bignumber.equal(feeBalance);
            });
            
            // properly account for BUYNOW secondary sale
            it('properly accounts for a BUYNOW secondary sale', async function () {
                await market.collectFees( {from: manager});
                await market.collectRoyalties(erc721.address, {from: minter});

                await erc721.mint(bidder, uri, {from: minter});
                await erc721.setApprovalForAll(market.address, true, { from: bidder});
                await market.create(new BN(0), erc721.address, new BN(1), new BN(startingBid), {from: bidder, value: new BN(listingDeposit) });
                console.log(startingBid.toString());
                fee = await market.calcFee(new BN(3), startingBid);
                console.log(fee.toString());
                totalBid = new BN(startingBid).add(fee);
                await time.increase(182);
                await market.bid(new BN(1), startingBid, { from: seller, value: totalBid});
                const calcMakerFee = await market.calcFee(new BN(0), startingBid);
                const makerTakerFee = fee.add(calcMakerFee);
                console.log(makerTakerFee.toString());
                const calcRoyaltyFee = await market.calcFee(new BN(4), new BN(makerTakerFee));
                console.log(calcRoyaltyFee.toString());
                const marketFee = new BN(makerTakerFee).sub(new BN(calcRoyaltyFee));
                console.log(marketFee.toString());
                const feeBalance = await market.checkFeeBalance();
                console.log(feeBalance.toString());
                (marketFee).should.be.bignumber.equal(feeBalance);
            });

            // transfer proper ETH amount to seller
            it('transfer proper ETH amount to seller', async function () {
                const balance = await web3.eth.getBalance(seller);

                const calcPrimaryFee = await market.calcFee(new BN(1), new BN(startingBid).mul(new BN(2)));
                const makerTakerFee = fee.add(calcPrimaryFee);
                const calcRoyaltyFee = await market.calcFee(new BN(4), new BN(makerTakerFee));
                const marketFee = new BN(makerTakerFee).sub(new BN(calcRoyaltyFee));
                const feeBalance = await market.checkFeeBalance();
                const sentAmount = new BN(startingBid).sub(calcPrimaryFee);
                const balanceMinusTxnFee = new BN(balance).sub(new BN(oldBalance));
                
                // const txnFee = new BN(1000000000000000000).sub(balanceMinusTxnFee.sub(sentAmount));
                // console.log(txnFee.toString());
                // TODO check this against gas consumption and gas price to be sure
                // (txnFee).should.be.bignumber.equal(calcTxnFee);
            });

           //  event AuctionClosed(uint256 auctionId, State closedState);
            it('produces a AuctionClosed event log', async function () {
                expectEvent.inLogs(log.logs, 'AuctionClosed', {
                    auctionId: new BN(0).toString(),
                    closedState: new BN(1)
                });
            });

        });

    });

    // unction collectRoyalties(INftERC721 token ) external;
    describe('collectRoyalties', function(){
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
            await erc721.setApprovalForAll(market.address, true, { from: seller});

            const listingDeposit = web3.utils.toWei('0.001', 'ether'); // about .65 cents
            const startingBid = web3.utils.toWei('1', 'ether');
            await market.create( new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: listingDeposit});

        });

        it('reverts if caller is not token minter or beneficiary', async function () {
            await time.increase(182);
            fee = await market.calcFee(new BN(3), startingBid);
            totalBid = new BN(startingBid).add(fee);
            await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            await expectRevert(market.collectRoyalties(erc721.address, {from: manager }), "NftMarket.collectRoyalties: NO_ROYALTY");
        });

        // success
        // function collectRoyalties(market) - success
        describe('collectRoyalties() success', function(){
        
            let log;
            let startingBid;
            let totalBid;
            let fee;
            beforeEach( async function () {
                startingBid = web3.utils.toWei('1', 'ether');
                // call contract to calc fee given the bid amount, enum order for fee checking BUYNOW_FEE, BID_FEE, MAKER_FEE, TAKER_FEE, ROYALTY_FEE
                fee = await market.calcFee(new BN(3), startingBid);
                totalBid = new BN(startingBid).add(fee);
                await time.increase(182);
                // auction 0, bid 0 (auto accepted for BUYNOW auction)
                await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
            });

            it('collects the royaties for an account', async function () {
                const oldBalance = await web3.eth.getBalance(minter);
                (await market.checkRoyalty(minter)).should.be.bignumber.greaterThan(new BN(0));
                log = await market.collectRoyalties(erc721.address, {from: minter });
                (await market.checkRoyalty(minter)).should.be.bignumber.equal(new BN(0));
            });

            // event RoyaltyCollected(address beneficiary, uint256 amountCollected);
            it('produces a RoyaltyCollected event log', async function () {
                expectEvent.inLogs(log.logs, 'RoyaltyCollected', {
                    beneficiary: minter,
                    amountCollected: fee.toString()
                });
            });

        });

    });

    // uint256 listingDeposit;
    // uint256 buyNowPrimaryFee;
    // uint256 bidPrimaryFee;
    // uint256 makerFee;
    // uint256 takerFee;
    // uint256 royaltyFee;
    // uint256 ttl;

    // function setListingDeposit(uint256 newDeposit) external;
    describe('setListingDeposit', function(){
        it('reverts if caller is not a manger', async function () {
            await expectRevert(market.setListingDeposit(new BN(0), { from: seller}), "ManageRole.onlyManager: NOT_MANAGER");
        });
        // success
        // function setListingDeposit(newDeposit) - success
        describe('setListingDeposit() success', function(){

            it('sets the listingDeposit', async function () {
                await market.setListingDeposit(new BN(0), { from: manager}); 
                const marketData = await market.getMarketData();
                (marketData[0]).should.be.bignumber.equal(new BN(0));
            });
        });
    });
    


    // setMarketFee(FeeParam param, uint256 newFee)
    describe('setMarketFee', function(){
        it('reverts if caller is not a manger', async function () {
            await expectRevert(market.setMarketFee(new BN(0), new BN(0), { from: seller}), "ManageRole.onlyManager: NOT_MANAGER");
        });

        // require(uint8(param) < uint8(FeeParam.DEPOSIT), "NftMarket.setMarketFee:INVALID_FEE_PARAM");
        it('reverts if fee param is deposit of large', async function () {
            await expectRevert(market.setMarketFee(new BN(5), new BN(0), { from: manager}), "NftMarket.setMarketFee: INVALID_FEE_PARAM");
        });

        // require(newFee <= MAX_PERCENT , "NftMarket.setBuyNowPrimaryFee: INVALID_FEE");
        it('reverts if fee is larger than the max percent value', async function () {
            await expectRevert(market.setMarketFee(new BN(0), new BN(10001),{ from: manager}), "NftMarket.setMarketFee: INVALID_FEE");
        });
        
        // success
        // setMarketFee(FeeParam param, uint256 newFee) - success
        describe('setMarketFee() success', function(){

            // BUYNOW_FEE, BID_FEE, MAKER_FEE, TAKER_FEE, ROYALTY_FEE
            it('sets the BUYNOW_FEE', async function () {
                await market.setMarketFee(new BN(0), new BN(0), { from: manager}); 
                const marketData = await market.getMarketData();
                (marketData[1]).should.be.bignumber.equal(new BN(0));
            });

            it('sets the BID_FEE', async function () {
                await market.setMarketFee(new BN(1), new BN(0), { from: manager}); 
                const marketData = await market.getMarketData();
                (marketData[2]).should.be.bignumber.equal(new BN(0));
            });

            it('sets the MAKER_FEE', async function () {
                await market.setMarketFee(new BN(2), new BN(0), { from: manager}); 
                const marketData = await market.getMarketData();
                (marketData[3]).should.be.bignumber.equal(new BN(0));
            });

            it('sets the TAKER_FEE', async function () {
                await market.setMarketFee(new BN(3), new BN(0), { from: manager}); 
                const marketData = await market.getMarketData();
                (marketData[4]).should.be.bignumber.equal(new BN(0));
            });

            it('sets the ROYALTY_FEE', async function () {
                await market.setMarketFee(new BN(4), new BN(0), { from: manager}); 
                const marketData = await market.getMarketData();
                (marketData[5]).should.be.bignumber.equal(new BN(0));
            });
        });
    });

    // revert if not manager
    // function setTTL(uint256 newTime) external;
    describe('setTTL', function(){
        it('reverts if caller is not a manger', async function () {
            await expectRevert(market.setTTL(new BN(0), { from: seller}), "ManageRole.onlyManager: NOT_MANAGER");
        });

        it('reverts if TTL is as large or lareger than the SAFETY number', async function () {
            await expectRevert(market.setTTL(new BN(1209600), { from: manager}), "NftMarket.setTTL: INVALID_TIME");
        });

        // success
        // function setListingDeposit(newDeposit) - success
        describe('setTTL() success', function(){
            it('sets the TTL', async function () {
                await market.setTTL(new BN(0), { from: manager})
                const marketData = await market.getMarketData();
                (marketData[6]).should.be.bignumber.equal(new BN(0));
            });
        });
    });
    
    // revert if not manager, correct amount sent
    // function collectFees() external;
    describe('collectFees', function(){
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
            await erc721.setApprovalForAll(market.address, true, { from: seller});

            const listingDeposit = web3.utils.toWei('0.001', 'ether'); // about .65 cents
            const startingBid = web3.utils.toWei('1', 'ether');
            await market.create( new BN(0), erc721.address, new BN(0), new BN(startingBid), {from: seller, value: listingDeposit});
            let fee = await market.calcFee(new BN(3), startingBid);
            let totalBid = new BN(startingBid).add(fee);
            await time.increase(182);
            // auction 0, bid 0 (auto accepted for BUYNOW auction)
            await market.bid(new BN(0), startingBid, { from: bidder, value: totalBid});
        });

        it('reverts if caller is not a manger', async function () {
            await expectRevert(market.collectFees({ from: seller}), "ManageRole.onlyManager: NOT_MANAGER");
        });

        describe('collectFees() success', function(){
            let feeBalance;
            let log;
            // TODO - success case
            it('collects the fees for a manager', async function () {
                feeBalance = await await market.checkFeeBalance();
                (await market.checkFeeBalance()).should.be.bignumber.greaterThan(new BN(0));
                log = await market.collectFees({from: manager});
                (await market.checkFeeBalance()).should.be.bignumber.equal(new BN(0));
            });

            // event MarketFeesCollected(address collectingManager, uint256 amountCollected);
            it('produces a MarketFeesCollected event log', async function () {
                expectEvent.inLogs(log.logs, 'MarketFeesCollected', {
                    collectingManager: manager,
                    amountCollected: feeBalance.toString()
                });
            });
        });
    });

});

