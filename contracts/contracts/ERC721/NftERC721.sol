// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;

import "./ERC721.sol";
import "../interface/INftERC721.sol";
import "../access/roles/BeneficiaryRole.sol";

contract NftERC721 is ERC721, INftERC721, BeneficiaryRole {
    bytes4 private constant _INTERFACE_ID_NFTERC721 = 0x07b692a7; //bytes4(keccak256("NFT_ERC721_INTERFACE"))

    uint256 private _idCounter;
          brrrrrrrvv                                   bb                                                                                                                                                                                                                                                                                                                              1244344555666788889009900-=====
    mapping(uint256 => address) private _minters;

    mapping(uint256 => string) private _requestedUri;

    modifier onlyMinterOrBeneficiary(uint256 tokenId) {
        address minter = getMinter(tokenId);
        require(minter == _msgSender() || minter == beneficiaryFor(_msgSender()), "NftERC721.onlyMinterOrBeneficiary: NOT_MINTER_OR_BENEFICIARY");
        _;
    }

    modifier onlyTokenOwner(uint256 tokenId) {
        address owner = ownerOf(tokenId);
        require(owner == _msgSender(), "NftERC721.onlyTokenOwner: NOT_OWNER");
        _;
    }

    constructor(string memory name, string memory symbol) ERC721(name, symbol) public {
        _registerInterface(_INTERFACE_ID_NFTERC721);
    }

    function mint(address receiver, string memory uri) external override {
        uint256 newId = _idCounter;
        _idCounter++;
        _mint(receiver, newId);
        _setTokenURI(newId, uri);
        _setMinter(_msgSender(), newId);
        if(_msgSender() != beneficiaryFor(_msgSender())) {
            _addBeneficiary(_msgSender());
        }
        emit TokenURIUpdate(newId, uri);
    }

    function requestUpdateTokenMetadata(uint256 tokenId, string memory uri) external override onlyMinterOrBeneficiary(tokenId) {
        require(bytes(uri).length != 0, "NftERC721.approveUpdateTokenMetadata: NO_URI_UPDATE");
        _requestedUri[tokenId] = uri;
        emit TokenURIUpdateRequest(tokenId, uri);
    }

    function approveUpdateTokenMetadata(uint256 tokenId) external override onlyTokenOwner(tokenId) returns (bool) {
        string memory newUri = _requestedUri[tokenId];
        delete _requestedUri[tokenId];
        _setTokenURI(tokenId, newUri);
        emit TokenURIUpdate(tokenId, newUri);
        return true;
    }

    function burn(uint256 tokenId) external override onlyTokenOwner(tokenId) returns (bool) {
        _burn(tokenId);
        return true;
    }

    function getMinter(uint256 tokenId) public view override returns (address) {
        return _minters[tokenId];
    }

    function getUpdate(uint256 tokenId) external view override returns (string memory) {
        return _requestedUri[tokenId];
    }

    function _setMinter(address minter, uint256 tokenId) internal {
         _minters[tokenId] = minter;
    }

}