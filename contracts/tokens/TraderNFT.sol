// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @custom:security-contact heseinberg@buffer.finance
contract TraderNFT is ERC721, ERC721URIStorage, Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    uint256 public nftBasePrice = 2 * 10**18;
    uint256 public maxNFTMintLimit = 10000;
    string public baseURI = "https://gateway.pinata.cloud/ipfs/";

    Counters.Counter public tokenIdCounter;
    Counters.Counter public claimTokenIdCounter;

    mapping(uint256 => uint8) public tokenTierMappings;
    mapping(uint256 => bool) public tokenMintMappings;
    mapping(address => uint8) public userTier;

    event UpdateNftBasePrice(uint256 nftBasePrice);
    event UpdateMaxNFTMintLimits(uint256 maxNFTMintLimit);
    event UpdateBaseURI(string baseURI);

    event Claim(uint256 claimTokenId, address account);
    event Mint(uint256 tokenId, address account, uint8 tier);

    address public admin;

    constructor(address _admin) ERC721("Buffer Prime", "pBFR") {
        admin = _admin;
    }

    function safeMint(
        address to,
        string memory uri,
        uint8 tier,
        uint256 claimtokenId
    ) public onlyOwner returns (uint256 tokenId) {
        require(
            tokenMintMappings[claimtokenId] == false,
            "Token already minted"
        );

        tokenId = tokenIdCounter.current();
        tokenIdCounter.increment();
        tokenTierMappings[tokenId] = tier;

        // userTier[to] = max(userTier[to], tier) // TODO: Remove this, fix bug
        if (userTier[to] < tier) {
            userTier[to] = tier;
        }

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        tokenMintMappings[claimtokenId] = true;
        emit Mint(tokenId, to, tier);
    }

    function claim()
        external
        payable
        nonReentrant
        returns (uint256 claimTokenId)
    {
        require(
            claimTokenIdCounter.current() < maxNFTMintLimit,
            "Maximum Limit for minting NFTs reached"
        );

        require(msg.value >= nftBasePrice, "Wrong value");
        if (msg.value > nftBasePrice) {
            payable(msg.sender).transfer(msg.value - nftBasePrice);
        }
        claimTokenId = claimTokenIdCounter.current();
        claimTokenIdCounter.increment();
        payable(admin).transfer(nftBasePrice);
        emit Claim(claimTokenId, msg.sender);
    }

    function setNftBasePrice(uint256 value) external onlyOwner {
        nftBasePrice = value;
        emit UpdateNftBasePrice(nftBasePrice);
    }

    function setMaxNFTMintLimit(uint256 value) external onlyOwner {
        maxNFTMintLimit = value;
        emit UpdateMaxNFTMintLimits(maxNFTMintLimit);
    }

    function _setTokenURI(uint256 tokenId, string memory _tokenURI)
        internal
        override
    {
        return super._setTokenURI(tokenId, _tokenURI);
    }

    function _burn(uint256 tokenId)
        internal
        override(ERC721, ERC721URIStorage)
    {
        super._burn(tokenId);
    }

    function _baseURI() internal view override returns (string memory) {
        return baseURI;
    }

    function setBaseURI(string memory value) external onlyOwner {
        baseURI = value;
        emit UpdateBaseURI(baseURI);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
}
