# URL Shortener

## 简介

`url-shortener` 是一个本地命令行工具（命令名 `shorten`）。它检查 http/https 网址并打印短链接。未指定自定义短码时使用 `abc123`。`list` 和 `stats` 只显示内置示例，不会把链接保存到磁盘。非法网址、不安全短码会被拒绝；网址里的方括号会按原样显示，避免终端样式改写链接或让命令崩溃。短链接前缀可用 `--base-url` 或环境变量 `SHORTEN_BASE_URL` 指定。

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Utility Tool](https://img.shields.io/badge/utility-tool-green.svg)](https://github.com/Master-626/url-shortener)

## Purpose

`shorten` checks that a link is an absolute http(s) URL, then prints a short link made of a base URL and a short code. Omit `--custom` and the code is `abc123`. `list` prints one sample row (`abc123`, `https://github.com`, 42 clicks). `stats` prints a sample count of 42 clicks for the code you pass. Short links are printed to the terminal and are not stored.

## Installation

Python 3.10 or newer is required. Current Click releases need 3.10, which is the minimum this project installs on.

```bash
git clone https://github.com/Master-626/url-shortener.git
cd url-shortener
python -m pip install .
```

Install the test and lint tools with the `dev` extra:

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
# Shorten a URL. The default code is abc123.
shorten shorten "https://github.com/Master-626"

# Choose the short code.
shorten shorten "https://github.com" -c gh

# Choose the prefix. A trailing slash is removed.
shorten shorten "https://github.com" -c gh -b https://s.example/r/

# The same prefix can come from the environment.
SHORTEN_BASE_URL=https://s.example shorten shorten "https://github.com"

# Sample table and sample click count.
shorten list
shorten stats gh

shorten --help
shorten shorten --help
shorten --version
```

Example output:

```text
✅ Shortened: https://github.com/Master-626 -> https://my.url/abc123
✅ Shortened: https://github.com -> https://s.example/r/gh
📊 Stats for gh: 42 clicks
```

## Options

| Command | Argument or option | What it does |
| --- | --- | --- |
| `shorten` | `URL` | Absolute `http` or `https` URL. Surrounding whitespace is removed. |
| `shorten` | `-c`, `--custom TEXT` | Short code used instead of `abc123`. Surrounding whitespace is removed. |
| `shorten` | `-b`, `--base-url TEXT` | Prefix of the short link. Default: `https://my.url`. Trailing slashes are removed. Overrides `SHORTEN_BASE_URL`. |
| `list` | | Prints the sample table. |
| `stats` | `CODE` | Prints `42 clicks` for that code. The code is shown as typed. |
| | `--version` | Prints the package version. |
| | `--help` | Prints help for the program or a command. |

A custom code stays a single path segment. It cannot be empty, `.`, or `..`, and it cannot contain whitespace, control characters, `/`, `\`, `?`, `#`, or `%`. Letters, digits, and other visible characters such as `-`, `_`, `.`, and non-ASCII text are allowed.

The target URL must include a scheme of `http` or `https`, a host, and a valid port. `javascript:`, `data:`, and `file:` URLs are rejected. A base URL follows the same scheme and host rules and cannot include a query or fragment.

## Running tests

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

GitHub Actions runs Ruff and pytest on Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## License

MIT License. See [LICENSE](LICENSE).
