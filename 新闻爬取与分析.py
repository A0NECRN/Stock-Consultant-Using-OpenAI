# 获取相关新闻的url

def get_urls():
    agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edge/44.18363.8131',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    ]
    random_agent = random.choice(agent_list)
    headers = {
        "Host": "interface.sina.cn",
        "User-Agent": random_agent,
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": r"http://www.sina.com.cn/mid/search.shtml?range=all&c=news&q=%E6%97%85%E6%B8%B8&from=home&ie=utf-8",
        "Cookie": "ustat=__172.16.93.31_1580710312_0.68442000; genTime=1580710312; vt=99; Apache=9855012519393.69.1585552043971; SINAGLOBAL=9855012519393.69.1585552043971; ULV=1585552043972:1:1:1:9855012519393.69.1585552043971:; historyRecord={'href':'https://news.sina.cn/','refer':'https://sina.cn/'}; SMART=0; dfz_loc=gd-default",
        "TE": "Trailers"
    }

    urls = []

    for page in range(0, 1):
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

# print(len(docs))
# print(docs[2])

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
print(output_news)
