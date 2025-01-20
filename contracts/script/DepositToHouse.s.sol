// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/ERC20.sol";

contract DepositToHouse is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address erc20Address = vm.envAddress("ERC20_ADDRESS");
        address blackjackAddress = vm.envAddress("BLACKJACK_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        BlackjackToken token = BlackjackToken(erc20Address);

        token.approve(blackjackAddress, 1000000 ether);
        token.transfer(blackjackAddress, 100000 ether);

        vm.stopBroadcast();
    }
}
