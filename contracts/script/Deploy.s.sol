// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/Blackjack.sol";

contract DeployAIBlackjack is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address erc20Address = vm.envAddress("ERC20_ADDRESS");

        vm.startBroadcast(deployerPrivateKey);

        Blackjack game = new Blackjack(erc20Address);

        vm.stopBroadcast();
    }
}
