#!/bin/bash
# 启动 Chrome 浏览器（调试模式）
# 这样 DrissionPage 就可以连接到你手动打开的浏览器

echo "======================================"
echo "启动调试模式浏览器"
echo "======================================"

# 检查是否有 Chrome 或 Edge 正在运行
CHROME_RUNNING=$(ps aux | grep "Google Chrome" | grep -v grep | wc -l)
EDGE_RUNNING=$(ps aux | grep "Microsoft Edge" | grep -v grep | wc -l)

if [ $CHROME_RUNNING -gt 0 ]; then
    echo "⚠️  检测到 Chrome 正在运行"
    echo "需要先关闭所有 Chrome 窗口才能以调试模式启动"
    echo "是否现在关闭 Chrome？(y/n)"
    read -t 10 choice
    if [ "$choice" == "y" ]; then
        killall "Google Chrome" 2>/dev/null
        sleep 2
        echo "✅ 已关闭 Chrome"
    else
        echo "已取消"
        exit 1
    fi
fi

echo ""
echo "启动 Chrome（调试模式）..."
echo "端口：9222"
echo "用户数据目录：/tmp/chrome_debug_profile"
echo ""

# 启动 Chrome（调试模式）
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --remote-debugging-port=9222 \
    --user-data-dir="/tmp/chrome_debug_profile" \
    > /dev/null 2>&1 &

sleep 2

# 检查是否启动成功
if ps aux | grep "remote-debugging-port=9222" | grep -v grep > /dev/null; then
    echo "✅ Chrome 已启动（调试模式）"
    echo ""
    echo "现在你可以："
    echo "1. 在浏览器中手动访问你想采集的网站"
    echo "2. 运行 'python use_my_browser.py' 连接到浏览器"
    echo ""
    echo "提示：关闭终端不会关闭浏览器"
else
    echo "❌ 启动失败"
    echo "请检查 Chrome 是否已安装在 /Applications/Google Chrome.app"
fi
