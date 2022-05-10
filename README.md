# VeighNa框架的CryptoCurrency扩展模块

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-0.1.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.7|3.8|3.9|3.10-blue.svg" />
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>


关于使用VeighNa框架进行Crypto交易的话题，新开了一个[Github Discussions论坛](https://github.com/vn-crypto/vnpy_crypto/discussions)，欢迎通过这里来进行讨论交流。

## 说明

针对CryptoCurrency相关交易功能的VeighNa开源量化交易平台扩展插件。

目前主要添加了对于Crypto交易所的枚举值支持：

* Exchange（位于vnpy.trader.constant)
    * BINANCE
    * BITFINEX
    * BITSTAMP
    * BYBIT
    * COINBASE
    * DERIBIT
    * DYDX
    * FTX
    * GATEIO
    * HUOBI
    * OKEX

## 安装

安装需要基于3.0.0版本的【[**VeighNa**](https://github.com/vnpy/vnpy)】。


下载解压后在cmd中运行：

```
python setup.py install
```


## 使用

在需要加载Crypto交易接口的启动脚本run.py文件的头部，加上如下代码即可：

```
import vnpy_crypto
vnpy_crypto.init()
```

上述代码会自动替换原生框架中的Exchange等枚举值，实现对Crypto交易所的支持。
