#!/bin/bash

# Jackpot Game Script for Termux
# Colored Output Variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Game Variables
balance=100
bet=0

echo -e "${GREEN}Welcome to the Termux Jackpot Game!${NC}"
echo -e "${YELLOW}Your starting balance is: \$${balance}${NC}"

while true; do
    echo -e "${GREEN}Enter your bet amount (0 to exit): ${NC}"
    read -r bet

    if [[ $bet -eq 0 ]]; then
        echo -e "${YELLOW}Thank you for playing! Your final balance is: \$${balance}${NC}"
        exit 0
    fi

    if [[ $bet -gt $balance ]]; then
        echo -e "${RED}Insufficient balance! Please bet a smaller amount.${NC}"
        continue
    fi

    # Simulating the result of the jackpot
    echo -e "${YELLOW}Spinning the wheels...${NC}"
    sleep 2
    result=$(( RANDOM % 10 )) # Random number between 0 and 9

    if [[ $result -eq 7 ]]; then
        echo -e "${GREEN}Congratulations! You hit the jackpot!${NC}"
        balance=$(( balance + bet * 10 )) # Winning Condition
    else
        echo -e "${RED}Unfortunately, you lost this round.${NC}"
        balance=$(( balance - bet )) # Deducting the bet from the balance
    fi

    echo -e "${YELLOW}Your new balance is: \$${balance}${NC}"
    
    if [[ $balance -le 0 ]]; then
        echo -e "${RED}You have run out of money. Game Over!${NC}"
        exit 0
    fi
done
