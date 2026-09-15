import os
import ast
import operator
import json

from dotenv import load_dotenv
from tavily import TavilyClient
SEARCH_MAX_RESULTS = 5
SEARCH_SNIPPET_CHARS = 1200
MAX_WEB_CHARS = 12000
RESEARCH_SOURCE_COUNT = 3
RESEARCH_SEARCH_RESULTS = 6
RESEARCH_MAX_CHARS_PER_SOURCE = 6000

load_dotenv()

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

def search_tool(query):

    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=5
    )

    results = []

    for item in response.get("results", []):

        content = item.get(
            "content",
            ""
        )

        # 每条搜索摘要最多保留 1200 个字符
        content = content[:1200]

        results.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": content
            }
        )

    if not results:
        return "没有搜索到相关结果"

    return json.dumps(
        results,
        ensure_ascii=False,
        indent=2
    )

def read_url_tool(url):

    response = tavily_client.extract(
        urls=[url],
        extract_depth="basic"
    )

    results = response.get(
        "results",
        []
    )

    if not results:
        return "无法读取这个网页"

    page = results[0]

    content = page.get(
        "raw_content",
        ""
    )

    # 限制正文长度
    if len(content) > MAX_WEB_CHARS:
        content = content[:MAX_WEB_CHARS]

    result = {
        "url": page.get("url", url),
        "content": content
    }

    return json.dumps(
        result,
        ensure_ascii=False
    )

def research_tool(topic):

    # =========================
    # 1. 先搜索候选来源
    # =========================

    search_response = tavily_client.search(
        query=topic,
        search_depth="basic",
        max_results=RESEARCH_SEARCH_RESULTS
    )

    search_results = search_response.get(
        "results",
        []
    )

    if not search_results:
        return "没有搜索到可用资料"


    # =========================
    # 2. 选择不同的 URL
    # =========================

    selected_sources = []
    seen_urls = set()

    for item in search_results:

        url = item.get("url", "")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        selected_sources.append(
            {
                "title": item.get(
                    "title",
                    ""
                ),
                "url": url
            }
        )

        if (
            len(selected_sources)
            >= RESEARCH_SOURCE_COUNT
        ):
            break


    if not selected_sources:
        return "没有找到可读取的网页"


    # =========================
    # 3. 一次读取多个网页
    # =========================

    urls = [
        source["url"]
        for source in selected_sources
    ]

    extract_response = tavily_client.extract(
        urls=urls,
        extract_depth="basic"
    )

    extracted_results = (
        extract_response.get(
            "results",
            []
        )
    )


    # =========================
    # 4. 整理正文
    # =========================

    pages_by_url = {}

    for item in extracted_results:

        url = item.get(
            "url",
            ""
        )

        content = item.get(
            "raw_content",
            ""
        )

        # 控制每篇文章长度
        content = content[
            :RESEARCH_MAX_CHARS_PER_SOURCE
        ]

        pages_by_url[url] = content


    # =========================
    # 5. 最终返回 3 个来源
    # =========================

    research_results = []

    for source in selected_sources:

        url = source["url"]

        research_results.append(
            {
                "title": source["title"],
                "url": url,
                "content": pages_by_url.get(
                    url,
                    ""
                )
            }
        )


    return json.dumps(
        research_results,
        ensure_ascii=False,
        indent=2
    )
def calculator_tool(expression):
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def calculate(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("只支持数字")

        if isinstance(node, ast.BinOp):
            left = calculate(node.left)
            right = calculate(node.right)

            op_type = type(node.op)

            if op_type not in operators:
                raise ValueError("不支持这种运算符")

            return operators[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            value = calculate(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

        raise ValueError("不支持的计算表达式")

    tree = ast.parse(
        expression,
        mode="eval"
    )

    return calculate(tree.body)


TOOLS = [
    {
        "type": "function",
        "name": "search_tool",
        "description": (
            "用于搜索互联网最新信息、新闻、"
            "网页资料和实时信息。"
            "当用户询问今天、最近、最新、实时内容时，"
            "优先使用这个工具。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "需要在互联网上搜索的问题或关键词"
                    )
                }
            },
            "required": [
                "query"
            ]
        }
    },

    {
        "type": "function",
        "name": "read_url_tool",
        "description": (
            "用于读取指定网页的详细正文。"
            "当 search_tool 已经找到相关网页，"
            "但仅凭搜索摘要不足以回答问题时，"
            "使用这个工具读取网页正文。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": (
                        "需要读取正文的网页 URL"
                    )
                }
            },
            "required": [
                "url"
            ]
        }
    },

    {
        "type": "function",
        "name": "research_tool",
        "description": (
            "用于需要多来源研究、比较、分析、"
            "事实核查或深度总结的任务。"
            "该工具会自动搜索多个来源，"
            "并读取多个网页内容进行综合研究。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": (
                        "需要进行多来源研究的主题或问题"
                    )
                }
            },
            "required": [
                "topic"
            ]
        }
    },

    {
        "type": "function",
        "name": "calculator_tool",
        "description": (
            "用于处理数学计算任务，"
            "例如加法、减法、乘法和除法。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "需要计算的数学表达式，"
                        "例如 123 * 456"
                    )
                }
            },
            "required": [
                "expression"
            ]
        }
    }
]