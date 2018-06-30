# KDDcup 最终报告 

计52 沈俊贤 2015011258

计52 王纪霆 2015011251

## 小组成员分工与工作量 

#### 沈俊贤

完成了数据预处理、xgboost模型构建、生成xgboost版本的submission部分

#### 王纪霆

(to be continued)

## 数据预处理

- 在对原始数据进行下载之后，我们首先通过数据分类，将全年所有站点的数据分割成每个站点一个文件，再对每个文件进行相应的处理。
- 在对缺失数据进行处理的过程中，我们对连续缺失量较大的数据，采取填入过去一段时间的平均值的方法；对连续缺失量较小的数据，填入上一个时间内的对应数据
- 在处理的过程中，我们通过将“过去某一段时间的平均值”进行计算，使得提取出了“时序”这样一个隐藏特征，通过对“过去一个月”、“过去两周”、“过去一周”、“过去三天”、“过去一天”、“过去12小时”、“过去6小时 ”、“过去3小时”这些特征的计算，增强了对时序的利用。
- 在计算平均值的时候，我们采用了简单的算术平均值的方法。在计算风速的时候，考虑到风速和风向两个因素实际上同时决定了“风”这个向量，所以我们在计算风的时候，将风速和风向两个因素都考虑了进去，作为一个向量，进行向量的算术平均数计算，最后还原成风速和风向 。

## 模型构建中所作的尝试 

### 决策树相关

因为xgboost作为决策树的工具包，既满足了我们想要使用决策树对数据进行特征提取的想法，也满足了对大量数据加速处理从而不至于让训练时间过慢，从而影响参数的调试。

在使用xgboost的时候 ，通过对xgboost的`eta`参数和`maxdepth`参数进行有间隔遍历，测试的时候使用了5月6日的数据，最后得到在`eta`为`0.4`，`maxdepth`为`10`的时候效果最好。

### 加速决策 

我们在实践中发现，对某一个特定的空气监测站站点来说，最具有代表性的气象数据可以局限在距离它最近的几个站点的数据中，一方面这几个数据最具有代表性；另外一方面距离它较远的数据失去了和它的数据相关性。所以我们在进行决策的时候，对于空气监测站来说，只选取了离它最近的四个气象监测站的站点数据，既保证了最后预测的准确性，同时也保证了决策在较短的时间内完成训练和预测。

## 使用的工具

- xgboost
- tensorflow
- (To be continued)

## 最终采用的方案

最终我们采用了xgboost（to be continued）

##  代码的组织结构

(to be continued)
