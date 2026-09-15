from agent.core import run_agent


# =========================
# 1. 对话历史
# =========================

history = [
    {
        "role": "system",
        "content": (
           "你是一个 AI Research Agent。"
            "当用户询问最新、今天、最近、新闻或实时信息时，"
            "先调用 search_tool 搜索互联网。"
            "对于需要研究、判断、总结的任务，"
            "不要只依赖单一来源。"
            "应优先选择 2 到 3 个高相关、可信的来源，"
            "必要时分别调用 read_url_tool 阅读正文。"
            "最后对比不同来源，说明共同结论、重要差异和来源链接。"
            "需要数学计算时使用 calculator_tool。"
        )
    }
]


# =========================
# 2. 主程序
# =========================

print("=== DeepSeek Agent ===")

print(
    "输入“退出”即可结束程序。"
)


while True:

    user_input = input(
        "\n请输入任务："
    ).strip()


    # 防止直接按 Enter
    if not user_input:

        print("请输入内容。")

        continue


    # 退出
    if user_input == "退出":

        print("Agent 已退出")

        break


    try:

        answer = run_agent(
            user_input,
            history
        )


        print("\nAgent：")
        print(answer)


        # =========================
        # 保存这一轮聊天记录
        # =========================

        history.append(
            {
                "role": "user",
                "content": user_input
            }
        )


        history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        # =========================
        # 防止 history 无限增长
        #
        # system + 最近 8 条消息
        # =========================

        history = (
            [history[0]]
            + history[-8:]
        )


    except Exception as error:

        print(
            "\nAgent 运行发生错误："
        )

        print(error)