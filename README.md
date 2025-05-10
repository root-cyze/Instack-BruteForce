# Instack - Instagram Brute Force Tool

![Instack Banner](https://github.com/user-attachments/assets/24f306aa-db3e-4eed-87f3-cea84968268d)

## Very Important

> **Using this tool without a proxy or TOR address may result in your IP address being banned by Instagram. Always route your traffic through a secure proxy.**

---

## Description

**Instack** is a Python-based brute force utility designed to interact with Instagram's API to test login credentials using wordlists. It is lightweight, mobile-friendly, and ideal for ethical testing and educational use only. The tool supports proxy integration to bypass rate-limiting and IP bans.

---

## Features

- Works with Instagram's login flow.
- Mobile-friendly design.
- Proxy support for secure and anonymous operation.
- Supports wordlist-based brute force attempts.
- Minimal and intuitive terminal interface.

---

## Installation

1. Clone the repository

```bash
git clone https://github.com/root-cyze/Instack-InstagramBruteForce
cd Instack-InstagramBruteForce
```

2. Install required libraries

```
pip install -r requirements.txt
```

> Make sure your Python version is 3.8 or above.



3. Setup your proxy

You must use a proxy to avoid IP bans. Edit your configuration (or the script) to include your proxy IP and port.


---

# Usage

1. Prepare your environment:

Add your proxy configuration.

Provide the target Instagram username.

Add your password wordlist (.txt).



#2. Run the tool:



```
python instagram_checker.py
```

3. Monitor output to view login attempts and status.




---

# File Structure

├── instagram_checker.py   
├── requirements.txt       
└── README.md              

---

# License & Legal

This tool is for educational and authorized testing purposes only.
Do not use it against accounts you do not own or have permission to test.
Violating Instagram's Terms of Service can result in account termination or legal action.

Unauthorized redistribution of this tool is strictly prohibited. All rights reserved to Cyze.
