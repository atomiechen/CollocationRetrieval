import thulac   
import time

thu1 = thulac.thulac(T2S=True)  #默认模式

file_name = 'Sogou_0001'
split_num = 3072 # 打算分成多少段

# 读取文件
f = open('../data/' + file_name,'r')
tmp = f.readlines()
f.close()
# 计算分块
total = len(tmp)
group_len = int(total / split_num)

# 处理一个分块
def proc_index(choose_index):
    global file_name, split_num, total, group_len
    print("proc_index begin: {}".format(choose_index))

    fw = open('../seg_data/' + file_name + '_' + str(split_num) + '_' + str(choose_index),'w')
    start = group_len * choose_index
    end = group_len * (choose_index + 1)
    if split_num - 1 == choose_index:
        end = total
    # print(file_name)

    time_start = time.time()
    for i, line in enumerate(tmp[int(start):int(end)]):
        if i % 1000 == 0:
            print(str(i / group_len) + ' percent have done')
        line = line.strip()
        line = line.replace(' ','')
        line = line.replace('<N>','0')
        line = thu1.cut(line, text=False)
        re = ""
        for item in line:
            if item[0] != '':
                re = re + item[0] + '/' + item[1] + ' '
        fw.write(re  + '\n')
    fw.close()
    print("proc_index exit: {}, total cost: {}".format(choose_index, time.time()-time_start))


for i in range(2019, 2048):
    proc_index(i)

