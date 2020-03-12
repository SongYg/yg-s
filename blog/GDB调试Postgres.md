# 使用 GDB 调试 Postgres
## 修改 Postgres 的配置，满足 GDB 调试
- 修改 Makefile.global:
    ```bash
    vim postgresql-9.4.2/src/Makefile.global 
    
    CFLAGS = -Wall -Wmissing-prototypes -Wpointer-arith Wdeclaration-after-statement -Wendif-labels Wmissing-format-attribute -Wformat-security fno-strict-aliasing -fwrapv -g -O2 
    ```
    上面的行的 "-O2" 选项删除，只保留 -g

- 运行 configure
    ```bash
    postgresql-9.4.2$ ./configure --enable-debug -prefix=/home/username/run/
    ```
    其中 -prefix 为可选项，含义为安装 Postgres的路径，路径可以自定义
- 编译、安装
    ```bash
    postgresql-9.4.2$ make
    postgresql-9.4.2$ make install
- 将 install 的 bin 路径加入 postgres 用户的环境变量（已经创建好了 postgres 用户了）
    ```bash
    ~$ su postgres 
    ~$ vim ~/.bash_profile
    ```
    将以下内容添加进 .bash_profile
    ```bash
    export PATH=$PATH:/home/username/run/bin/
    export PGDATA=/usr/local/pgsql/data/
    ```
    退出 vim， 然后：**`source ~/.bash_profile`**  
    修改 .bash_profile中的 PATH 是添加环境变量，路径为刚刚设置的 prefix/bin。  
    PGDATA 是启动 psql 的数据存储的地方，即 postgresql-9.4.2/INSTALL 文件里 initdb 命令时 -D 的参数值，默认为 PGDATA=/usr/local/pgsql/data/，添加这个之后就可以直接使用 `pg_ctl start` 启动，不需要加 -D 的参数了。
- 关闭和重启 Postgres 服务，已经加了环境变量了，因此可以直接执行以下命令：
    ```bash
    ~$ pg_ctl stop
    ~$ pg_ctl start
    ```
- 生成数据可以参考 [TPC-H 生成数据和插入到 psql 中](https://github.com/SongYg/yg-s/blob/master/TPCH%E6%B5%8B%E8%AF%95Postgres.md)。
## 使用 GDB 调试
- 先在 postgres 用户下打开 psql。
  ```bash
  postgres@ubuntu:~$ psql
  ```
    会进入 psql 的一个窗口：
    ```
    postgres@iZuf6866edq67pc3r0m9wzZ:~$ psql
    psql (9.4.2)
    Type "help" for help.

    postgres=# 
    ```
- 然后在一个有 sudo 权限的用户下，搜索刚刚打开的 psql 的进程号：`ps -ef | grep postgres`，将会得到类似的如下一行的进程信息：
    ```
    ~$ ps -ef | grep postgres
    ...
    postgres 11802  5619  0 23:27 ? 00:00:00 postgres: postgres postgres [local] idle
    ...
    ```
    记住这个 PID : 11802
- 在有 sudo 的用户下执行命令： `sudo gdb postgres 11802`，进入 GDB 调试视图。然后可以添加断点，执行 gdb 调试，比如添加断点：
    ```
    (gdb) b raw_parser
    Breakpoint 1 at 0x56ab8c: file parser.c, line 36.
    ```
    在打上断点之后，在 postgres 用户的 psql 窗口输入简单的查询语句并回车，比如：`postgres=# select oid from pg_class where relname='nation';`  
    再在 GDB 的窗口进行调试：
    ```
    (gdb) c
    Continuing.

    Breakpoint 1, raw_parser (str=0x19ebe50 "select oid from pg_class where relname='nation';") at parser.c:36
    36	{
    (gdb) bt
    #0  raw_parser (str=0x19ebe50 "select oid from pg_class where relname='nation';") at parser.c:36
    #1  0x000000000076f0b9 in pg_parse_query (query_string=0x19ebe50 "select oid from pg_class where relname='nation';") at postgres.c:590
    #2  0x000000000076f4a5 in exec_simple_query (query_string=0x19ebe50 "select oid from pg_class where relname='nation';") at postgres.c:906
    #3  0x0000000000773c06 in PostgresMain (argc=1, argv=0x1984350, dbname=0x1984200 "postgres", username=0x19841e0 "postgres") at postgres.c:4074
    #4  0x00000000007028ba in BackendRun (port=0x19a3d30) at postmaster.c:4164
    #5  0x0000000000701fa1 in BackendStartup (port=0x19a3d30) at postmaster.c:3829
    #6  0x00000000006fe911 in ServerLoop () at postmaster.c:1597
    #7  0x00000000006fdf4b in PostmasterMain (argc=1, argv=0x1983490) at postmaster.c:1244
    #8  0x00000000006637d0 in main (argc=1, argv=0x1983490) at main.c:228
    ```
    b 打上断点，具体 GDB 的操作就不详细说明了，c 是 continue，bt 是 backtrace 查看调用栈，可以看到调用的函数信息。