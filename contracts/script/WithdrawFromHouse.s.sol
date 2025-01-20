// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/Blackjack.sol";
import "../src/ERC20.sol";

contract DepositToHouse is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address blackjackAddress = vm.envAddress("BLACKJACK_ADDRESS");
        address erc20Address = vm.envAddress("ERC20_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        Blackjack blackjack = Blackjack(blackjackAddress);
        BlackjackToken token = BlackjackToken(erc20Address);

        uint256 balance = token.balanceOf(blackjackAddress);

        blackjack.withdrawHouseFunds(balance);

        vm.stopBroadcast();
    }
}
