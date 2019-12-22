from gensim.models import Word2Vec


def w2v_cal(query, searcher, win, stopwords):
	hits = searcher.search(query, n=5*10**3)
	query_terms = query.strip().split()

	model = Word2Vec(size=100, window=win, min_count=1, iter=2, workers=4)
	sentences = []
	for hit in hits.scoreDocs:
		doc = searcher.getDoc(hit)
		line = doc.get("text")
		words = line.strip().split()
		output_line = []
		for word in words:
			parts = word.split('/')
			if parts[-1] != 'w' and len(parts) == 2:
				term, pos_t = parts
				if term and term not in stopwords:
					output_line.append(term)
		sentences.append(output_line)
	model.build_vocab(sentences)
	model.train(sentences, total_examples=model.corpus_count, epochs=model.epochs)
	try:
		ans = model.wv.most_similar(positive=query_terms, topn=20)
		return ans
	except Exception:
		return None
