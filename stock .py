import openai
import os
import langchain
import requests
import json
import httpx
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAI
from langchain import PromptTemplate
from bs4 import BeautifulSoup
import baostock as bs
import pandas as pd

llm = OpenAI(
    temperature = 0.9,
    base_url="https://oneapi.xty.app/v1",
    api_key="sk-Y6Cm1t6j5chqu6ypC2C7799792Db48AbA3037c87Bb701c02",
    http_client=httpx.Client(
        base_url="https://oneapi.xty.app/v1",
        follow_redirects=True,
    ),
)


# 从baostock获取股价

def get_stock_price(ticker, start_date, end_date):
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    # 获取指数(综合指数、规模指数、一级行业指数、二级行业指数、策略指数、成长指数、价值指数、主题指数)K线数据
    # 综合指数，例如：sh.000001 上证指数，sz.399106 深证综指 等；
    # 规模指数，例如：sh.000016 上证50，sh.000300 沪深300，sh.000905 中证500，sz.399001 深证成指等；
    # 一级行业指数，例如：sh.000037 上证医药，sz.399433 国证交运 等；
    # 二级行业指数，例如：sh.000952 300地产，sz.399951 300银行 等；
    # 策略指数，例如：sh.000050 50等权，sh.000982 500等权 等；
    # 成长指数，例如：sz.399376 小盘成长 等；
    # 价值指数，例如：sh.000029 180价值 等；
    # 主题指数，例如：sh.000015 红利指数，sh.000063 上证周期 等；

    # 详细指标参数，参见“历史行情指标参数”章节；“周月线”参数与“日线”参数不同。
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    rs = bs.query_history_k_data_plus(ticker,
                                      "date,code,open,close",
                                      start_date=start_date, end_date=end_date, frequency="d")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)

    # 打印结果集
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    # 结果集输出到csv文件
    result.to_csv("D:\\history_Index_k_data.csv", index=False)
    # print(result)

    # 登出系统
    bs.logout()

    return result

stock_price = get_stock_price("sz.300476","2020-01-01", "2024-02-17")
# print(stock_price)

# 获取相关新闻的url

def get_urls():
    headers = {
        "Host": "interface.sina.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": r"http://www.sina.com.cn/mid/search.shtml?range=all&c=news&q=%E6%97%85%E6%B8%B8&from=home&ie=utf-8",
        "Cookie": "ustat=__172.16.93.31_1580710312_0.68442000; genTime=1580710312; vt=99; Apache=9855012519393.69.1585552043971; SINAGLOBAL=9855012519393.69.1585552043971; ULV=1585552043972:1:1:1:9855012519393.69.1585552043971:; historyRecord={'href':'https://news.sina.cn/','refer':'https://sina.cn/'}; SMART=0; dfz_loc=gd-default",
        "TE": "Trailers"
    }

    urls = []

    for page in range(0,1):
        params = {
            "t": "",
            "q": "胜宏科技",
            "pf": "0",
            "ps": "0",
            "page": page,
            "stime": "2023-03-30",
            "etime": "2024-02-18",
            "sort": "rel",
            "highlight": "1",
            "num": "10",
            "ie": "utf-8"
        }

        response = requests.get("https://interface.sina.cn/homepage/search.d.json?", params=params, headers=headers)
        dic = json.loads(response.text)

        for item in dic["result"]["list"]:
            urls.append(item["url"])

    return urls

if __name__ == '__main__':
    urls = get_urls()
#     print(urls)

# 通过url获取新闻内容

def get_text_from_urls(urls):
    texts = []

    for url in urls:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        soup_text = soup.get_text()

        texts.append(soup_text)

    return texts

if __name__ == '__main__':
    urls = get_urls()
    texts = get_text_from_urls(urls)

# 拆分新闻文本

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50
)

texts = str(texts)

docs = text_splitter.create_documents([texts])

print(len(docs))
# print(docs[2])

# 获取季频盈利能力

def get_financial_statements(ticker, year, quarter):
    # 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    # 查询季频估值指标盈利能力
    profit_list = []
    rs_profit = bs.query_profit_data(code=ticker, year=2017, quarter=2)
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_list.append(rs_profit.get_row_data())
    result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)

    # 登出系统
    bs.logout()

    return result_profit


sheet = get_financial_statements("sz.300476", "2023", "1")
# print(sheet)

# 构建新闻总结的prompt

template = """
%INSTRUCTIONS:
You are a financial analyst, please analyze the impact of this news on the stock market

%TEXT:
{text}
"""

prompt = PromptTemplate(
    input_variables = ["text"],
    template = template,
    verbose = True
)

# 利用langchain调用openai分析新闻

chain = load_summarize_chain(llm = llm,chain_type = 'map_reduce')
# chain.get_prompts(prompt)

output_news = chain.invoke(docs)
# print(output_news)

# 转换输出内容的类型并单独提取输出的text

output_news = str(output_news)
# print(type(output_news))

output_news_1 = output_news.split(" 'output_text': ")[len(output_news.split(" 'output_text': "))-1]
# print(output_news_1)

# 构建新闻分析的prompt

template = """
%INSTRUCTIONS:
You are a financial analyst, please analyze the impact of the content after 'output_text' on the stock market
Don't talk about Sina


%TEXT:
{text}
"""

prompt = PromptTemplate(
    input_variables = ["text"],
    template = template
)

confusing_text = output_news_1
final_prompt = prompt.format(text = confusing_text)

# 调用openai进行分析并输出

output_news_2 = llm.invoke(final_prompt)
# print(output_news_2)

# 构建股价分析的prompt

template = """
%INSTRUCTIONS:
You are a financial analyst,please analyze the data situation of this stock.
Your analyze should include the information of the stock price.
Your answer should not be shorter than 500 words.

%TEXT:
{text}
"""

prompt = PromptTemplate(
    input_variables=["text"],
    template=template
)

final_prompt = prompt.format(text=stock_price)

# 调用openai分析股价

output_stock = llm.invoke(final_prompt)
# print(output_stock)
# print(type(output_stock))

# 构建财务报表分析的prompt

template = """
%INSTRUCTIONS:
you are a professional financial analyst,
please analyze this financial statement and give your analysis and speculate on its impact on the stock price 
no less than 200 words

%TEXT:
{text}
"""

prompt = PromptTemplate(
    input_variables=["text"],
    template=template
)

final_prompt = prompt.format(text=sheet)

# 调用openai分析财务报表

output_state = llm.invoke(final_prompt)
# print(output_state)

# 将新闻分析,股价分析和报表分析整合为新的输入内容

input_text = output_stock+output_news_1+output_state

# 构建总分析的prompt

template = """
%INSTRUCTIONS:
You are a professional financial analyst and a financial consultant,
please analyze the possible impact of this information on the stock price and tell me whether I should buy or sell,
Tell me exactly whether I should buy, sell or hold
You should also give me a prediction of yours, guess its future trend


{text}
"""

prompt = PromptTemplate(
    input_variables = ["text"],
    template = template
)

final_prompt_1 = prompt.format(text = input_text)
# print(final_prompt_1)

# 调用openai进行分析并输出
output = llm.invoke(final_prompt_1)
print("BOT's Idea:")
print(output)