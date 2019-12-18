from flask import (
    Flask, escape, render_template, url_for, request
)

from backend import (
    lucene, Searcher, search_query, read_stopwords, read_pos_translation, pos_list_string, parse_win,
    idxdir_path, file_stopwords, file_pos
)

## html和css文件都在根目录下
app = Flask(__name__, template_folder="", static_folder="")

@app.route('/')
def index():
    query = request.args.get("query")
    print(f"### query: {query}")
    if query:
        ## ---start--- MUST add for lucene functionality
        vm_env = lucene.getVMEnv()
        vm_env.attachCurrentThread()
        ## ---end---

        win_str = request.args.get("win")
        win = parse_win(win_str)
        pos = []
        checkbox_state = {}
        if not request.args.get("cb_all"):
            for key in request.args.keys():
                if key.startswith("cb_"):
                    pos_t = key[3:]
                    pos.append(pos_t)
        for key in request.args.keys():
            if key.startswith("cb_"):
                pos_t = key[3:]
                pos.append(pos_t)
                checkbox_state[key] = True
        print(f"### pos: {pos}")
        print(f"### win: {win}")
        counter, pos_dict = search_query(query, searcher, pos, win, stopwords)
        ans = counter.most_common(n)

        ## display answers
        answer_list = []
        print(f"### get top {len(ans)} answers")
        for item in ans:
            ans = (item[0], pos_list_string(pos_dict[item[0]], pos_trans))
            answer_list.append(ans)
        return render_template("result.html", answer_list=answer_list, query_str=query, win=win if win != 0 else "", **checkbox_state)

    return render_template("index.html")


### backend init begin
print("initiating backend: lucene")
lucene.initVM()
searcher = Searcher(idxdir_path)
stopwords = read_stopwords(file_stopwords)
pos_trans = read_pos_translation(file_pos)
n = 20
print("backend initiated!")
### backend init end

if __name__ == "__main__":
    app.run()
