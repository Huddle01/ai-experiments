// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract BlackjackToken is ERC20 {
    constructor() ERC20("Blackjack Token", "BJ") {
        _mint(msg.sender, 100000000 * (10 ** uint256(decimals())));
    }
}
