# Agent 工具使用说明

当前 AI Pilot Agent 支持多类数据分析工具。

对于渠道转化数据，可以使用渠道分析工具，计算访问量、注册量、支付量、注册率、支付率和注册到支付转化率。

对于股票价格数据，可以使用金融分析工具，计算总收益率、年化波动率、最大回撤和夏普比率。

对于均线策略，可以运行均线回测，生成回测报告，生成回测图表，扫描不同均线参数组合，并生成策略研究总结。

如果用户要求生成 MA5-MA10 回测报告，应优先选择 generate_backtest_report 工具，并传入 short_window=5 和 long_window=10。

如果用户要求生成参数扫描图表，应优先选择 generate_parameter_scan_chart 工具，并根据用户关注的指标选择 sort_by 参数。

当用户说“收益率”时，sort_by 可以使用 strategy_total_return。

当用户说“夏普”时，sort_by 可以使用 sharpe_ratio。

当用户说“最大回撤”时，sort_by 可以使用 max_drawdown。

当用户输入不属于已有工具能力范围时，Agent 应该说明当前没有合适工具，而不是强行调用工具。