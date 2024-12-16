# By Traders, For Traders.

<p align="center">
  <img src ="https://github.com/veighna-global/vnpy_evo/blob/dev/logo.png" width="300" height="300"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-0.3.2-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.10|3.11|3.12-blue.svg"/>
    <img src ="https://img.shields.io/github/license/veighna-global/vnpy_evo.svg?color=orange"/>
</p>

VeighNa Evo (vnpy_evo) is the core module for using [VeighNa (vnpy)](https://github.com/vnpy/vnpy) quant trading platform on the crypto market.

## Social

- <sub>[![Twitter](https://img.shields.io/twitter/follow/veighna.svg?style=social&label=VeighNa%20Global)](https://x.com/veighna_global)</sub>  Follow us on Twitter
- <sub>[![Telegram Announcements](https://img.shields.io/badge/VeighNa%20Global-Channel-blue?logo=telegram)](https://t.me/veighna_channel)</sub>  Follow our important announcements
- <sub>[![Telegram Chat](https://img.shields.io/badge/VeighNa%20Global-Chat-blue?logo=telegram)](https://t.me/+8KGF_z35nK03YWE1)</sub>  If you need technical support


## Features

1. Full-featured quantitative trading platform (vnpy_evo.trader)

2. Gateways which connect to exchanges for receiving market data and sending trading orders:

    * Crypto Market

        * Binance ([binance](https://www.github.com/veighna-global/vnpy_binance)): Spot/Perpetual/Futures/Option

        * OKX ([okx](https://www.github.com/veighna-global/vnpy_okx)): Spot/Perpetual/Futures/Option

        * Bybit ([bybit](https://www.github.com/veighna-global/vnpy_bybit)): Spot/Perpetual/Futures/Option

        * BTSE ([btse](https://www.github.com/veighna-global/vnpy_btse)): Spot/Perpetual/Futures

    * Forex Market

        * MT5 ([mt5](https://www.github.com/veighna-global/vnpy_mt5)): Forex/Gold/Commodity/Crypto

3. Applications for various quantitative strategies:

    * Nova Strategy ([nova_strategy](https://www.github.com/veighna-global/vnpy_novastrategy)): The quant strategy app module which is designed specifically for crypto markets, supports trend following, pair trading, multi-factor and many other types of quant strategies.

4. Event processing engine (vnpy_evo.event), which is the core of event-driven trading program

5. Database adaptors which support most commonly used databases:

    * DuckDB ([duckdb](https://www.github.com/veighna-global/vnpy_duckdb)): The high-performance in-process analytical database which is designed to be fast, reliable, portable, and easy to use.

6. Standarad RPC solution (vnpy_evo.rpc) for implementing complex trading systems with distributed deployments

7. High-performance charting widget (vnpy_evo.chart), which supports stream market data update

## Install

**MacOS**

Please ensure you have installed [XCode](https://developer.apple.com/xcode/) and [Homebrew](https://brew.sh/) before running the following command:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/veighna-global/vnpy_evo/HEAD/install_macos.sh)"
```

**Ubuntu**

```
sudo /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/veighna-global/vnpy_evo/HEAD/install_linux.sh)"
```

## Example

You can start running VeighNa Evo with only a few lines of code.

```Python
from vnpy_evo.event import EventEngine
from vnpy_evo.trader.engine import MainEngine
from vnpy_evo.trader.ui import MainWindow, create_qapp

from vnpy_binance import BinanceLinearGateway
from vnpy_novastrategy import NovaStrategyApp

def main():
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)

    main_engine.add_gateway(BinanceUsdtGateway)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(NovaStrategyApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()

if __name__ == "__main__":
    main()
```

Open a terminal within the directory and run the following command to start VeighNa Trader.

    python run.py

## Licence

MIT