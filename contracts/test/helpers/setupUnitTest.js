const contractArtifacts = require('./contractArtifacts');
const { BN } = require('./setup');

const listingDeposit = web3.utils.toWei('0.001', 'ether'); // about .65 cents
const buyNowPrimaryFee = new BN('1000'); // 10%
const bidPrimaryFee = new BN('2000'); // 20%
const makerFee = new BN('250'); // 2.5%
const takerFee = new BN('250'); // 2.5%
const royaltyFee = new BN('2000'); // 20%
const ttl = new BN(180); // 3 minutes in seconds

async function setUpUnitTest (accounts) {
    const [manager, minter, beneficiary, seller, bidder, ...others] = accounts;

    const SafeMath = await contractArtifacts.SafeMath.new({ from: manager });
    const libs = {
        SafeMath: SafeMath.address,
    };

    let NftMarket = await contractArtifacts.NftMarket.new(
        [
            listingDeposit,
            buyNowPrimaryFee,
            bidPrimaryFee,
            makerFee,
            takerFee,
            royaltyFee,
            ttl
        ],
        { from: manager }
    );

        // // deploy erc721 independant of our factory ( no creator/royalty attached)
    // await deployer.link(SafeMath, NftERC721);
    let NftERC721 = await contractArtifacts.NftERC721.new(
        'NFT ERC721', 
        'XNFT',
        { from: manager }
    );

    let TestERC721 = await contractArtifacts.TestERC721.new(
        'INDEPENDENT ERC721', 
        'INFT',
        { from: manager }
    );

    const contracts = {
        NftMarket: NftMarket,
        NftERC721: NftERC721,
        TestERC721: TestERC721,
    };
    return { instances: contracts };
}

module.exports = {
  setUpUnitTest,
};