/*
 * Author: Weihao CHEN
 * Date: 2019.10.25
 */

#include <iostream>
#include <fstream>
#include <thread>
#include "include/thulac.h"
using namespace std;

char file_in[] = "../data/Sogou_0001";
char file_out_template[] = "../data/Sogou_0001_out/Sogou_0001_%d_%d";
int split_num = 3072;
int file_ptr[3072];
int total, group_len; // 对于Sogou_0001，total = 48593331
// int total = 48593331;
// int group_len = 15818;

int thread_num = 2;
vector<string> data;
thread * thread_t;

// 将所有的文件都读到内存中，比较耗时，可以优化
void procFile(const string & filename) {
    ifstream fin(filename);
    string line;
    while (getline(fin, line)) {  // 已经去除换行符
        data.push_back(line);
    }
    fin.close();
    total = data.size();
    group_len = total / split_num;
}

void trimChar(string & s, char sep = ' ') {
    int index = 0;
    if(!s.empty()) {
        while((index = s.find(sep, index)) != string::npos) {
            s.erase(index, 1);
        }
    }
}

void trimStr(string & s, const string & term) {
    int index = 0;
    int len = term.length();
    if(!s.empty()) {
        while((index = s.find(term, index)) != string::npos) {
            s.erase(index, len);
        }
    }
}

// 处理行
void procLine(FILE * fout, const THULAC & lac, int line_idx, char sep = '/') {
    string & line = data[line_idx];
    trimChar(line);
    trimStr(line, "<N>");

    THULAC_result result;
    lac.cut(line, result);

    string output_line;
    for (int i = 0; i < result.size()-1; i++) { // 去除最后一个
        output_line += result[i].first + sep + result[i].second + " ";
    }
    fprintf(fout, "%s\n", output_line.c_str());
}

void procBlock(FILE * fout, const THULAC & lac, int choose_index) {
    printf("process block: %d\n", choose_index);
    int start = group_len * choose_index;
    int end = group_len * (choose_index + 1);
    if (choose_index == split_num - 1) { // 最后一块可能比一般的块更大
        end = total;
    }
    for (int line_idx = start; line_idx < end; line_idx++) {
        procLine(fout, lac, line_idx);
    }
}

void thread_fun(const THULAC & lac, int block_start, int block_end) {
    printf("thread start: %d - %d\n", block_start, block_end);
    char tmp_filename[100];
    for (int block_idx = block_start; block_idx < block_end; block_idx++) {
        sprintf(tmp_filename, file_out_template, split_num, block_idx);
        FILE * fout = fopen(tmp_filename, "w");
        procBlock(fout, lac, block_idx);
        fclose(fout);
    }
    printf("thread exit: %d - %d\n", block_start, block_end);
}

int main() {
    
    procFile(file_in);
    printf("Input file processed: %s\n", file_in);
    cout << total << endl;

    char* model_path_char = NULL;
    char* user_specified_dict_name = NULL;
    char* input_path = NULL;
    char* output_path = NULL;

    bool useT2S = false;
    bool seg_only = false;
    bool useFilter = false;
    char sep = '/';

    THULAC lac[thread_num];
    for (int i = 0; i < thread_num; i++) {
        lac[i].init(model_path_char, user_specified_dict_name, seg_only, useT2S, useFilter, sep);
    }
    // lac.init(model_path_char, user_specified_dict_name, seg_only, useT2S, useFilter, sep);
    // lac2.init(model_path_char, user_specified_dict_name, seg_only, useT2S, useFilter, sep);
    cout << "THU lac initiated" << endl;

    thread_t = new thread[thread_num];
    int thread_task = 512;
    int offset = 2048;
    for (int i = 0; i < thread_num; i++) {
        thread_t[i] = thread(thread_fun, lac[i], offset + i*thread_task, offset + (i+1)*thread_task);
    }
    // thread_t[0] = thread(thread_fun, lac, 2022, 2035);
    // thread_t[1] = thread(thread_fun, lac2, 2035, 2048);
    for (int i = 0; i < thread_num; i++) {
        thread_t[i].join();
    }

    // thread_t[0].join();
    // thread_t[1].join();

    cout << "All finished!" << endl;
}