// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;

import "./ERC721.sol";

contract TestERC721 is ERC721 {
    event TokenURIUpdate(uint256 indexed tokenId, string uri);
    uint256 private _idCounter;

    modifier onlyTokenOwner(uint256 tokenId) {
        address owner = ownerOf(tokenId);
        require(owner == _msgSender(), "NftERC721.onlyTokenOwner: NOT_OWNER");
        _;
    }

    constructor(string memory name, string memory symbol) ERC721(name, symbol) public {}

    function mint(address receiver, string memory uri) external {
        uint256 newId = _idCounter;
        _idCounter++;
        _mint(receiver, newId);
        _setTokenURI(newId, uri);
        emit TokenURIUpdate(newId, uri);
    }

    function burn(uint256 tokenId) external onlyTokenOwner(tokenId) returns (bool) {
        _burn(tokenId);
        return true;
    }
}