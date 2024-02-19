# 获取季频盈利能力

def get_financial_statements(ticker, year, quarter):
# 登陆系统
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    # 查询季频估值指标盈利能力
    profit_list = []
    rs_profit = bs.query_profit_data(code=ticker, year=2017, quarter=2)
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_list.append(rs_profit.get_row_data())
    result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)

    # 登出系统
    bs.logout()
    
    return result_profit

sheet = get_financial_statements("sz.300476","2023","1")
# print(sheet)

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
    input_variables = ["text"],
    template = template
)

final_prompt = prompt.format(text = sheet)

# 调用openai分析财务报表

output_state = llm.invoke(final_prompt)
print(output_state)
