pragma solidity ^0.7.0;
import "./ERC721.sol";
import "./Ownable.sol";


/**
 * @title LinkKey INO contract
 * @dev Extends ERC721 Non-Fungible Token Standard basic implementation
 */
contract LinkKeyINO is ERC721, Ownable {
    using SafeMath for uint256;

    string public LINKKEY_PROVENANCE = "";

    uint public constant maxBatch = 20;

    uint public MAX_KEYS;

    constructor(string memory name, string memory symbol, uint256 maxNftSupply) ERC721(name, symbol) {
        MAX_KEYS = maxNftSupply;
    }

    modifier lockedPosition(){
        require(((balanceOf(owner()) < 1) && (totalSupply() == MAX_KEYS)) || _msgSender() == owner() || isApprovedForAll(owner(), _msgSender()), "token can not transfer before lock position.");
        _;
    }

    /*
    * Set provenance once it's calculated
    */
    function setProvenanceHash(string memory provenanceHash) public onlyOwner {
        LINKKEY_PROVENANCE = provenanceHash;
    }

    function setBaseURI(string memory baseURI) public onlyOwner {
        _setBaseURI(baseURI);
    }

    function setTokenURI(string memory tokenURI, uint256 tokenId) public onlyOwner {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "transfer caller is not owner nor approved");
        _setTokenURI(tokenId, tokenURI);
    }

    /**
    * Mints Link Key Token
    */
    function mintKey(uint numberOfTokens) public onlyOwner {
        require(numberOfTokens <= maxBatch, "Can only mint 20 tokens at a time");
        require(totalSupply().add(numberOfTokens) <= MAX_KEYS, "Mint number would exceed max supply of LinkKey");

        for(uint i = 0; i < numberOfTokens; i++) {
            uint mintIndex = totalSupply().add(1);
            if (totalSupply() < MAX_KEYS) {
                _safeMint(msg.sender, mintIndex);
            }
        }
    }

    /**
     * @dev See {ERC721-approve}.
     */
    function approve(address to, uint256 tokenId) public virtual override lockedPosition {
        super.approve(to, tokenId);
    }

    /**
     * @dev See {ERC721-setApprovalForAll}.
     */
    function setApprovalForAll(address operator, bool approved) public virtual override lockedPosition{
        super.setApprovalForAll(operator, approved);
    }

    /**
     * @dev See {ERC721-transferFrom}.
     */
    function transferFrom(address from, address to, uint256 tokenId) public virtual override lockedPosition{
        super.transferFrom(from, to, tokenId);
    }

    /**
     * @dev See {ERC721-safeTransferFrom}.
     */
    function safeTransferFrom(address from, address to, uint256 tokenId) public virtual override lockedPosition{
        super.safeTransferFrom(from, to, tokenId);
    }

    /**
     * @dev See {ERC721-safeTransferFrom}.
     */
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory _data) public virtual override lockedPosition{
        super.safeTransferFrom(from, to, tokenId, _data);
    }
}