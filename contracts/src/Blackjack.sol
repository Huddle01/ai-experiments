// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract Blackjack is ReentrancyGuard {
    enum GameState {
        PLAYER_BUST,
        DEALER_BUST,
        PLAYER_BLACKJACK,
        DEALER_BLACKJACK,
        PLAYER_WIN,
        DEALER_WIN,
        TIE
    }

    struct Player {
        uint256 balance;
        bool exists;
        uint256 activeBet;
        bool hasActiveBet;
        address playerAddress;
    }

    mapping(uint256 => Player) public players;
    address public owner;
    uint256 public minBet = 100 * 10 ** 18;
    uint256 public maxBet = 10000 * 10 ** 18;
    IERC20 public gameToken;

    event HouseFundsDeposited(address indexed owner, uint256 amount);
    event FundsDeposited(
        uint256 playerId,
        address indexed player,
        uint256 amount
    );
    event BetPlaced(uint256 playerId, uint256 amount);
    event GameResult(uint256 playerId, GameState result, uint256 payout);
    event FundsWithdrawn(
        uint256 playerId,
        address indexed player,
        uint256 amount
    );

    constructor(address _tokenAddress) {
        owner = msg.sender;
        gameToken = IERC20(_tokenAddress);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier validPlayerId(uint256 _playerId) {
        require(players[_playerId].exists, "Player ID does not exist");
        _;
    }

    modifier onlyPlayerOwner(uint256 _playerId) {
        require(
            players[_playerId].playerAddress == msg.sender,
            "Only player owner can withdraw"
        );
        _;
    }

    function deposit(uint256 _playerId, uint256 _amount) external nonReentrant {
        require(_amount > 0, "Deposit amount must be greater than 0");

        if (!players[_playerId].exists) {
            players[_playerId].exists = true;
            players[_playerId].playerAddress = msg.sender;
        } else {
            require(
                players[_playerId].playerAddress == msg.sender,
                "PlayerId already registered to different address"
            );
        }

        require(
            gameToken.transferFrom(msg.sender, address(this), _amount),
            "Token transfer failed"
        );

        players[_playerId].balance += _amount;
        emit FundsDeposited(_playerId, msg.sender, _amount);
    }

    function getBalance(uint256 _playerId) external view returns (uint256) {
        require(players[_playerId].exists, "Player ID does not exist");
        return players[_playerId].balance;
    }

    function placeBet(
        uint256 _playerId,
        uint256 _betAmount
    ) external validPlayerId(_playerId) nonReentrant {
        require(!players[_playerId].hasActiveBet, "Player has an active bet");
        require(_betAmount >= minBet, "Bet amount below minimum");
        require(_betAmount <= maxBet, "Bet amount above maximum");
        require(
            players[_playerId].balance >= _betAmount,
            "Insufficient balance"
        );

        players[_playerId].balance -= _betAmount;
        players[_playerId].activeBet = _betAmount;
        players[_playerId].hasActiveBet = true;
        emit BetPlaced(_playerId, _betAmount);
    }

    function resolveGame(
        uint256 _playerId,
        GameState _gameState
    ) external onlyOwner validPlayerId(_playerId) nonReentrant {
        require(
            players[_playerId].hasActiveBet,
            "No active bet for this player"
        );
        uint256 _betAmount = players[_playerId].activeBet;
        uint256 payout = 0;

        if (_gameState == GameState.PLAYER_BLACKJACK) {
            payout = (_betAmount * 5) / 2;
        } else if (
            _gameState == GameState.PLAYER_WIN ||
            _gameState == GameState.DEALER_BUST
        ) {
            payout = _betAmount * 2;
        } else if (_gameState == GameState.TIE) {
            payout = _betAmount;
        }

        if (payout > 0) {
            players[_playerId].balance += payout;
        }

        players[_playerId].activeBet = 0;
        players[_playerId].hasActiveBet = false;
        emit GameResult(_playerId, _gameState, payout);
    }

    function withdraw(
        uint256 _playerId,
        uint256 _amount
    )
        external
        validPlayerId(_playerId)
        onlyPlayerOwner(_playerId)
        nonReentrant
    {
        require(_amount > 0, "Withdrawal amount must be greater than 0");
        require(
            !players[_playerId].hasActiveBet,
            "Cannot withdraw with active bet"
        );
        require(players[_playerId].balance >= _amount, "Insufficient balance");

        players[_playerId].balance -= _amount;
        require(
            gameToken.transfer(msg.sender, _amount),
            "Token transfer failed"
        );

        emit FundsWithdrawn(_playerId, msg.sender, _amount);
    }

    function updateBetLimits(
        uint256 _newMinBet,
        uint256 _newMaxBet
    ) external onlyOwner {
        require(_newMinBet < _newMaxBet, "Invalid bet limits");
        minBet = _newMinBet;
        maxBet = _newMaxBet;
    }

    function withdrawHouseFunds(
        uint256 _amount
    ) external onlyOwner nonReentrant {
        require(
            _amount <= gameToken.balanceOf(address(this)),
            "Insufficient contract balance"
        );
        require(gameToken.transfer(owner, _amount), "Token transfer failed");
    }

    function depositHouseFunds(
        uint256 _amount
    ) external onlyOwner nonReentrant {
        require(_amount > 0, "Deposit amount must be greater than 0");

        require(
            gameToken.transferFrom(msg.sender, address(this), _amount),
            "Token transfer failed"
        );

        emit HouseFundsDeposited(msg.sender, _amount);
    }
}
