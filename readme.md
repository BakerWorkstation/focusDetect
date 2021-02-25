## 集中检测程序
*****
#### conf -> 配置文件目录
    system.ini  主配置文件
*****
#### env -> 依赖模块目录
    linux (已启用)
    windows
*****
#### libs -> 工具目录

*****
#### logs -> 日志目录
    kafkaData  从KAFKA消费日志目录
*****
#### module -> 模块工作目录
    kafkaConsume.py   从KAFKA拉取异常事件数据
    demo.py   模板文件
*****
#### services -> 服务文件目录
    编写service文件，使服务开机自启
*****
#### test -> 测试目录  
    单元测试、集成测试
*****
#### utils -> 通用函数目录  
    loadConf.py  解析配置文件
    log.py    输出日志信息到文件
    pgConnect.py  连接postgresql数据库，返回连接句柄
    redisConnect.py  连接redis数据库，返回连接句柄
    similarity.py  计算数据相似度，返回相似系数
*****
