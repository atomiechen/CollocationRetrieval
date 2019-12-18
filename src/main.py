import os, argparse, math
from collections import Counter

import lucene
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, BooleanQuery
from org.apache.lucene.queryparser.classic import QueryParser
from java.nio.file import Paths


idxdir_path = "../lucene-idx"
file_stopwords = "../data/stopwords.txt"
file_pos = "../data/pos.txt"


class Searcher:
	def __init__(self, indexDirectoryPath):
		self.indexDirectoryPath = indexDirectoryPath
		self.indexDirectory = FSDirectory.open(Paths.get(indexDirectoryPath))
		self.indexSearcher = IndexSearcher(DirectoryReader.open(self.indexDirectory))
		self.queryParser = QueryParser("text", StandardAnalyzer())
	
	def search(self, searchQuery, n=1024):
		query = self.queryParser.parse(searchQuery)
		if n <= 0:
			n = BooleanQuery.getMaxClauseCount()
		return self.indexSearcher.search(query, n)
	
	def getDoc(self, scoreDoc):
		return self.indexSearcher.doc(scoreDoc.doc)


## 窗口大小win至少为3，偶数向下变成奇数
def proc_line(line, counter, pos_dict, stopwords, pos=[], win=0, query_terms=None):
	words = line.split()
	half = len(words)
	if win >= 3:  ## 设置了窗口大小
		half = int((win-1) / 2)

	idx_list = []
	## 记录检索词的索引位置
	for idx, word in enumerate(words):
		for term in query_terms:
			if term in word:
				idx_list.append(idx)
				break  # 索引在列表中添加一次即可
	## 筛选出合适距离的候选词
	for idx, word in enumerate(words):
		for idx_fixed in idx_list:
			if abs(idx - idx_fixed) <= half:
				parts = word.split('/')
				## 忽略标点
				if parts[-1] != 'w' and len(parts) == 2:
					term, pos_t = parts
					if term and term not in stopwords:
						if not pos or pos_t in pos:
							counter.update([term])
							if term in pos_dict:
								pos_dict[term].add(pos_t)
							else:
								pos_dict[term] = set([pos_t])
				break

def read_stopwords(filename):
	stopwords = []
	try:
		with open(filename, 'r') as fin:
			for line in fin:
				stopwords.append(line.strip())
	except:
		print("stopwords not set!")
	return stopwords

def read_pos_translation(filename):
	pos_trans = {}
	try:
		with open(filename, 'r') as fin:
			all = fin.read()
		items = all.split()
		for item in items:
			eng, chn = item.split('/')
			pos_trans[eng] = chn
	except:
		print("part of speech translation not set!")
	return pos_trans

def search_query(query, searcher, pos=[], win=5, stopwords=[]):
	hits = searcher.search(query)
	query_terms = query.strip().split()

	counter = Counter()
	pos_dict = {}
	print(f"hit docs: \t{len(hits.scoreDocs)}")
	for hit in hits.scoreDocs:
		doc = searcher.getDoc(hit)
		line = doc.get("text")
		proc_line(line, counter, pos_dict, stopwords, pos=pos, win=win, query_terms=query_terms)
	## 还需要去掉用来搜索的term
	for term in query_terms:
		del counter[term]
		if term in pos_dict:
			del pos_dict[term]

	print(f"candidates: \t{len(counter)}")
	return counter, pos_dict

def parse_pos(pos):
	pos = pos.split('/')
	pos = [item for item in pos if item]
	if pos:
		print(f"chosen part of speech: {pos}")
	else:
		print("no part of speech specified, all will be accepted")
	return pos

def parse_win(win):
	valid = True
	try:
		win = int(win)
		if win < 3:
			valid = False
	except:
		valid = False
	if valid:
		print(f"current window size: {win}")
	else:
		win = 0
		print(f"INVALID window size, unlimit window size constraint")
	return win

def parse_n(n):
	valid = True
	try:
		n = int(n)
		if n < 1:
			valid = False
	except:
		valid = False
	if valid:
		print(f"set top n to: {n}")
	else:
		n = 20
		print(f"INVALID n number, set to {n}")
	return n

def pos_list_string(pos_list, pos_trans):
	ans = ""
	for pos in pos_list:
		if pos in pos_trans:
			ans += pos_trans[pos]
		else:
			ans += pos
		ans += " "
	return ans

def main(args):
	lucene.initVM()
	searcher = Searcher(args.index)
	pos = parse_pos(args.pos)
	win = parse_win(args.win)
	stopwords = read_stopwords(file_stopwords)
	pos_trans = read_pos_translation(file_pos)

	n = 20
	quit_words = ["q", "quit", "exit"]

	while True:
		query = input("Input query (type ? to get command list)>>> ")
		# query = "清华"
		if query.startswith("?"):
			print()
			print("type <?> to get this help")
			print("type <p> for part of speech")
			print("type <w> for window size")
			print("type <n> for top n answers")
			print("type <q>, <quit> or <exit> to exit")
			print()
			continue

		if query == "p":
			pos = input("Input part of speech (e.g. v/n/a)>>> ")
			pos = parse_pos(pos)
			continue
		elif query == 'w':
			win = input("Input window size (3 at least)>>> ")
			win = parse_win(win)
			continue
		elif query == 'n':
			n = input("Input top n number (must be positive)>>> ")
			n = parse_n(n)
		elif query in quit_words:
			return
		elif query:
			counter, pos_dict = search_query(query, searcher, pos, win, stopwords)
			ans = counter.most_common(n)
			print(f"top {len(ans)} answers:")
			for item in ans:
				print(f"\t{item[0]}     \t\t    {pos_list_string(pos_dict[item[0]], pos_trans)}")
		print()


if __name__ == '__main__':
	description = "A Collocation Retrieval System, made by Weihao CHEN"
	parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)  ## help显示default
	parser.add_argument('-i', dest='index', action='store', default=idxdir_path, help='path of lucene index directory')
	parser.add_argument('-p', dest='pos', action='store', default="", help='part of speech: v/n/a/...')
	parser.add_argument('-w', dest='win', action='store', type=int, default=5, help='window size, at least 3 to be valid')
	args = parser.parse_args()
	main(args)
