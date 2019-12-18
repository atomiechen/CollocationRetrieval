import os, argparse

import lucene
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
from java.nio.file import Paths


data_path = "../data"
data_prefix = "Sogou"
idxdir_path = "../lucene-idx"


class Indexer:
	def __init__(self, indexDirectoryPath):
		self.indexDirectoryPath = indexDirectoryPath
		self.indexDirectory = FSDirectory.open(Paths.get(indexDirectoryPath))
		self.indexWriter = IndexWriter(self.indexDirectory, IndexWriterConfig())

	def index_file(self, filename):
		with open(filename, 'r') as fin:
			for line_idx, line in enumerate(fin):
				line = line.strip()
				document = Document()
				ft = FieldType()
				ft.setIndexOptions(IndexOptions.DOCS_AND_FREQS)
				ft.setStored(True)  # store the field value
				document.add(Field("text", line, ft))
				self.indexWriter.addDocument(document)
		print(f"Indexing done: {filename}")
		print(f"Current number of docs: {self.indexWriter.numDocs()}")
	
	def close(self):
		self.indexWriter.close()


## 支持with语句的索引方法
class index:
	@staticmethod
	def gen_indexer(idxdirpath):
		if not os.path.exists(idxdirpath):
			os.makedirs(idxdirpath)
		indexer = Indexer(idxdirpath)
		return indexer

	def __init__(self, idxdirpath):
		self.idxdirpath = idxdirpath

	def __enter__(self):
		self.indexer = self.gen_indexer(self.idxdirpath)
		return self.indexer

	def __exit__(self, exc_type, exc_value, traceback):
		self.indexer.close()


def main(args):
	lucene.initVM()
	with index(args.index) as indexer:
		if args.file:  ## 指定一系列需要index的文件
			for filename in args.file:
				indexer.index_file(filename)
		else:  ## 指定一个需要index文件夹目录，并规定文件名前缀
			file_prefix = args.prefix
			dir_path = args.dir
			for filename in os.listdir(dir_path):
				if filename.startswith(file_prefix):  ## 文件名前缀满足要求
					filename = os.path.join(dir_path, filename)
					if not os.path.isdir(filename):  ## 不是文件夹
						indexer.index_file(filename)


if __name__ == "__main__":
	description = "Generate index for the Collocation Retrieval System, made by Weihao CHEN"
	parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)  ## help显示default
	parser.add_argument('-d', dest='dir', action='store', default=data_path, help='dir path of data to be indexed')
	parser.add_argument('-p', dest='prefix', action='store', default=data_prefix, help='prefix of file names')
	parser.add_argument('-i', dest='index', action='store', default=idxdir_path, help='path of lucene index directory')
	parser.add_argument('-f', dest='file', action='store', nargs='+', help='a list of files (override DIR)')
	args = parser.parse_args()
	main(args)
