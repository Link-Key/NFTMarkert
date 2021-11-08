// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;

interface IBeneficiaryRole {    

    function isBeneficiary(address account) external view returns (bool);

    function beneficiaryFor(address beneficiary) external view returns(address);

    function addBeneficiary(address account) external;

    function renounceBeneficiary() external;

}