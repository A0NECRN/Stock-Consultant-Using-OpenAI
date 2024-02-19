# Stock-Consultant-Using-OpenAI
注意事项：
1.需要将API替换为有效的OpenAI API
2."ticker", "q","start_date"," end_date","year","quater","stime","etime"等参数需要根据使用者的需求进行替换
  ticker：股票名称/股票代码
  q：搜索关键词，在本程序中一般为ticker对应的公司
  start_date：获取数据的开始时间
  end_date：获取数据的结束时间
  year：获取的报表的年份
  quarter：查询的季度
  stime：获取数据的开始时间
  etimne：获取数据的结束时间
3.主程序中的主要模块已拆分为三个单独的文件:新闻爬取与分析、股价获取与分析、报表获取与分析，导入依赖模块后可单独使用
