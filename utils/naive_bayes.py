'''
Author: your name
Date: 2020-12-24 10:43:34
LastEditTime: 2020-12-30 13:38:01
LastEditors: Please set LastEditors
Description: 有监督学习  朴素贝叶斯分类
FilePath: /opt/focusDetect/utils/naive_bayes.py
'''
import math

class NB():
    def __init__(self):
        self.cla_all_num = 0
        self.cla_num = {}
        self.cla_tag_num = {}
        self.landa = 1  # 拉普拉斯修正值

    def train(self, taglist, cla):  # 训练，每次插入一条数据
        # 插入分类
        self.cla_all_num += 1
        if cla in self.cla_num:  # 是否已存在该分类
            self.cla_num[cla] += 1
        else:
            self.cla_num[cla] = 1
        if cla not in self.cla_tag_num:
            self.cla_tag_num[cla] = {}  # 创建每个分类的标签字典
        # 插入标签
        tmp_tags = self.cla_tag_num[cla]  # 浅拷贝，用作别名
        for tag in taglist:
            if tag in tmp_tags:
                tmp_tags[tag] += 1
            else:
                tmp_tags[tag] = 1

    def P_C(self, cla):  # 计算分类 cla 的先验概率
        return self.cla_num[cla] / self.cla_all_num

    def P_all_C(self):  # 计算所有分类的先验概率
        tmpdict = {}
        for key in self.cla_num.keys():
            tmpdict[key] = self.cla_num[key] / self.cla_all_num
        return tmpdict

    def P_W_C(self, tag, cla):  # 计算分类 cla 中标签 tag 的后验概率
        tmp_tags = self.cla_tag_num[cla]  # 浅拷贝，用作别名
        if tag not in self.cla_tag_num[cla]:
            return self.landa / (self.cla_num[cla] + len(tmp_tags) * self.landa)  # 拉普拉斯修正
        return (tmp_tags[tag] + self.landa) / (self.cla_num[cla] + len(tmp_tags) * self.landa)

    def test(self, test_tags):  # 测试
        res = ''
        res_P = None
        for cla in self.cla_num.keys():
            log_P_W_C = 0
            for tag in test_tags:
                log_P_W_C += math.log(self.P_W_C(tag, cla))
            tmp_P = log_P_W_C + math.log(self.P_C(cla))  # P(w|Ci) * P(Ci)
            if res_P is None:
                res = cla
                res_P = tmp_P
            if tmp_P > res_P:
                res = cla
                res_P = tmp_P
        return res

    def set_landa(self, landa):
        self.landa = landa

    def clear(self):  # 重置模型
        self.cla_all_num = 0
        self.cla_num.clear()
        self.cla_tag_num.clear()


if __name__ == '__main__':
    nb = NB()  # 生成模型
    # 训练模型
    # 年龄，收入，是否学生，信用等级  --->  是否买了电脑
    nb.train([1087518,  921646,  252.0904033379694, 437.00616405879566, 1460,  1460,  1199,  617,   1924,   0,  2384, 2102], 'true')
    nb.train([1619180,	933197	,574.7887824	,401.5477625,	1460	,1460	,1296	,655,	3	,0	,2809	,2317], 'false')
    nb.train([1456776,	929669,	531.670073	,418.2046784	,1460	,1460	,	680	,2	,0	,2734	,2218], 'false')
    nb.train([1209451,  924066,	485.5283019,	424.6626838,	1460,	1460,	1203,	617	,5	,0,	2483,	2168], 'false')
    nb.train([1381348,	958404,	510.287403,	408.1788756,	1460,	1460	,1222	,647,	12,	0	,2675	,2323], 'false')
    nb.train([1088576,	1034091,	417.398773,	436.878327,	1460,	1460,	1263,	712,	17,	0,	2571,	2334], 'false')
    nb.train([1229811,	1549883,	415.6171004,	539.0897391,	1460,	1460,	1328,	749,	22,	0,	2909,	2827], 'false')
    nb.train([1324549,	926704,	507.4900383,	428.6327475,	1460,	1460,	1214,	629	,3,	0	,2601,	2153], 'false')
    nb.train([49374,	   44046,	   440.8392857,	440.46,	   1460,	1460,	56,	   29,	   0	,0,	112,	100], 'false')
    
    # nb.train(['<30', '高', '否', '一般'], '1')
    # nb.train(['<30', '高', '否', '好'], '2')
    # nb.train(['30-40', '高', '否', '一般'], '3')
    # nb.train(['>40', '中', '否', '一般'], '3')
    # nb.train(['>40', '低', '是', '一般'], '2')
    # nb.train(['>40', '低', '是', '好'], '1')
    # nb.train(['30-40', '低', '是', '好'], '2')
    # nb.train(['<30', '中', '否', '一般'], '3')
    # nb.train(['<30', '低', '是', '一般'], '4')
    # nb.train(['>40', '中', '是', '一般'], '2')
    # nb.train(['<30', '中', '是', '好'], '3')
    # nb.train(['30-40', '中', '否', '好'], '3')
    # nb.train(['30-40', '高', '是', '一般'], '1')
    # nb.train(['>40', '中', '否', '好'], '2')   
    # testdata = [469501,  401933,  309.0855826201448  ,     440.2332968236583  ,     1460  ,  1460  ,  518   ,  266 ,    482 ,    0    ,   1035  ,  909]
    testdata = [1075740,	932528,	422.8537736	,420.0576577,	1460,	1460,	1291	,719,	3	,0	,2529	,2211]
    print('测试结果：', nb.test(testdata))