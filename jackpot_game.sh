#!/bin/bash

# Jackpot Game Script for Termux
# Colored Output Variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

DATA_DIR="$HOME/.luckytermux"
SAVE_FILE="$DATA_DIR/jackpot_save.txt"
LOG_FILE="$DATA_DIR/jackpot_history.log"

# Game Variables
balance=100
bet=0
player_name=""
jackpot_pool=500

mkdir -p "$DATA_DIR"

print_header() {
    clear
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}        TERMUX JACKPOT GAME v2          ${NC}"
    echo -e "${GREEN}=========================================${NC}"
}

pause() {
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r _
}

log_event() {
    local msg="$1"
    printf "%s | %s | %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$player_name" "$msg" >> "$LOG_FILE"
}

load_save() {
    if [[ -f "$SAVE_FILE" ]]; then
        read -r player_name balance jackpot_pool < "$SAVE_FILE"
    else
        player_name=""
        balance=100
        jackpot_pool=500
    fi
}

save_game() {
    printf "%s %s %s\n" "$player_name" "$balance" "$jackpot_pool" > "$SAVE_FILE"
}

choose_player() {
    print_header
    echo -e "${YELLOW}Enter your player name:${NC}"
    read -r player_name
    if [[ -z "$player_name" ]]; then
        player_name="Player"
    fi
    log_event "Login"
    save_game
}

show_status() {
    echo -e "${YELLOW}Player: ${NC}${GREEN}${player_name}${NC}"
    echo -e "${YELLOW}Balance: ${NC}${GREEN}\$${balance}${NC}"
    echo -e "${YELLOW}Jackpot Pool: ${NC}${GREEN}\$${jackpot_pool}${NC}"
}

choose_bet_level() {
    echo -e "${GREEN}Choose Bet Level:${NC}"
    echo -e "1. Low (Bet 5-50, Win x3, Hit on 1/4)"
    echo -e "2. Medium (Bet 10-100, Win x5, Hit on 1/6)"
    echo -e "3. High (Bet 20-200, Win x10, Hit on 1/10)"
    read -r level
    case "$level" in
        1) min_bet=5; max_bet=50; win_mult=3; hit_mod=4;;
        2) min_bet=10; max_bet=100; win_mult=5; hit_mod=6;;
        3) min_bet=20; max_bet=200; win_mult=10; hit_mod=10;;
        *) echo -e "${RED}Invalid choice.${NC}"; return 1;;
    esac
    return 0
}

main_menu() {
    while true; do
        print_header
        show_status
        echo -e "${GREEN}1. Play${NC}"
        echo -e "${GREEN}2. View History${NC}"
        echo -e "${GREEN}3. Save & Exit${NC}"
        read -r menu_choice
        case "$menu_choice" in
            1) play_round;;
            2) view_history;;
            3) save_game; echo -e "${YELLOW}Game saved. Bye!${NC}"; exit 0;;
            *) echo -e "${RED}Invalid option.${NC}"; pause;;
        esac
    done
}

view_history() {
    print_header
    if [[ -f "$LOG_FILE" ]]; then
        tail -n 20 "$LOG_FILE"
    else
        echo -e "${YELLOW}No history yet.${NC}"
    fi
    pause
}

play_round() {
    print_header
    show_status
    choose_bet_level || { pause; return; }
    echo -e "${GREEN}Enter your bet amount (0 to cancel): ${NC}"
    read -r bet

    if [[ $bet -eq 0 ]]; then
        return
    fi

    if [[ $bet -gt $balance ]]; then
        echo -e "${RED}Insufficient balance! Please bet a smaller amount.${NC}"
        pause
        return
    fi

    if [[ $bet -lt $min_bet || $bet -gt $max_bet ]]; then
        echo -e "${RED}Bet must be between \$${min_bet} and \$${max_bet}.${NC}"
        pause
        return
    fi

    # Simulating the result of the jackpot
    echo -e "${YELLOW}Spinning the wheels...${NC}"
    sleep 2
    result=$(( RANDOM % hit_mod ))
    jackpot_hit=$(( RANDOM % 50 )) # 1/50 chance for progressive jackpot

    if [[ $result -eq 0 ]]; then
        echo -e "${GREEN}You win!${NC}"
        win_amount=$(( bet * win_mult ))
        balance=$(( balance + win_amount ))
        log_event "Win: +$win_amount (bet $bet, level x$win_mult)"
    else
        echo -e "${RED}Unfortunately, you lost this round.${NC}"
        balance=$(( balance - bet ))
        jackpot_pool=$(( jackpot_pool + bet / 2 ))
        log_event "Lose: -$bet"
    fi

    if [[ $jackpot_hit -eq 0 ]]; then
        echo -e "${GREEN}!!! PROGRESSIVE JACKPOT HIT !!!${NC}"
        balance=$(( balance + jackpot_pool ))
        log_event "Progressive Jackpot: +$jackpot_pool"
        jackpot_pool=500
    fi

    echo -e "${YELLOW}Your new balance is: \$${balance}${NC}"
    
    if [[ $balance -le 0 ]]; then
        echo -e "${RED}You have run out of money. Game Over!${NC}"
        log_event "Game Over"
        save_game
        pause
        exit 0
    fi
    save_game
    pause
}

load_save
if [[ -z "$player_name" ]]; then
    choose_player
fi
main_menu
