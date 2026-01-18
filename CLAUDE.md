# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DrissionPage 是一个基于 Python 的网页自动化工具，可以：
- 控制 Chromium 内核浏览器（使用 Chrome DevTools Protocol，不依赖 webdriver）
- 发送 HTTP 请求（基于 requests）
- 两种模式可以无缝切换

支持 Python 3.6+，支持 Windows/Linux/Mac。

## 常用命令

```bash
# 安装依赖
pip install -e .

# CLI 工具 (安装后可用)
dp -p <browser_path>    # 设置浏览器路径
dp -u <user_data_path>  # 设置用户数据路径
dp -c                   # 复制默认配置文件到当前目录
dp -l <port>            # 启动浏览器，0 表示使用配置文件中的端口
```

## 代码架构

### 核心入口类 (DrissionPage/__init__.py)

- **Chromium**: 浏览器实例管理，单例模式
- **ChromiumPage**: 浏览器自动化页面对象
- **SessionPage**: HTTP 请求页面对象（基于 requests）
- **WebPage**: 混合模式，可在浏览器模式('d')和请求模式('s')之间切换

### 模块结构

```
DrissionPage/
├── _base/           # 基础类
│   ├── base.py      # BasePage 抽象基类
│   ├── chromium.py  # Chromium 浏览器管理，CDP 连接
│   └── driver.py    # WebSocket 驱动，CDP 通信
├── _pages/          # 页面对象
│   ├── chromium_base.py   # 浏览器页面基类，元素查找/等待/截图等
│   ├── chromium_page.py   # ChromiumPage 实现
│   ├── chromium_tab.py    # 标签页对象
│   ├── chromium_frame.py  # iframe 处理
│   ├── session_page.py    # SessionPage 实现
│   ├── web_page.py        # WebPage 混合模式实现
│   └── mix_tab.py         # 混合模式标签页
├── _elements/       # 元素对象
│   ├── chromium_element.py  # 浏览器元素，支持点击/输入/属性获取等
│   ├── session_element.py   # 请求模式元素（基于 lxml 解析）
│   └── none_element.py      # 空元素（未找到时返回）
├── _configs/        # 配置管理
│   ├── chromium_options.py  # 浏览器启动配置
│   ├── session_options.py   # 请求会话配置
│   └── configs.ini          # 默认配置文件
├── _units/          # 功能单元
│   ├── actions.py    # 动作链（鼠标/键盘操作）
│   ├── clicker.py    # 点击器
│   ├── waiter.py     # 等待器（元素出现/消失/URL变化等）
│   ├── scroller.py   # 滚动器
│   ├── setter.py     # 属性设置器
│   ├── listener.py   # 网络监听器
│   └── downloader.py # 下载管理器
├── _functions/      # 工具函数
│   ├── locator.py   # 定位语法解析（核心）
│   ├── keys.py      # 键盘按键定义
│   ├── cookies.py   # Cookie 处理
│   └── cli.py       # 命令行工具入口
├── common.py        # 公共导出（Actions, Keys, Settings 等）
└── errors.py        # 自定义异常类
```

### 定位语法 (_functions/locator.py)

DrissionPage 使用简化的定位语法，而非标准 XPath/CSS：

```python
# 属性定位
'@id=value'          # 单属性精确匹配
'@id:value'          # 单属性模糊匹配
'@@id=v1@@class=v2'  # 多属性 AND
'@|id=v1@|class=v2'  # 多属性 OR
'@!id=value'         # 属性否定

# 文本定位
'text=精确文本'
'text:模糊文本'
'text^开头文本'
'text$结尾文本'

# 标签定位
'tag:div'
'tag:div@class=foo'

# 也支持标准语法
'xpath://div[@id="foo"]'
'css:div.class'
```

### 关键设计模式

1. **单例模式**: Chromium 和 ChromiumPage 使用单例，相同浏览器实例会返回已有对象
2. **延迟初始化**: 属性如 `set`, `wait` 在首次访问时才创建
3. **自动重试**: 内置重试机制，配置在 `retry_times` 和 `retry_interval`
4. **跨 iframe 查找**: 可以直接在整个文档中查找元素，无需切换 iframe

## 配置文件

配置文件为 INI 格式，可通过 `dp -c` 复制到当前目录，或使用 `ChromiumOptions`/`SessionOptions` 动态配置：

```python
from DrissionPage import ChromiumOptions
co = ChromiumOptions()
co.set_browser_path('/path/to/chrome')
co.set_local_port(9222)
co.save()  # 保存到默认配置
```
