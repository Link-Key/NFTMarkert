const { ZERO_ADDRESS } = require('./helpers/constants');
const { setUpUnitTest } = require('./helpers/setUpUnitTest');

const {
    BN,           // Big Number support
    constants,    // Common constants, like the zero address and largest integers
    expectEvent,  // Assertions for emitted events
    expectRevert, // Assertions for transactions that should fail
    time,
    } = require('@openzeppelin/test-helpers');

const uri = 'https://s3.ap-northeast-2.amazonaws.com/nft.yamagata/1608269120318-0.jpg';
const uri2 = 'https://s3.ap-northeast-2.amazonaws.com/nft.yamagata/1608269145023-1.jpg';

contract('NftERC721', function (accounts) {
    require('@openzeppelin/test-helpers/configure')({
        provider: web3.currentProvider,
    });

    const [manager, minter, beneficiary, seller, bidder, ...others] = accounts;

    console.log('seller=',seller);
    console.log('minter=',minter);

    const users = others.slice(0,);

    let market;
    let erc721;

    beforeEach(async function () {
        const { instances } = await setUpUnitTest(accounts);
        market = instances.NftMarket;
        erc721 = instances.NftERC721;
    });

    // beneficiary roles
    describe('roles', function(){

        it('fails to set the Beneficiary role if not called by a Beneficiary', async function () {
            await expectRevert(erc721.addBeneficiary(users[0], { from: users[0] }), "BeneficiaryRole.onlyBeneficiary: NOT_BENEFICIARY");
        });

        it('fails to renounce the Beneficiary role if there are no other Beneficiary accounts for that minter', async function () {
            await expectRevert(erc721.renounceBeneficiary({ from: manager }), "BeneficiaryRole.removeBeneficiary: MIN_BENEFICIARIES");
        });

        it('sets a token minter as a Beneficiary role', async function () {
            await erc721.mint(minter, uri, {from: minter});
            (await erc721.isBeneficiary(minter)).should.be.equal(true);
        });

        it('set the Beneficiary role', async function () {
            await erc721.mint(minter, uri, {from: minter});
            const { logs } = await erc721.addBeneficiary(beneficiary, { from: minter });

            (await erc721.isBeneficiary(beneficiary)).should.be.equal(true);

            expectEvent.inLogs(logs, 'BeneficiaryAdded', {
                account: beneficiary,
            });
        });

        it('renounce the Beneficiary role', async function () {
            await erc721.mint(minter, uri, {from: minter});
            await erc721.addBeneficiary(beneficiary, { from: minter });
            const { logs } = await erc721.renounceBeneficiary({ from: minter });

            (await erc721.isBeneficiary(minter)).should.be.equal(false);

            expectEvent.inLogs(logs, 'BeneficiaryRemoved', {
                account: minter,
            });
        });

    });

    // mint
    describe('mint', function(){

        // function mint(address receiver, string memory uri) - success
        describe('mint() success', function(){

            let log;
            beforeEach(async function () {
                log = await erc721.mint(seller, uri, {from: minter});
            });
            
            it('adds minter to beneficiay list (if not already)', async function () {
                await erc721.mint(minter, uri, {from: minter});
                (await erc721.isBeneficiary(minter)).should.be.equal(true);
            });
            
            it('creates a new token', async function () {
                (await erc721.totalSupply()).should.be.bignumber.equal(new BN(1));
            });

            it('assigns minter address as the token minter', async function () {
                (await erc721.getMinter(new BN(0))).should.be.equal(minter);
            });

            it('issues the minted token to the correct receiver', async function () {
                (await erc721.ownerOf(new BN(0))).should.be.equal(seller);
            });

            it('assigns the correct URI to the minted token', async function () {
                // tokenURI(uint256 tokenId)
                (await erc721.tokenURI(new BN(0))).should.be.equal(uri);
            });

            // event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
            it('produces a Transfer event log', async function () {
                expectEvent.inLogs(log.logs, 'Transfer', {
                    from: ZERO_ADDRESS,
                    to: seller,
                    tokenId: new BN(0).toString(),
                });
            });
        });
    });

    // function requestUpdateTokenMetadata(uint256 tokenId, string memory uri) external;
    describe('requestUpdateTokenMetadata', function(){

        beforeEach(async function () {
            await erc721.mint(minter, uri, {from: minter});
        });

        // NftERC721.onlyMinterOrBeneficiary: NOT_MINTER_OR_BENEFICIARY
        it('reverts if caller is not token minter or a beneficiary', async function () {
            await expectRevert(erc721.requestUpdateTokenMetadata(new BN(0), uri2, {from: manager }), "NftERC721.onlyMinterOrBeneficiary: NOT_MINTER_OR_BENEFICIARY");
        });

        // require(bytes(newUri).length != 0, "NftERC721.approveUpdateTokenMetadata: NO_URI_UPDATE");  
        it('reverts if the uri is empty', async function () {
            await expectRevert(erc721.requestUpdateTokenMetadata(new BN(0), "", {from: minter }), "NftERC721.approveUpdateTokenMetadata: NO_URI_UPDATE");
        });

        // success
        // function requestUpdateTokenMetadata(tokenId, uri) - success
        describe('requestUpdateTokenMetadata() success', function(){
        
            let log;
            beforeEach(async function () {
                log = await erc721.requestUpdateTokenMetadata(new BN(0), uri2, {from: minter });
            });

            it('allows beneficiary to call', async function () {
                await erc721.addBeneficiary(beneficiary, { from: minter });
                await erc721.requestUpdateTokenMetadata(new BN(0), uri2, {from: beneficiary });
            });

            it('assigns the correct URI to be requested', async function () {
                // getUpdate(uint256 tokenId)
                (await erc721.getUpdate(new BN(0))).should.be.equal(uri2);
            });

            // log event TokenURIUpdateRequest(uint256 indexed tokenId, string uri);
            it('produces a TokenURIUpdateRequest event log', async function () {
                expectEvent.inLogs(log.logs, 'TokenURIUpdateRequest', {
                    tokenId: new BN(0).toString(),
                    uri: uri2,
                });
            });
        });
    });

    describe('approveUpdateTokenMetadata', function() {
        beforeEach(async function () {
            await erc721.mint(seller, uri, {from: minter});
            await erc721.requestUpdateTokenMetadata(new BN(0), uri2, {from: minter });
        });
        // revert if not token owner
        it('reverts if caller is not token owner', async function () {
            await expectRevert(erc721.approveUpdateTokenMetadata(new BN(0), {from: minter }), "NftERC721.onlyTokenOwner: NOT_OWNER");
        });

        // success
        // function approveUpdateTokenMetadata(tokenId) - success
        describe('approveUpdateTokenMetadata() success', function(){
        
            let log;
            beforeEach(async function () {
                log = await erc721.approveUpdateTokenMetadata(new BN(0), {from: seller });
            });

            // reset request uri
            it('resets the URI request', async function () {
                // getUpdate(uint256 tokenId)
                (await erc721.getUpdate(new BN(0))).should.be.equal("");
            });

            // set proper uri
            it('assigns the correct URI to token', async function () {
                // getUpdate(uint256 tokenId)
                (await erc721.tokenURI(new BN(0))).should.be.equal(uri2);
            });

            // log event TokenURIUpdate(uint256 indexed tokenId, string uri);
            it('produces a TokenURIUpdate event log', async function () {
                expectEvent.inLogs(log.logs, 'TokenURIUpdate', {
                    tokenId: new BN(0).toString(),
                    uri: uri2,
                });
            });

        });

    });

    // burn
    describe('burn', function(){
        beforeEach(async function () {
            await erc721.mint(minter, uri, {from: minter});
        });

        // this was already tested and accounted in NFTFactory
        it('reverts if no token ', async function () {
            await expectRevert(erc721.burn(new BN(1), {from: minter }), "ERC721: owner query for nonexistent token");
        });
        // this was already tested and accounted in NFTFactory
        it('reverts if not called by token owner', async function () {
            await expectRevert(erc721.burn(new BN(0), {from: seller }), "NftERC721.onlyTokenOwner: NOT_OWNER");
        });

        // success
        // function collectRoyalties(market) - success
        describe('burn() success', function(){

            let log;
            beforeEach( async function () {
                log = await erc721.burn(new BN(0), {from: minter });
            });

            it('burns the token', async function () {
                (await erc721.totalSupply()).should.be.bignumber.equal(new BN(0));
            });

        });

    });

});