// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;

import "../Roles.sol";

import "../../utils/Context.sol";
import "../../interface/IBeneficiaryRole.sol";


contract BeneficiaryRole is Context, IBeneficiaryRole {
    using Roles for Roles.Role;

    event BeneficiaryAdded(address indexed account);
    event BeneficiaryRemoved(address indexed account);

    Roles.Role private _beneficiaries;

    mapping (address => address) private _beneficiariesToMinter;
    mapping (address => uint256) private _beneficiariesCount;

    constructor () public {}

    modifier onlyBeneficiary() {
        require(isBeneficiary(_msgSender()), "BeneficiaryRole.onlyBeneficiary: NOT_BENEFICIARY");
        _;
    }

    function isBeneficiary(address account) public view override returns (bool) {
        return _beneficiaries.has(account);
    }

    function beneficiaryFor(address beneficiary) public view override returns(address) {
        return _beneficiariesToMinter[beneficiary];
    }

    function addBeneficiary(address account) public override onlyBeneficiary {
        _addBeneficiary(account);
    }

    function renounceBeneficiary() public override {
        _removeBeneficiary(_msgSender());
    }

    function _addBeneficiary(address account) internal {
        _beneficiaries.add(account);
        _beneficiariesToMinter[account] = _msgSender();
        _beneficiariesCount[account] = _beneficiariesCount[account]+1;
        emit BeneficiaryAdded(account);
    }

    function _removeBeneficiary(address account) internal {
        require(_beneficiariesCount[account] > 0, "BeneficiaryRole.removeBeneficiary: MIN_BENEFICIARIES");
        _beneficiariesCount[account] = _beneficiariesCount[account]-1;
        _beneficiaries.remove(account);
        delete _beneficiariesToMinter[_msgSender()];
        emit BeneficiaryRemoved(account);
    }
}