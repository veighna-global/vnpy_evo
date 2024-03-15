# By Traders, For Traders.

<p align="center">
  <img src ="https://github.com/veighna-global/vnpy_evo/blob/dev/logo.png" width="300" height="300"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-0.1.0-blueviolet.svg"/>
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

        * Bybit ([bybit](https://www.github.com/veighna-global/vnpy_bybit)): Spot/Perpetual/Futures

        * Deribit ([deribit](https://www.github.com/veighna-global/vnpy_deribit)): Perpetual/Futures/Option

    * Special Applications

        * RPC service ([rpc](https://www.github.com/vnpy/vnpy_rpcservice)): inter-process communication interface for distributed architecture

3. Applications for various quantitative strategies (vnpy_evo.app).

    * [cta_strategy](https://www.github.com/vnpy/vnpy_ctastrategy): CTA strategy engine module, which allows users to perform fine-grained control over the withdrawal behavior of delegates during the operation of CTA-type strategies while maintaining ease of use (reducing trading slippage, implementing high-frequency strategies)

    * [cta_backtester](https://www.github.com/vnpy/vnpy_ctabacktester): CTA strategy backtester module, no need to use Jupyter Notebook, directly use the graphical interface to directly carry out strategy backtester analysis, parameter optimization and other related work

    * [spread_trading](https://www.github.com/vnpy/vnpy_spreadtrading): spread trading module, support custom spreads, real-time calculation of spread quotes and positions, support semi-automatic spread algorithm trading and fully automatic spread strategy trading two modes

    * [option_master](https://www.github.com/vnpy/vnpy_optionmaster): option trading module, designed for the domestic options market, supports a variety of option pricing models, implied volatility surface calculation, Greek value risk tracking and other functions

    * [portfolio_strategy](https://www.github.com/vnpy/vnpy_portfoliostrategy): portfolio strategy module, designed for trading multi-contract quantitative strategies (Alpha, option arbitrage, etc.) at the same time, providing historical data backtesting and live automatic trading functions

    * [algo_trading](https://www.github.com/vnpy/vnpy_algotrading): algorithm trading module, providing a variety of commonly used intelligent trading algorithms: TWAP, Sniper, Iceberg, BestLimit, etc.

    * [script_trader](https://www.github.com/vnpy/vnpy_scripttrader): script strategy module, designed for multi-standard portfolio trading strategies, also can be directly in the command line to achieve REPL instructions in the form of trading, does not support the backtest function

    * [paper_account](https://www.github.com/vnpy/vnpy_paperaccount): Simulation trading module, pure localization of simulation trading functions, based on the real-time quotes obtained from the trading interface for commission aggregation, providing commission transaction push and position records

    * [chart_wizard](https://www.github.com/vnpy/vnpy_chartwizard): K-line chart module, based on RQData data service (futures) or trading interface (digital currency) to obtain historical data, and combined with Tick push to display real-time market changes

    * [portfolio_manager](https://www.github.com/vnpy/vnpy_portfoliomanager): portfolio module, for all kinds of fundamental trading strategies, based on separate strategy sub-accounts, providing automatic tracking of trading positions and real-time profit and loss statistics

    * [rpc_service](https://www.github.com/vnpy/vnpy_rpcservice): RPC service module, allowing a VeighNa Trader process to be started as a server, serving as a unified routing channel for quotes and trades, allowing multiple clients to connect at the same time, realizing a multi-process distributed system

    * [data_manager](https://www.github.com/vnpy/vnpy_datamanager): Historical data management module, view the existing data in the database through the tree directory, select any time period data to view the field details, support CSV file data import and export

    * [data_recorder](https://www.github.com/vnpy/vnpy_datarecorder): Quotes recording module, based on the graphical interface for configuration, according to the demand for real-time recording Tick or K-line quotes to the database, for strategy backtesting or live initialization

    * [excel_rtd](https://www.github.com/vnpy/vnpy_excelrtd): Excel RTD (Real Time Data) real-time data service, based on pyxll module to achieve real-time push updates of various data (quotes, contracts, positions, etc.) in Excel

    * [risk_manager](https://www.github.com/vnpy/vnpy_riskmanager): risk management module, providing statistics and restrictions on rules including trade flow control, number of orders placed, active orders, total number of cancelled orders, etc., effectively realizing front-end risk control functions
    
    * [web_trader](https://www.github.com/vnpy/vnpy_webtrader): The web service module is designed according to the requirements of B-S architecture, and implements a web server that provides active function call (REST) and passive data push (WebSocket)


4. Standard network clients for connecting to exchange APIs:
    
    * REST Client ([rest](https://www.github.com/vnpy/vnpy_rest)): The high-performance rest API client based on coroutine process asynchronous IO which adopts the programming model of event message cycle to support the sending of high concurrent real-time transaction requests
    
    * Websocket Client ([websocket](https://www.github.com/vnpy/vnpy_websocket)): The high-performance websocket API client based on coroutine process asynchronous IO supports which sharing event loops with REST Client to avoid multi-threaded performance loss caused by GIL


5. Event processing engine (vnpy_evo.event), which is the core of event-driven trading program

6. Database adaptors which support most commonly used databases:

    * SQL

        * SQLite ([sqlite](https://www.github.com/vnpy/vnpy_sqlite)): lightweight single file database, no need to install and configure data service programs, default option of vnpy_evo.py, suitable for novice users

        * MySQL ([mysql](https://www.github.com/vnpy/vnpy_mysql)): the world's most popular open source relational database, extremely rich documentation, and can replace other high NewSQL compatible implementations (such as TiDB)

        * PostgreSQL ([postgresql](https://www.github.com/vnpy/vnpy_postgresql)): more feature-rich open source relational database, support for new features through extension plug-ins, only recommended for skilled users

    * NoSQL

        * MongoDB ([mongodb](https://www.github.com/vnpy/vnpy_mongodb)): non-relational database based on distributed file storage (bson format), built-in memory cache of hot data provides faster read and write speeds
        
        * InfluxDB ([influxdb](https://www.github.com/vnpy/vnpy_influxdb)): non-relational database specially designed for time-series data, columnar data storage provides high read/write efficiency and peripheral analysis applications
        
        * LevelDB ([leveldb](https://www.github.com/vnpy/vnpy_leveldb)): The high-performance key/value database launched by Google which realizes the process memory storage engine based on LSM algorithm, and supports billions of levels of massive data

7. Standarad RPC solution (vnpy_evo.rpc) for implementing complex trading systems with distributed deployments

8. High-performance charting widget (vnpy_evo.chart), which supports stream market data update

## Install

Download the latest version from [here](https://github.com/veighna_global/vnpy_evo/releases), unzip it and run the following command to install it.

**Windows**

```
install.bat
```

**Ubuntu**

```
bash install.sh
```

**Macos**

```
bash install_osx.sh
```

## Example

You can start running VeighNa Evo with only a few lines of code.

```Python
from vnpy_evo.event import EventEngine
from vnpy_evo.trader.engine import MainEngine
from vnpy_evo.trader.ui import MainWindow, create_qapp

from vnpy_binance import BinanceUsdtGateway
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctabacktester import CtaBacktesterApp

def main():
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    
    main_engine.add_gateway(BinanceUsdtGateway)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()

if __name__ == "__main__"。
    main()
```

Open a terminal within the directory and run the following command to start VeighNa Trader.

    python run.py

## Licence

MIT