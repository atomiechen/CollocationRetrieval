# README

陈伟浩，2016013288



## 代码运行

### 命令行交互

代码在`src`文件夹下，其中：

- `main.py`是检索程序入口，提供了一个命令行交互界面，其运行方式为：

  ```sh
  python3 main.py
  ```

  加上参数`-h`可获得如下帮助：

  ```
  usage: main.py [-h] [-i INDEX] [-p POS] [-w WIN]
  
  A Collocation Retrieval System, made by Weihao CHEN
  
  optional arguments:
    -h, --help  show this help message and exit
    -i INDEX    path of lucene index directory (default: ../lucene-idx)
    -p POS      part of speech: v/n/a/... (default: )
    -w WIN      window size, at least 3 to be valid (default: 5)
  ```

  由于是交互命令界面，故在如下提示后直接输入检索字符串即可：

  ```
  Input query (type ? to get command list)>>>
  ```

  还可输入如下命令，根据提示动态设置查询：

  ```
  type <?> to get this help 输入英文问号?得到帮助信息
  type <p> for part of speech 输入p来设置返回词性，不输入则取消词性限制
  type <w> for window size 输入w来设置上下文窗口大小，最小为3，输入不合法则取消窗口限制
  type <n> for top n answers 输入n来设置结果显示数量
  type <q>, <quit> or <exit> to exit 输入q、quit或exit来退出程序
  ```

  可选的词性有（同THULAC词性标记方式）：

  ```
  n/名词 np/人名 ns/地名 ni/机构名 nz/其它专名
  m/数词 q/量词 mq/数量词 t/时间词 f/方位词 s/处所词
  v/动词 a/形容词 d/副词 h/前接成分 k/后接成分 i/习语 
  j/简称 r/代词 c/连词 p/介词 u/助词 y/语气助词
  e/叹词 o/拟声词 g/语素 w/标点 x/其它
  ```

- `gen_index.py`是从数据生成检索的程序，其运行方式为：

  ```sh
  python3 gen_index.py
  ```

  加上参数`-h`可获得如下帮助：

  ```
  usage: gen_index.py [-h] [-d DIR] [-p PREFIX] [-i INDEX] [-f FILE [FILE ...]]
  
  Generate index for the Collocation Retrieval System, made by Weihao CHEN
  
  optional arguments:
    -h, --help          show this help message and exit
    -d DIR              dir path of data to be indexed (default: ../data)
    -p PREFIX           prefix of file names (default: Sogou)
    -i INDEX            path of lucene index directory (default: ../lucene-idx)
    -f FILE [FILE ...]  a list of files (override DIR) (default: None)
  ```

### Web交互

代码在`src-flask`下。其中：

- `server.py`是主入口，需要在虚拟环境下运行，在根目录下开启虚拟环境：

  ```sh
  . venv/bin/activate
  ```

  运行网页服务器：

  ```
  cd src-flask
  python3 server.py
  ```

  或者先设置环境变量后用flask运行：

  ```
  cd src-flask
  export FLASK_APP=server.py
  flask run
  ```

- `backend.py`同`src/main.py`，是后端代码，调用了Lucene

- 其余html和css文件用于构建网页前端



## 数据存放

- `data`文件夹：

  - `stopwords.txt`里面存放的是停止词，检索的结果将不会包括这些词

  - `pos.txt`存放的是词性英文缩写和中文的对应，用于翻译词性，内容同下：

    ```
    n/名词 np/人名 ns/地名 ni/机构名 nz/其它专名
    m/数词 q/量词 mq/数量词 t/时间词 f/方位词 s/处所词
    v/动词 a/形容词 d/副词 h/前接成分 k/后接成分 i/习语 
    j/简称 r/代词 c/连词 p/介词 u/助词 y/语气助词
    e/叹词 o/拟声词 g/语素 w/标点 x/其它
    ```

  - 原始语料数据可放在`data`文件夹下进行处理，处理后可删除

- Lucene生成的索引数据在`lucene-idx`文件夹下



## 配置

为运行上述代码，需要安装PyLucene 7.7.1，其底层需要Java的支持。

### MacOS下安装PyLucene 7.7.1

参考：https://stackoverflow.com/questions/14376513/installing-pylucene-on-a-mac

PyLucene官方下载及教程：http://lucene.apache.org/pylucene/install.html

- 下载安装[Java Development Kit 8](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html)和[Java 1.6 from Apple](https://support.apple.com/kb/dl1572?locale=en_US)

- 配置环境变量JAVA_HOME

  - 参考：https://stackoverflow.com/questions/21964709/how-to-set-or-change-the-default-java-jdk-version-on-os-x

  - 查看所有的java版本：`/usr/libexec/java_home -V`

  - 选择JDK 1.8版本并设置环境变量：p3

    ```sh
    export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)
    ```

  - 如果系统装了更高版本的JDK，由于jcc的setup.py里面运行的是命令`/usr/libexec/java_home`，而该命令返回版本最高的JDK，故需要临时禁止高版本的JDK被返回，通过对其返回路径下的`Contents/Info.plist`进行重命名即可（参考stackoverflow第二高回答），示例：

    ```sh
    mv /Library/Java/JavaVirtualMachines/jdk-11.0.2.jdk/Contents/Info.plist /Library/Java/JavaVirtualMachines/jdk-11.0.2.jdk/Contents/Info.plist.disabled
    ```

- 解压下载包，在文件夹中进入jcc并安装jcc

  ```sh
  cd jcc
  python3 setup.py build
  ```

- 回到文件夹根目录，修改`Makefile`，设置如下变量以适应自己的平台：

  ```makefile
  PYTHON=python3
  ANT=ant
  JCC=$(PYTHON) -m jcc --shared --arch x86_64
  NUM_FILES=8
  ```

- 编译并安装

  ```sh
  make
  make test
  make install
  ```

- 安装完之后可以把屏蔽某版本的JDK的`Info.plist`改回原名，实际使用Lucene时只需要JVM虚拟机

