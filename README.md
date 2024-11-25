# Megathronic Instagram Checker

## Vısual 

![Screenshot_2024-11-25-23-33-06-763_com termux-edit~2](https://github.com/user-attachments/assets/20f015d0-0d24-4bd8-8f74-00ee0da471a5)

## Very Important

- **Logging into the target account** without using a proxy or tor address will result in your **IP address being banned**.
- **Recommended usage**: 
Configure the target's country in the `torrc` file.
Start the Tor proxy.
Use this software while connected through Tor.
- **Note**: Using this software from the same IP address repeatedly will not be beneficial.

## Description

This project is a Python-based brute force tool designed to work with Instagram's API. The tool works by sending requests and is compatible with mobile devices. Users must have their own proxy service to use this tool effectively. Additionally, users can attempt to crack passwords using wordlists.

## Features

- Works with Instagram's API for brute force attacks.
- Compatible with mobile devices.
- Requires users to have their own proxy service.
- Allows users to attempt to crack passwords using wordlists.

- Easy to use and install.

## Installation

1. Clone the repository:

```
git clone https://github.com/archescyber/instagram-forcer
```

2. Install the requires:

```
pip install instaloader
```

3. Install the proxy service.  Make sure you have a valid proxy server to route your requests through.

## Usage

1. Configure the tool:
- Edit the configuration file to include your proxy details.
- Enter the target username and the wordlist you want to use for password attempts.

2. Run the script:

```
python megathronic.py
```

3. Monitor the output for progress and results as the tool attempts to crack the password.

## Important Notes

- **Proxy Requirement**: Users must have their own proxy service. The tool will not work without a valid proxy.

- **Wordlist Usage**: Users can specify a wordlist to attempt to crack the password. Make sure your wordlist is formatted correctly for best performance.

- **Ethical Considerations**: Use this tool responsibly and only on accounts you own or have explicit permission to test. Unauthorized access to accounts is illegal and unethical.
- **API Rate Limits**: Use a good proxy service to avoid temporary access suspensions. You will need this to bypass API rate limits.

## Contribution

Feel free to contribute to the project by submitting issues or pull requests. All contributions are welcome!   

For communication, you can send feedback to my Instagram account named **@yusuf.cyw**
