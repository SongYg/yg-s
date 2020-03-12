# Ubuntu(Linux) 下安装 Postgresql 并由 TPC-H 生成数据导入数据库
## 安装 Postgresql
- 下载 Postgresql（下称为 Postgres ），下载地址为：[Postgres](https://www.postgresql.org/ftp/source/)
- 解压缩，按照 Postgres 根目录的 INSTALL 文件安装
  ```bash
    ./configure
    make
    su
    make install
    adduser postgres
    mkdir /usr/local/pgsql/data
    chown postgres /usr/local/pgsql/data
    su - postgres
    /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data
    /usr/logfileocal/pgsql/bin/postgres -D /usr/local/pgsql/data >logfile 2>&1 &
    /usr/local/pgsql/bin/createdb test
    /usr/local/pgsql/bin/psql test
  ```
## TPC-H 生成数据
- 下载 TPC-H，下载地址为：[TCP-H](http://www.tpc.org/tpc_documents_current_versions/download_programs/tools-download-request.asp?bm_type=TPC-H&bm_vers=2.18.0&mode=CURRENT-ONLY)
- 解压缩 TPC-H，打开进入 dbgen 目录，执行以下命令生成 .tbl 数据。.tbl 数据是 TPC-H 生成的数据的格式，之后会转化为 CSV 文件导入Postgres，这一步我们先生成数据。
    ```bash
    /dbgen$ ./dbgen -s 1 -vf
    ```
    其中 1 是生成数据的大小，以 G 为单位，vf 是如果已存在数据那么进行覆盖。
- 将 .tbl 文件转化为 CSV 文件，准备导入 Postgres
    ```bash
    /dbgen$ for i in `ls *.tbl`; do sed 's/|$//' $i > ${i/tbl/csv}; echo $i; done;
    ```
## 将数据导入Postgres
- 首先将 Postgres 的按照的 bin 目录加入环境变量，Postgres 的默认路径是： /usr/local/pgsql/bin。将以下命令加入 ~/.bashrc 文件：
    ```bash
    export PATH=$PATH:/usr/local/pgsql/bin
    ```
    然后 source .bashrc 文件：
    ```bash
    ~$ source .bashrc
    ```
- 命令行执行 psql，打开 psql local idle：
    ```bash
    psql
    ```
- 在 psql 中新建 tables 对应 TPC-H 生成的数据的 tables：
    ```sql
    postgres=#
    CREATE TABLE NATION  ( N_NATIONKEY  INTEGER NOT NULL,
                                N_NAME       CHAR(25) NOT NULL,
                                N_REGIONKEY  INTEGER NOT NULL,
                                N_COMMENT    VARCHAR(152));

    CREATE TABLE REGION  ( R_REGIONKEY  INTEGER NOT NULL,
                                R_NAME       CHAR(25) NOT NULL,
                                R_COMMENT    VARCHAR(152));

    CREATE TABLE PART  ( P_PARTKEY     INTEGER NOT NULL,
                              P_NAME        VARCHAR(55) NOT NULL,
                              P_MFGR        CHAR(25) NOT NULL,
                              P_BRAND       CHAR(10) NOT NULL,
                              P_TYPE        VARCHAR(25) NOT NULL,
                              P_SIZE        INTEGER NOT NULL,
                              P_CONTAINER   CHAR(10) NOT NULL,
                              P_RETAILPRICE DECIMAL(15,2) NOT NULL,
                              P_COMMENT     VARCHAR(23) NOT NULL );

    CREATE TABLE SUPPLIER ( S_SUPPKEY     INTEGER NOT NULL,
                                 S_NAME        CHAR(25) NOT NULL,
                                 S_ADDRESS     VARCHAR(40) NOT NULL,
                                 S_NATIONKEY   INTEGER NOT NULL,
                                 S_PHONE       CHAR(15) NOT NULL,
                                 S_ACCTBAL     DECIMAL(15,2) NOT NULL,
                                 S_COMMENT     VARCHAR(101) NOT NULL);

    CREATE TABLE PARTSUPP ( PS_PARTKEY     INTEGER NOT NULL,
                                 PS_SUPPKEY     INTEGER NOT NULL,
                                 PS_AVAILQTY    INTEGER NOT NULL,
                                 PS_SUPPLYCOST  DECIMAL(15,2)  NOT NULL,
                                 PS_COMMENT     VARCHAR(199) NOT NULL );

    CREATE TABLE CUSTOMER ( C_CUSTKEY     INTEGER NOT NULL,
                                 C_NAME        VARCHAR(25) NOT NULL,
                                 C_ADDRESS     VARCHAR(40) NOT NULL,
                                 C_NATIONKEY   INTEGER NOT NULL,
                                 C_PHONE       CHAR(15) NOT NULL,
                                 C_ACCTBAL     DECIMAL(15,2)   NOT NULL,
                                 C_MKTSEGMENT  CHAR(10) NOT NULL,
                                 C_COMMENT     VARCHAR(117) NOT NULL);

    CREATE TABLE ORDERS  ( O_ORDERKEY       INTEGER NOT NULL,
                               O_CUSTKEY        INTEGER NOT NULL,
                               O_ORDERSTATUS    CHAR(1) NOT NULL,
                               O_TOTALPRICE     DECIMAL(15,2) NOT NULL,
                               O_ORDERDATE      DATE NOT NULL,
                               O_ORDERPRIORITY  CHAR(15) NOT NULL,  
                               O_CLERK          CHAR(15) NOT NULL, 
                               O_SHIPPRIORITY   INTEGER NOT NULL,
                               O_COMMENT        VARCHAR(79) NOT NULL);

    CREATE TABLE LINEITEM ( L_ORDERKEY    INTEGER NOT NULL,
                                 L_PARTKEY     INTEGER NOT NULL,
                                 L_SUPPKEY     INTEGER NOT NULL,
                                 L_LINENUMBER  INTEGER NOT NULL,
                                 L_QUANTITY    DECIMAL(15,2) NOT NULL,
                                 L_EXTENDEDPRICE  DECIMAL(15,2) NOT NULL,
                                 L_DISCOUNT    DECIMAL(15,2) NOT NULL,
                                 L_TAX         DECIMAL(15,2) NOT NULL,
                                 L_RETURNFLAG  CHAR(1) NOT NULL,
                                 L_LINESTATUS  CHAR(1) NOT NULL,
                                 L_SHIPDATE    DATE NOT NULL,
                                 L_COMMITDATE  DATE NOT NULL,
                                 L_RECEIPTDATE DATE NOT NULL,
                                 L_SHIPINSTRUCT CHAR(25) NOT NULL,
                                 L_SHIPMODE     CHAR(10) NOT NULL,
                                 L_COMMENT      VARCHAR(44) NOT NULL);
    ```
- 将 TPC-H 生成的 CSV 数据导入 psql，在 psql 中执行以下命令，/xdb/tpch/dbgen/dss/data/ 对应为生成的 CSV 所在的目录：
    ```sql
    postgres=#
    COPY customer(C_CUSTKEY,C_NAME,C_ADDRESS,C_NATIONKEY,C_PHONE,C_ACCTBAL,C_MKTSEGMENT,C_COMMENT) FROM '/xdb/tpch/dbgen/dss/data/customer.csv' delimiter '|' ;
    COPY lineitem(L_ORDERKEY,L_PARTKEY,L_SUPPKEY,L_LINENUMBER,L_QUANTITY,L_EXTENDEDPRICE,L_DISCOUNT,L_TAX,L_RETURNFLAG,L_LINESTATUS,L_SHIPDATE,L_COMMITDATE,L_RECEIPTDATE,L_SHIPINSTRUCT,L_SHIPMODE,L_COMMENT) FROM '/xdb/tpch/dbgen/dss/data/lineitem.csv' delimiter '|' ;
    COPY nation(N_NATIONKEY,N_NAME,N_REGIONKEY,N_COMMENT) FROM   '/xdb/tpch/dbgen/dss/data/nation.csv' delimiter '|' ;
    COPY orders(O_ORDERKEY,O_CUSTKEY,O_ORDERSTATUS,O_TOTALPRICE,O_ORDERDATE,O_ORDERPRIORITY,O_CLERK,O_SHIPPRIORITY,O_COMMENT) FROM   '/xdb/tpch/dbgen/dss/data/orders.csv' delimiter '|' ;
    COPY partsupp(PS_PARTKEY,PS_SUPPKEY,PS_AVAILQTY,PS_SUPPLYCOST,PS_COMMENT) FROM '/xdb/tpch/dbgen/dss/data/partsupp.csv' delimiter '|' ;
    COPY part(P_PARTKEY,P_NAME,P_MFGR,P_BRAND,P_TYPE,P_SIZE,P_CONTAINER,P_RETAILPRICE,P_COMMENT) FROM     '/xdb/tpch/dbgen/dss/data/part.csv' delimiter '|' ;
    COPY region(R_REGIONKEY,R_NAME,R_COMMENT) FROM   '/xdb/tpch/dbgen/dss/data/region.csv' delimiter '|' ;
    COPY supplier(S_SUPPKEY,S_NAME,S_ADDRESS,S_NATIONKEY,S_PHONE,S_ACCTBAL,S_COMMENT) FROM '/xdb/tpch/dbgen/dss/data/supplier.csv' delimiter '|' ;
    ```
- 修改 psql 建立的表的内外键：
    ```sql
    postgres=# 
    --PRIMARY KEY
    ALTER TABLE PART ADD PRIMARY KEY (P_PARTKEY);
    ALTER TABLE SUPPLIER ADD PRIMARY KEY (S_SUPPKEY);
    ALTER TABLE PARTSUPP ADD PRIMARY KEY (PS_PARTKEY, PS_SUPPKEY);
    ALTER TABLE CUSTOMER ADD PRIMARY KEY (C_CUSTKEY);
    ALTER TABLE ORDERS ADD PRIMARY KEY (O_ORDERKEY);
    ALTER TABLE LINEITEM ADD PRIMARY KEY (L_ORDERKEY, L_LINENUMBER);
    ALTER TABLE NATION ADD PRIMARY KEY (N_NATIONKEY);
    ALTER TABLE REGION ADD PRIMARY KEY (R_REGIONKEY);

    -- FOREIGN KEY
    ALTER TABLE SUPPLIER ADD FOREIGN KEY (S_NATIONKEY) REFERENCES NATION(N_NATIONKEY);
    ALTER TABLE PARTSUPP ADD FOREIGN KEY (PS_PARTKEY) REFERENCES PART(P_PARTKEY);
    ALTER TABLE PARTSUPP ADD FOREIGN KEY (PS_SUPPKEY) REFERENCES SUPPLIER(S_SUPPKEY);
    ALTER TABLE CUSTOMER ADD FOREIGN KEY (C_NATIONKEY) REFERENCES NATION(N_NATIONKEY);
    ALTER TABLE ORDERS ADD FOREIGN KEY (O_CUSTKEY) REFERENCES CUSTOMER(C_CUSTKEY);
    ALTER TABLE LINEITEM ADD FOREIGN KEY (L_ORDERKEY) REFERENCES ORDERS(O_ORDERKEY);
    ALTER TABLE LINEITEM ADD FOREIGN KEY (L_PARTKEY,L_SUPPKEY) REFERENCES PARTSUPP(PS_PARTKEY,PS_SUPPKEY);
    ALTER TABLE NATION ADD FOREIGN KEY (N_REGIONKEY) REFERENCES REGION(R_REGIONKEY);
    ```
    至此数据已经导入 psql 当中。
- 可以在 psql 中执行 \d 命令查看当前所建立的表格：
    ```bash
    postgres=# \d+
    ```
    表格结果为：
    ```
    postgres=# \d+
                        List of relations  
     Schema |   Name   | Type  |  Owner   |    Size    | Description  
    --------+----------+-------+----------+------------+-------------  
     public | customer | table | postgres | 28 MB      |  
     public | lineitem | table | postgres | 879 MB     |  
     public | nation   | table | postgres | 8192 bytes |  
     public | orders   | table | postgres | 204 MB     |  
     public | part     | table | postgres | 32 MB      |  
     public | partsupp | table | postgres | 136 MB     |  
     public | region   | table | postgres | 8192 bytes |  
     public | supplier | table | postgres | 1800 kB    |  
    (8 rows)
    ```
