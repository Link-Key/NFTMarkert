
require('dotenv').config();

const {
    SafeMath,
    NftMarket,
    NftERC721,
    TestERC721
} = require('../test/helpers/contractArtifacts');

const { time } = require('@openzeppelin/test-helpers');

// var MyContract = artifacts.require("./MyContract.sol");

const { accountsData } = require('../test/helpers/accounts');

const constants = require('../test/helpers/constants');
const web3Utils = require('web3-utils');
const Web3 = require('web3');
// const web3 = new Web3('http://127.0.0.1:7545');
const web3 = new Web3(`https://ropsten.infura.io/v3/4a3ccc321c044cc69b9b2a4548af83b9`);
// const web3 = new Web3(`https://kovan.infura.io/v3/4a3ccc321c044cc69b9b2a4548af83b9`);

const BN = web3Utils.BN;

const listingDeposit = web3.utils.toWei('0.001', 'ether'); // about .65 cents
const buyNowPrimaryFee = new BN('1000'); // 10%
const bidPrimaryFee = new BN('2000'); // 20%
const makerFee = new BN('250'); // 2.5%
const takerFee = new BN('250'); // 2.5%
const royaltyFee = new BN('2000'); // 20%
const ttl = new BN(180); //3 min


const uri = 'https://s3.ap-northeast-2.amazonaws.com/nft.yamagata/1608269120318-0.jpg';
const uri2 = 'https://s3.ap-northeast-2.amazonaws.com/nft.yamagata/1608269145023-1.jpg';

module.exports = async function (deployer, network, accounts) {
    require('@openzeppelin/test-helpers/configure')({
        provider: deployer.provider,
    });
    const [manager, minter, beneficiary, seller, bidder, ...others] = accounts;

    const users = others.slice(0,);
    console.log('users=',users[0]);

    // await deployer.deploy(MyContract);

    // const accts = await accountsData(accounts.length);
    // deploy and link SafeMath
    // await deployer.deploy(SafeMath);
    // await deployer.link(SafeMath, NftMarket);

    // deploy NftMarket
    // await deployer.deploy(NftMarket,
    //     [
    //         listingDeposit,
    //         buyNowPrimaryFee,
    //         bidPrimaryFee,
    //         makerFee,
    //         takerFee,
    //         royaltyFee,
    //         ttl
    //     ]
    // );
    //
    // const market = await NftMarket.deployed();

    // console.log('market=',market);

    // console.log('market.address1=', market.address);

    // await deployer.link(SafeMath, NftERC721);
    // await deployer.deploy(NftERC721, 'NFT FULL NAME', 'NFT NAME', {from: manager});
    // const nft = await NftERC721.deployed();

    // console.log('minter=', minter);

    // // tokenId 0
    // await nft.mint(minter, uri, {from: minter});

    // // test get minter
    // console.log((await nft.getMinter(new BN(0))).toString());
    //
    // // // IERC721Enumerable
    // console.log('IERC721Enumerable:');
    // console.log((await nft.totalSupply()).toString());
    // console.log(await nft0.methods.tokenOfOwnerByIndex(creator, '0').call());
    // console.log(await nft0.methods.tokenByIndex('0').call());

    // // IERC721Metadata
    // console.log('IERC721Metadata:');
    // console.log(await nft.name());
    // console.log(await nft.symbol());
    // console.log(await nft.tokenURI(new BN(0)));
    //
    // // // IERC721
    // console.log('IERC721:');
    // console.log((await nft.balanceOf(minter)).toString());
    // console.log(minter);
    // console.log(await nft.ownerOf(new BN(0)));

    // MINT tokens for different states
    // tokenId 1
    // await nft.mint(
    //     minter,
    //     uri2,
    //     {from: minter}
    // );

    // tokenId 2
    // await nft.mint(
    //     minter,
    //     uri,
    //     {from: minter}
    // );
    //
    // // tokenId 3
    // await nft.mint(
    //     minter,
    //     uri2,
    //     {from: minter}
    // );
    //
    // // tokenId 4
    // await nft.mint(
    //     minter,
    //     uri,
    //     {from: minter}
    // );

    // fetch metadata link
    // console.log(await nft.tokenURI(new BN(1)));

    // test transferFrom and safeTransferFrom and give to seller
    // console.log('seller=', seller);
    // await nft.transferFrom(minter, seller, new BN(0), {from: minter});
    // await nft.safeTransferFrom(minter, seller, new BN(1), {from: minter});
    // await nft.safeTransferFrom(minter, seller, new BN(2), {from: minter});
    // await nft.safeTransferFrom(minter, seller, new BN(3), {from: minter});
    // await nft.safeTransferFrom(minter, seller, new BN(4), {from: minter});

    // verify seller is owner
    // console.log(seller);
    // console.log(await nft.ownerOf(new BN(0)));
    // console.log((await nft.balanceOf(seller)).toString());

    // request metadata update flow
    // no update requested
    // console.log(await nft.getUpdate(new BN(2)));
    // make request by creator
    // await nft.requestUpdateTokenMetadata(
    //     // new BN(2),
    //     uri2,
    //     {from: minter}
    // );
    // same uri
    // console.log(await nft.tokenURI(new BN(2)));
    // // lookup request
    // console.log(await nft.getUpdate(new BN(2)));
    //
    // // approval by owner
    // await nft.approveUpdateTokenMetadata(new BN(2), {from: seller});
    // // uri has changed
    // console.log(await nft.tokenURI(new BN(2)));

    // add another beneficiary for roylaty collection
    // await nft.addBeneficiary(
    //     beneficiary,
    //     {from: minter}
    // );

    // verify beneficiary is linked to creator account
    // console.log(await nft.beneficiaryFor(beneficiary, {from: beneficiary}));

    // remove beneficiary test
    // await nft.renounceBeneficiary(
    //     {from: beneficiary}
    // );

    // NFT Market
    // get basic market data

    // console.log('=======test all setters for market params===')
    //
    // console.log(await market.getMarketData());
    //
    // // test all setters for market params
    // await market.setListingDeposit(new BN(0), { from: manager });
    //
    // console.log(await market.getMarketData());
    //
    // await market.setMarketFee(new BN(0), new BN(0), { from: manager });
    //
    // console.log(await market.getMarketData());
    //
    // await market.setMarketFee(new BN(1), new BN(0), { from: manager });
    //
    // console.log(await market.getMarketData());
    //
    // await market.setMarketFee(new BN(2), new BN(0), { from: manager });
    //
    // console.log(await market.getMarketData());
    //
    // await market.setMarketFee(new BN(3), new BN(0), { from: manager });
    //
    // console.log(await market.getMarketData());
    //
    // await market.setMarketFee(new BN(4), new BN(0), { from: manager });
    //
    // console.log(await market.getMarketData());
    //
    //
    // // verify no auctions yet
    // console.log((await market.totalAuctions()).toString());
    //
    // // set market as operator
    // await nft.setApprovalForAll(market.address, true, { from: seller});
    //
    // // verfiy approval
    // console.log(await nft.isApprovedForAll(seller, market.address));
    //
    // // create auction 0, end state - BUYNOW, OPEN state (no bids), NFT0, tokenId 0 held in market
    // const startingBid = web3.utils.toWei('209', 'ether');
    //
    // console.log('listingDeposit=', listingDeposit);
    //
    // console.log('new BN(0)', new BN(0));
    //
    // console.log('nft.address', nft.address);
    //
    // console.log('startingBid', startingBid);
    //
    // console.log('seller', seller);
    //
    // await market.create( new BN(0), nft.address, new BN(0), startingBid, { from: seller, value: listingDeposit });
    // // verify auction 0 data
    // console.log(await market.getAuction(new BN(0)));
    // // verify market is owner
    // console.log(market.address);
    // console.log(await nft.ownerOf(new BN(0)));
    //
    // // create auction 1, end state - BUYNOW, SOLD, bid 0, NFT0, tokenId 1 sold to bidder
    // await market.create( new BN(0), nft.address, new BN(1), startingBid, { from: seller, value: listingDeposit });
    //
    // await time.increase(181);
    //
    // // check is active
    // console.log(await market.isActive(nft.address, new BN(1)));
    //
    // const amountWei = web3.utils.toWei(new BN(1));
    //
    // // call contract to calc fee given the bid amount, enum order for fee checking BUYNOW_FEE, BID_FEE, MAKER_FEE, TAKER_FEE, ROYALTY_FEE
    // const fee = await market.calcFee(new BN(3), amountWei);
    //
    // const totalBid = new BN(amountWei).add(fee);
    //
    // // auction 1, bid 0 (auto accepted for BUYNOW auction)
    // await market.bid(new BN(1), amountWei, { from: bidder, value: totalBid});
    //
    // // get auction 1 data, confirmed SOLD and highBid ACCEPTED
    // console.log(await market.getAuction(new BN(1)));
    // // verify bidder is owner
    // console.log(bidder);
    // console.log(await nft.ownerOf(new BN(1)));
    //
    // // create auction 2, end state - BUYNOW, CANCELLED, no bids, NFT0, tokenId 2 returned to seller
    // await market.create( new BN(0), nft.address, new BN(2), startingBid, { from: seller, value: listingDeposit });
    //
    // // cancel by seller before TTL
    // await market.cancelAuction(new BN(2), { from: seller});
    // // verify auction 2 data, CANCELLED, no bids
    // console.log(await market.getAuction(new BN(2)));
    // // verify seller is again owner
    // console.log(seller);
    // console.log(await nft.ownerOf(new BN(2)));
    //
    // // create auction 3, end state - BID, CANCELLED, bid 0 RETIRED, bid 1 CANCELLED, NFT0, tokenId 3 returned to seller
    // await market.create( new BN(1), nft.address, new BN(3), startingBid, { from: seller, value: listingDeposit });
    //
    // console.log("Increase time by 181 sec to expire the TTL so bids can occur...");
    // await time.increase(181);
    //
    // // auction 3, bid 0
    // await market.bid(new BN(3), amountWei, { from: bidder, value: totalBid});
    //
    // // verify bid 0 state ACTIVE
    // console.log(await market.getBid(new BN(3), new BN(0)));
    // // also verify it is highBid
    // console.log(await market.getAuction(new BN(3)));
    //
    // // auction 3, bid 1
    // const amountWei2 = web3.utils.toWei(new BN(2));
    // const fee2 = await market.calcFee(new BN(3), amountWei2);
    // //console.log(fee.toString());
    // const totalBid2 = new BN(amountWei2).add(fee2);
    // await market.bid(new BN(3), amountWei2, { from: users[0], value: totalBid2});
    //
    // // verify bid 0 state RETIRED
    // console.log(await market.getBid(new BN(3), new BN(0)));
    //
    // // verify bid 1 state ACTIVE
    // console.log(await market.getBid(new BN(3), new BN(1)));
    // // also verify bid 1 is new highBid
    // console.log(await market.getAuction(new BN(3)));
    // // can also very ETH back to bidder for bid 0
    //
    //
    // // advance timestamp beyond the safetyThreshold, so manager can cancel
    // const duration = new BN(1296000); // 15 days into the future!
    // await time.increase(duration);
    //
    // // cancel auction 3
    // await market.cancelAuction(new BN(3), { from: manager});
    // // verify bid 1 state CANCELLED
    // console.log(await market.getBid(new BN(3), new BN(1)));
    // // also verify auction 3 is CANCELLED
    // console.log(await market.getAuction(new BN(3)));
    // // verify seller is again owner of tokenId 3
    // console.log(seller);
    // console.log(await nft.ownerOf(new BN(3)));
    // // can also very ETH back to users[0] for bid 1
    //
    //
    // // create auction 4, end state - BID, ACCEPTED, bid 0 ACCEPTED, NFT0, tokenId 4 sold to bidder
    // await market.create( new BN(1), nft.address, new BN(4), startingBid, { from: seller, value: listingDeposit });
    //
    // console.log("Increase time by 181 sec to expire the TTL so bids can occur...");
    // await time.increase(181);
    //
    // // auction 4, bid 0
    // await market.bid(new BN(4), amountWei, { from: bidder, value: totalBid});
    //
    // // verify bid 0 state ACTIVE
    // console.log(await market.getBid(new BN(4), new BN(0)));
    // // also verify it is highBid
    // console.log(await market.getAuction(new BN(4)));
    //
    // // seller accept bid 0
    // await market.accept(new BN(4), { from: seller });
    //
    // // verify bid 0 state ACCEPTED
    // console.log(await market.getBid(new BN(4), new BN(0)));
    // // also verify auction 4 state SOLD
    // console.log(await market.getAuction(new BN(4)));
    // // verify bidder is owner of tokenId 4
    // console.log(bidder);
    // console.log(await nft.ownerOf(new BN(4)));
    //
    //
    // // deploy erc721 independant of our factory ( no creator/royalty attached)
    // await deployer.link(SafeMath, TestERC721);
    // await deployer.deploy(TestERC721, 'INDEPENDANT ERC721', 'INFT', {from: users[0]});
    // const erc721 = await TestERC721.deployed();
    //
    // // independent tokenId 0
    // await erc721.mint(users[0], uri, {from: users[0]});
    //
    // // approve for use on market
    // await erc721.setApprovalForAll(market.address, true, { from: users[0]});
    //
    // // verfiy approval
    // console.log(await erc721.isApprovedForAll(users[0], market.address));
    //
    // // auction 5 end state - BID, OPEN, no bids, INFT, tokenId 0 held in market
    // await market.create( new BN(1), erc721.address, new BN(0), startingBid, { from: users[0], value: listingDeposit });
    //
    // // see no minter assigned
    // console.log(await market.getAuction(new BN(5)));
    //
    // // gather fees and royalties!
    //
    // // market has fees to collect
    // console.log((await market.checkFeeBalance()).toString());
    //
    // // manger collect fees
    // await market.collectFees({ from: manager });
    //
    // // no more fees to collect
    // console.log((await market.checkFeeBalance()).toString());
    //
    // // minteer has royalties to collect
    // console.log((await market.checkRoyalty(minter)).toString());
    //
    // // check balance before hand
    // console.log(await web3.eth.getBalance(beneficiary));
    // // beneficiary account collect royalties
    // await market.collectRoyalties(nft.address, { from: beneficiary });
    //
    // // check balances afterwards to confirm
    // console.log((await market.checkRoyalty(minter)).toString());
    // console.log(await web3.eth.getBalance(beneficiary));

}