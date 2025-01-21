// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Blackjack.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// Mock ERC20 token for testing
contract MockToken is ERC20 {
    constructor() ERC20("Mock Token", "MTK") {
        // Mint 100,000 tokens to cover all test scenarios
        _mint(msg.sender, 100000 * 10 ** 18);
    }
}

contract BlackjackTest is Test {
    Blackjack public game;
    MockToken public token;
    address public owner;
    address public player;
    address public otherPlayer;
    uint256 public playerId;
    uint256 public constant INITIAL_BALANCE = 5000 * 10 ** 18;
    uint256 public constant MIN_BET = 100 * 10 ** 18;
    uint256 public constant DEPOSIT_AMOUNT = 1000 * 10 ** 18;
    uint256 public constant BET_AMOUNT = 100 * 10 ** 18;

    function setUp() public {
        owner = address(this);
        player = address(0x1);
        otherPlayer = address(0x2);
        playerId = 1;

        token = new MockToken();

        require(
            token.balanceOf(address(this)) >= INITIAL_BALANCE * 3,
            "Insufficient initial tokens"
        );

        game = new Blackjack(address(token));

        token.transfer(player, INITIAL_BALANCE);
        token.transfer(otherPlayer, INITIAL_BALANCE);

        token.approve(address(game), INITIAL_BALANCE);
        game.depositHouseFunds(INITIAL_BALANCE);

        vm.prank(player);
        token.approve(address(game), INITIAL_BALANCE);
        vm.prank(otherPlayer);
        token.approve(address(game), INITIAL_BALANCE);
    }

    function testDeposit() public {
        vm.prank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);
        assertEq(game.getBalance(playerId), DEPOSIT_AMOUNT);
    }

    function testFailDepositSameIdDifferentAddress() public {
        vm.prank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);

        vm.prank(otherPlayer);
        game.deposit(playerId, DEPOSIT_AMOUNT);
    }

    function testPlaceBet() public {
        vm.startPrank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);
        game.placeBet(playerId, BET_AMOUNT);
        vm.stopPrank();

        assertEq(game.getBalance(playerId), DEPOSIT_AMOUNT - BET_AMOUNT);
    }

    function testResolveGame_PlayerBlackjack() public {
        vm.startPrank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);
        game.placeBet(playerId, BET_AMOUNT);
        vm.stopPrank();

        game.resolveGame(playerId, Blackjack.GameState.PLAYER_BLACKJACK);
        // Blackjack pays 2.5x the bet amount (100 * 2.5 = 250) plus remaining balance (900)
        assertEq(
            game.getBalance(playerId),
            DEPOSIT_AMOUNT - BET_AMOUNT + ((BET_AMOUNT * 5) / 2)
        );
    }

    function testWithdraw() public {
        vm.startPrank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);
        uint256 withdrawAmount = 500 * 10 ** 18;
        uint256 balanceBefore = token.balanceOf(player);
        game.withdraw(playerId, withdrawAmount);
        uint256 balanceAfter = token.balanceOf(player);
        vm.stopPrank();

        assertEq(game.getBalance(playerId), DEPOSIT_AMOUNT - withdrawAmount);
        assertEq(balanceAfter - balanceBefore, withdrawAmount);
    }

    function testFailWithdrawFromWrongAddress() public {
        vm.prank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);

        vm.prank(otherPlayer);
        game.withdraw(playerId, 500 * 10 ** 18);
    }

    function testFailWithdrawWithActiveBet() public {
        vm.startPrank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);
        game.placeBet(playerId, BET_AMOUNT);
        game.withdraw(playerId, 500 * 10 ** 18);
        vm.stopPrank();
    }

    function testFailBetBelowMinimum() public {
        vm.startPrank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);
        game.placeBet(playerId, MIN_BET - 1);
        vm.stopPrank();
    }

    function testFailBetAboveMaximum() public {
        vm.startPrank(player);
        game.deposit(playerId, DEPOSIT_AMOUNT);
        game.placeBet(playerId, 10001 * 10 ** 18);
        vm.stopPrank();
    }

    function testDepositHouseFunds() public {
        uint256 houseDepositAmount = 10000 * 10 ** 18;
        uint256 balanceBefore = token.balanceOf(address(game));

        token.approve(address(game), houseDepositAmount);
        game.depositHouseFunds(houseDepositAmount);

        uint256 balanceAfter = token.balanceOf(address(game));
        assertEq(balanceAfter - balanceBefore, houseDepositAmount);
    }

    function testFailDepositHouseFundsNotOwner() public {
        uint256 houseDepositAmount = 10000 * 10 ** 18;

        vm.prank(player);
        game.depositHouseFunds(houseDepositAmount);
    }
}
