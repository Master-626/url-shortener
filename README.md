# URL Shortener

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Utility Tool](https://img.shields.io/badge/utility-tool-green.svg)]()

A URL shortening and management CLI with click statistics.

## ✨ Features

- **Shorten URLs** - Quickly shorten long URLs
- **Custom Codes** - Use custom short codes
- **Click Stats** - Track how many times links are clicked
- **Link Expiration** - Set expiration dates for links
- **Tags** - Organize links with tags
- **Search** - Find your links quickly
- **QR Codes** - Generate QR codes for links
- **Rich UI** - Beautiful colored terminal output

## 📦 Installation

```bash
git clone https://github.com/Master-626/url-shortener.git
cd url-shortener
pip install .
```

## 🚀 Quick Start

```bash
# Shorten a URL
shorten shorten "https://github.com/Master-626"

# Custom short code
shorten shorten "https://github.com" -c gh

# View stats
shorten stats gh
```

## 📄 License

MIT License
