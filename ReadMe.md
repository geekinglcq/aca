# 运行说明  
## 概述
本代码是微软-清华开放学术精准画像大赛的解决方案，我们团队是这次比赛的初赛No.4，决赛No.2。  
整理后的可执行代码在`code`文件夹，其他的文件可以无视了喵。  
This repo is the No.2 solution to [Open Academic Data Challenge 2017](https://biendata.com/competition/scholar/).  
**Clean code** in the `code` folder, please ignore other files.  

## Task1:  
task1程序，使用python3，入口是`final_1.py`文件，但是由于爬虫的不稳定性，比赛中还用到了其他代码，下面会有所说明。  
+ `final_1.py` 程序入口  
+ `crawler.py` 爬虫模块，负责三部分，爬取搜索页面，爬取（认定的）主页并存储，爬取网页上的图片并存储  
+ `data_io.py` 数据读取输出模块  
+ `utility.py` 一些小工具，包括识别email的正则表达式，以及email图片的过滤器，这里设置email图片的代码没有写进`final_1.py`
+ `pagehome.py` 判断用户主页的模块，这里用到的xgb模型存储在`./model/good_model.dat`
+ `loc_pos.py` 判断用户location 和position的模块  
+ `first.py` 包含判断email，生成答案文件等函数  

`./final/`文件夹存储爬取到的主页html，`./head/`文件夹存储头像图片数据。`./output/`存储中间暂存以及最终的结果`task1_ans.txt`
对于学者的多项属性，我们实现了不同的方法，为了尽可能提高分数，会对这些进行加权模型融合，但是考虑到效率问题，不推荐这么做。

## Task2:
环境要求：  
1. python 2.7  
2. gensim  
3. Networkx  

原始文件需放在 ./raw_data 文件夹下，包含以下文件：
（注：因 papers.txt 文件较大，没有放在文件夹中，请自行添加。）
raw_data:  
1. `papers.txt`
2. `training.txt`
3. `task2_test_final.txt`
4. `labels.txt`

运行顺序：  
1. `python create_file.py`
2. `python create_citenet.py`
3. `python expand_paper.py`
4. `python expand_author_press.py`
5. `python task2_main.py`

程序结果：
 最终结果在task2_out里面，

## Task3:  
1. Python 版本：2.7.13
2. Python package: sci-learn, numpy, scipy, random, csv, pickle。均为截至2017年10月8号的最新版。task3相关代码：`task3.py`,`ILearner.py`,`Paper.py`。
3. 保证代码所在路径下有`./data/task3/`文件夹，同时，在task3文件夹中应有任务3的训练集`train.csv`、验证集`validation.csv`、训练集`test.csv`以及数据集`papers.txt`。考虑到**papers.txt文件过大**，不适宜放在邮件附件中，所以还请手动复制到相应目录。
4. 运行：在代码所在路径，执行`python task3.py`命令。
5. 结果：在上述task3文件夹中，`output3_validation.txt`是任务三的验证集输出；`output3_final.txt`是任务三的测试集输出。

