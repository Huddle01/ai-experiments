// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/Blackjack.sol";

contract AIBlackjackTest is Test {
    Blackjack public game;
    address public owner;
    address public player;
    address public otherPlayer;
    uint256 public playerId;

    function setUp() public {
        owner = address(this);
        player = address(0x1);
        otherPlayer = address(0x2);
        playerId = 1;
        game = new Blackjack();
        vm.deal(player, 100 ether);
        vm.deal(otherPlayer, 100 ether);
    }

    function testDeposit() public {
        vm.prank(player);
        game.deposit{value: 1 ether}(playerId);
        assertEq(game.getBalance(playerId), 1 ether);
    }

    function testFailDepositSameIdDifferentAddress() public {
        vm.prank(player);
        game.deposit{value: 1 ether}(playerId);

        vm.prank(otherPlayer);
        game.deposit{value: 1 ether}(playerId);
    }

    function testPlaceBet() public {
        vm.startPrank(player);
        game.deposit{value: 1 ether}(playerId);
        game.placeBet(playerId, 0.5 ether);
        vm.stopPrank();
        assertEq(game.getBalance(playerId), 0.5 ether);
    }

    function testResolveGame_PlayerBlackjack() public {
        vm.startPrank(player);
        game.deposit{value: 1 ether}(playerId);
        game.placeBet(playerId, 0.5 ether);
        vm.stopPrank();

        game.resolveGame(playerId, Blackjack.GameState.PLAYER_BLACKJACK);
        assertEq(game.getBalance(playerId), 1.75 ether);
    }

    function testWithdraw() public {
        vm.startPrank(player);
        game.deposit{value: 1 ether}(playerId);
        game.withdraw(playerId, 0.5 ether);
        vm.stopPrank();
        assertEq(game.getBalance(playerId), 0.5 ether);
    }

    function testFailWithdrawFromWrongAddress() public {
        vm.prank(player);
        game.deposit{value: 1 ether}(playerId);

        vm.prank(otherPlayer);
        game.withdraw(playerId, 0.5 ether); // Should fail
    }

    function testFailWithdrawWithActiveBet() public {
        vm.startPrank(player);
        game.deposit{value: 1 ether}(playerId);
        game.placeBet(playerId, 0.5 ether);
        game.withdraw(playerId, 0.3 ether); // Should fail
        vm.stopPrank();
    }

    receive() external payable {}
}
