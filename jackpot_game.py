#!/usr/bin/env python3
import os
import random
import sys
import time
from datetime import datetime

try:
    from rich.align import Align
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except Exception:
    Console = None

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"

DATA_DIR = os.path.join(os.path.expanduser("~"), ".luckytermux")
SAVE_FILE = os.path.join(DATA_DIR, "jackpot_save.txt")
LOG_FILE = os.path.join(DATA_DIR, "jackpot_history.log")

balance = 100
bet = 0
player_name = ""
jackpot_pool = 500

os.makedirs(DATA_DIR, exist_ok=True)

console = Console() if Console else None
USE_RICH = console is not None


def clear_screen():
    os.system("clear")


def print_header():
    clear_screen()
    if USE_RICH:
        title = "[bold green]TERMUX JACKPOT GAME v2[/bold green]"
        subtitle = "[green]LuckyTermux Edition[/green]"
        body = f"{title}\n{subtitle}"
        console.print(Panel(Align.center(body), border_style="green"))
        return
    print(f"{GREEN}========================================={NC}")
    print(f"{GREEN}        TERMUX JACKPOT GAME v2          {NC}")
    print(f"{GREEN}========================================={NC}")


def pause():
    print(f"{YELLOW}Press Enter to continue...{NC}")
    input()


def log_event(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts} | {player_name} | {msg}\n")


def load_save():
    global player_name, balance, jackpot_pool
    if os.path.isfile(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                parts = f.read().strip().split()
                if len(parts) >= 3:
                    player_name = parts[0]
                    balance = int(parts[1])
                    jackpot_pool = int(parts[2])
        except (OSError, ValueError):
            player_name = ""
            balance = 100
            jackpot_pool = 500


def save_game():
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        f.write(f"{player_name} {balance} {jackpot_pool}\n")


def choose_player():
    global player_name
    print_header()
    print(f"{YELLOW}Enter your player name:{NC}")
    name = input().strip()
    player_name = name if name else "Player"
    log_event("Login")
    save_game()


def show_status():
    if USE_RICH:
        table = Table(show_header=False, box=None)
        table.add_row("[yellow]Player[/yellow]", f"[green]{player_name}[/green]")
        table.add_row("[yellow]Balance[/yellow]", f"[green]${balance}[/green]")
        table.add_row("[yellow]Jackpot Pool[/yellow]", f"[green]${jackpot_pool}[/green]")
        console.print(Panel(table, title="Status", border_style="green"))
        return
    print(f"{YELLOW}Player: {NC}{GREEN}{player_name}{NC}")
    print(f"{YELLOW}Balance: {NC}{GREEN}${balance}{NC}")
    print(f"{YELLOW}Jackpot Pool: {NC}{GREEN}${jackpot_pool}{NC}")


def choose_bet_level():
    print(f"{GREEN}Choose Bet Level:{NC}")
    print("1. Low (Bet 5-50, Win x3, Hit on 1/4)")
    print("2. Medium (Bet 10-100, Win x5, Hit on 1/6)")
    print("3. High (Bet 20-200, Win x10, Hit on 1/10)")
    choice = input().strip()
    if choice == "1":
        return 5, 50, 3, 4
    if choice == "2":
        return 10, 100, 5, 6
    if choice == "3":
        return 20, 200, 10, 10
    print(f"{RED}Invalid choice.{NC}")
    return None


def spin_animation(win: bool):
    symbols = ["7", "★", "♦", "♣", "♥", "☀", "☘", "◆"]
    frames = 18
    interval = 0.08

    for _ in range(frames):
        s1 = random.choice(symbols)
        s2 = random.choice(symbols)
        s3 = random.choice(symbols)
        sys.stdout.write(f"\r{YELLOW}Spinning... [{s1}] [{s2}] [{s3}]{NC}")
        sys.stdout.flush()
        time.sleep(interval)

    if win:
        final = ("7", "7", "7")
    else:
        final = random.sample(symbols, 3)

    sys.stdout.write(f"\r{GREEN}Result:   [{final[0]}] [{final[1]}] [{final[2]}]{NC}\n")
    sys.stdout.flush()


def view_history():
    print_header()
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-20:]
        for line in lines:
            print(line.rstrip())
    else:
        print(f"{YELLOW}No history yet.{NC}")
    pause()


def play_round():
    global balance, jackpot_pool
    print_header()
    show_status()
    level = choose_bet_level()
    if level is None:
        pause()
        return

    min_bet, max_bet, win_mult, hit_mod = level
    print(f"{GREEN}Enter your bet amount (0 to cancel): {NC}")
    try:
        bet_input = int(input().strip())
    except ValueError:
        print(f"{RED}Invalid bet amount.{NC}")
        pause()
        return

    if bet_input == 0:
        return

    if bet_input > balance:
        print(f"{RED}Insufficient balance! Please bet a smaller amount.{NC}")
        pause()
        return

    if bet_input < min_bet or bet_input > max_bet:
        print(f"{RED}Bet must be between ${min_bet} and ${max_bet}.{NC}")
        pause()
        return

    result = random.randint(0, hit_mod - 1)
    jackpot_hit = random.randint(0, 49)
    win = result == 0

    print(f"{YELLOW}Spinning the wheels...{NC}")
    spin_animation(win)

    if win:
        win_amount = bet_input * win_mult
        balance += win_amount
        print(f"{GREEN}You win!{NC}")
        log_event(f"Win: +{win_amount} (bet {bet_input}, level x{win_mult})")
    else:
        balance -= bet_input
        jackpot_pool += bet_input // 2
        print(f"{RED}Unfortunately, you lost this round.{NC}")
        log_event(f"Lose: -{bet_input}")

    if jackpot_hit == 0:
        print(f"{GREEN}!!! PROGRESSIVE JACKPOT HIT !!!{NC}")
        balance += jackpot_pool
        log_event(f"Progressive Jackpot: +{jackpot_pool}")
        jackpot_pool = 500

    print(f"{YELLOW}Your new balance is: ${balance}{NC}")

    if balance <= 0:
        print(f"{RED}You have run out of money. Game Over!{NC}")
        log_event("Game Over")
        save_game()
        pause()
        raise SystemExit(0)

    save_game()
    pause()


def main_menu():
    while True:
        print_header()
        show_status()
        if USE_RICH:
            menu = Table(show_header=False, box=None)
            menu.add_row("[green]1.[/green]", "Play")
            menu.add_row("[green]2.[/green]", "View History")
            menu.add_row("[green]3.[/green]", "Save & Exit")
            console.print(Panel(menu, title="Menu", border_style="green"))
        else:
            print(f"{GREEN}1. Play{NC}")
            print(f"{GREEN}2. View History{NC}")
            print(f"{GREEN}3. Save & Exit{NC}")
        choice = input().strip()
        if choice == "1":
            play_round()
        elif choice == "2":
            view_history()
        elif choice == "3":
            save_game()
            print(f"{YELLOW}Game saved. Bye!{NC}")
            raise SystemExit(0)
        else:
            print(f"{RED}Invalid option.{NC}")
            pause()


def main():
    load_save()
    if not player_name:
        choose_player()
    main_menu()


if __name__ == "__main__":
    main()
