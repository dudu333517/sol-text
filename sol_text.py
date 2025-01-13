import requests
import time

# Telegram 机器人配置
bot_token = '6929705636:AAFzoMsqr3FT_OQHoj0F1f87B6sx8F3bCZM'  # 替换为您的 Bot Token
chat_id = '-1002404846949'  # 替换为目标频道或群组的 Chat ID

def send_telegram_message(message):
    """
    发送消息到 Telegram 频道或群组
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",  # 支持 HTML 格式
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Telegram 消息发送成功")
    else:
        print(f"Telegram 消息发送失败: {response.status_code}, {response.text}")

def get_bwb_quote(usdt_amount):
    """
    获取 USDT 兑换 BWB 的报价
    """
    lamports_amount = int(usdt_amount * 10**6)  # 转换为微 USDT（整数）

    url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
        "outputMint": "6FVyLVhQsShWVUsCq2FJRr1MrECGShc3QxBwWtgiVFwK",  # BWB
        "amount": lamports_amount,  # 转换后的金额
        "slippageBps": 50,  # 0.5% 滑点
    }

    BWB_DECIMALS = 8  # 假设 BWB 的小数位精度为 8

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        out_amount = int(data['outAmount'])  # 获取目标代币的最小单位数量
        bwb_amount = out_amount / (10 ** BWB_DECIMALS)  # 转换为目标代币单位
        return bwb_amount
    else:
        print(f"Error fetching BWB quote: {response.status_code}")
        return None


def get_bgb_quote():
    """
    获取 BGB 的买一报价
    """
    url = "https://api.bitget.com/api/mix/v1/market/ticker?symbol=BGBUSDT_UMCBL"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        bestBid = float(data['data']['bestBid'])  # 获取买一价
        return bestBid
    else:
        print(f"Error fetching BGB quote: {response.status_code}")
        return None


def main():
    """
    无限循环监控报价
    """
    usdt_amount = 50  # 用户希望的 USDT 金额

    while True:
        bwb_amount = get_bwb_quote(usdt_amount)  # 获取 BWB 数量
        bestBid = get_bgb_quote()  # 获取 BGB 买一价

        if bwb_amount is not None and bestBid is not None:
            # 假设 BWB 兑换为 BGB 的比率
            bgb_amount = bwb_amount * 0.0856  # 假设兑换比例
            sell_bgb = bgb_amount * bestBid  # 卖出 BGB 的收益

            if sell_bgb >= usdt_amount + 0.7:  # 判断是否有利润
                profit = sell_bgb - usdt_amount
                message = (
                    f"<b>当前有利润！</b>\n"
                    f"数量为：<code>{bwb_amount:.8f} BWB</code>\n"
                    f"BGB 数量：<code>{bgb_amount:.8f} BGB</code>\n"
                    f"利润为：<b>{profit:.2f} USDT</b>"
                )
                print(message)
                send_telegram_message(message)
            else:
                print('没有利润')
        else:
            print("获取报价失败，无法计算利润")
            send_telegram_message("获取报价失败，无法计算利润")

        time.sleep(3)  # 等待 3 秒


if __name__ == "__main__":
    main()
