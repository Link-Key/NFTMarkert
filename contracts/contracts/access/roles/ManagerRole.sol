// SPDX-License-Identifier: MIT

pragma solidity >=0.6.2 <0.8.0;

import "../../utils/Context.sol";
import "../Roles.sol";

contract ManagerRole is Context {
    using Roles for Roles.Role;

    event ManagerAdded(address indexed account);
    event ManagerRemoved(address indexed account);

    Roles.Role private _managers;

    constructor () public {
        _addManager(_msgSender());
    }

    modifier onlyManager() {
        require(isManager(_msgSender()), "ManageRole.onlyManager: NOT_MANAGER");
        _;
    }

    function isManager(address account) public view returns (bool) {
        return _managers.has(account);
    }

    function addManager(address account) public onlyManager {
        _addManager(account);
    }

    function renounceManager() public {
        _removeManager(_msgSender());
    }

    function _addManager(address account) internal {
        _managers.add(account);
        emit ManagerAdded(account);
    }

    function _removeManager(address account) internal {
        _managers.remove(account);
        emit ManagerRemoved(account);
    }
}