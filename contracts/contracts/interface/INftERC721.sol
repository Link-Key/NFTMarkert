// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;

import "./IERC721.sol";
import "./IBeneficiaryRole.sol";
import "./IERC721Enumerable.sol";
import "./IERC721Metadata.sol";

/**
 * @dev Interface extension to ERC721 for NFT added functionality
 */
interface INftERC721 is IERC721, IBeneficiaryRole {
    // events
    event TokenURIUpdateRequest(uint256 indexed tokenId, string uri);

    event TokenURIUpdate(uint256 indexed tokenId, string uri);

    // public
    function mint(address reciever, string memory uri) external;

    // minter/beneficiary only
    function requestUpdateTokenMetadata(uint256 tokenId, string memory uri) external;

    // token owner only function
    function approveUpdateTokenMetadata(uint256 tokenId) external returns (bool);

    function burn(uint256 tokenId) external returns (bool);

    function getMinter(uint256 tokenId) external view returns (address);

    function getUpdate(uint256 tokenId) external view returns (string memory);

    

    

}