# Postgres 词法分析和语法分析
## 整体介绍
Postgres main 函数都通过调用 exec_simple_query() 函数执行 SQL 语句，exec_simple_query() 通过一系列初始化后会首先对 SQL 语句进行词法分析和语法分析。词法分析和语法分析主要是调用函数 pg_parse_query() 完成的，pg_parse_query() 会调用 raw_parser() 获取词法分析和语法分析的 parsertree，过程如下（图中的1、2、3、4）：
![Postgres 主要过程调用图](https://github.com/SongYg/yg-s/blob/master/blog/fig/exec_simple_query.png?raw=true)
语法解析与词法解析的函数调用图如下：
![Postgres 词法语法分析](https://github.com/SongYg/yg-s/blob/master/blog/fig/raw_parser.png?raw=true)

## List 结构
raw_parser() 函数返回的 yyextra.parsetree 是 List 类型，实际上用来 Flex/Bison 工具完成的词法和语法分析，具体实现过程在 scan.l 和 gram.y 文件内。结合 gram.y 可以看到返回的 List* parser_tree 是什么样的，选取 gram.y 中的 simple_select 的代码：
```yacc
/*
 * This rule parses SELECT statements that can appear within set operations,
 * including UNION, INTERSECT and EXCEPT.  '(' and ')' can be used to specify
 * the ordering of the set operations.	Without '(' and ')' we want the
 * operations to be ordered per the precedence specs at the head of this file.
 *
 * As with select_no_parens, simple_select cannot have outer parentheses,
 * but can have parenthesized subclauses.
 *
 * Note that sort clauses cannot be included at this level --- SQL requires
 *		SELECT foo UNION SELECT bar ORDER BY baz
 * to be parsed as
 *		(SELECT foo UNION SELECT bar) ORDER BY baz
 * not
 *		SELECT foo UNION (SELECT bar ORDER BY baz)
 * Likewise for WITH, FOR UPDATE and LIMIT.  Therefore, those clauses are
 * described as part of the select_no_parens production, not simple_select.
 * This does not limit functionality, because you can reintroduce these
 * clauses inside parentheses.
 *
 * NOTE: only the leftmost component SelectStmt should have INTO.
 * However, this is not checked by the grammar; parse analysis must check it.
 */
simple_select:
			SELECT opt_adaptive opt_online opt_distinct opt_target_list
			into_clause from_clause where_clause
			group_clause having_clause window_clause
			withtime_clause confidence_clause
			reportinterval_clause initsample_clause
				{
					SelectStmt *n = makeNode(SelectStmt);
					n->adaptive = $2;
					n->hasOnline = ($2 || $3);
					n->distinctClause = $4;
					n->targetList = $5;
					n->intoClause = $6;
					n->fromClause = $7;
					n->whereClause = $8;
					n->groupClause = $9;
					n->havingClause = $10;
					n->windowClause = $11;
					n->withTime = $12;
					n->confidence = $13;
					n->reportInterval = $14;
					n->nInitSamples = $15;
					$$ = (Node *)n;
				}
			| ...
		;
```
从代码中可以看出，SELECT 语句经过语法分析后，返回的是一个 SelectStmt 的结构体，它被存在了 List 结构中的 Listcell 中，Listcell 采用保存 void* 指针。解析 SELECT 语句的时候实际上是返回的是 SelectStmt* 结构，但是在 parser_tree 中被当做 void* 保存。非常好的地方也就是使用了 void* 保存，这样使得 parser_tree 更灵活，而在最后使用的时候会用 ISA() 函数判断 void* 指针具体是什么结构。
```c
typedef struct List
{
	NodeTag		type;			/* T_List, T_IntList, or T_OidList */
	int			length;
	ListCell   *head;
	ListCell   *tail;
} List;

struct ListCell
{
	union
	{
		void	   *ptr_value;
		int			int_value;
		Oid			oid_value;
	}			data;
	ListCell   *next;
};
```
可以从 parse_analyze() 阶段找到返回的 List* parsertree 是怎么用的。在 parse_analyze 阶段 transformTopLevelStmt() 函数内会调用 ISA 函数，根据 parsertree 中具体的结构分析：
```c
Query *
transformTopLevelStmt(ParseState *pstate, Node *parseTree)
{
	if (IsA(parseTree, SelectStmt))
	{
		SelectStmt *stmt = (SelectStmt *) parseTree;

		/* If it's a set-operation tree, drill down to leftmost SelectStmt */
		while (stmt && stmt->op != SETOP_NONE)
			stmt = stmt->larg;
		Assert(stmt && IsA(stmt, SelectStmt) &&stmt->larg == NULL);

		if (stmt->intoClause)
		{
			CreateTableAsStmt *ctas = makeNode(CreateTableAsStmt);

			ctas->query = parseTree;
			ctas->into = stmt->intoClause;
			ctas->relkind = OBJECT_TABLE;
			ctas->is_select_into = true;

			/*
			 * Remove the intoClause from the SelectStmt.  This makes it safe
			 * for transformSelectStmt to complain if it finds intoClause set
			 * (implying that the INTO appeared in a disallowed place).
			 */
			stmt->intoClause = NULL;

			parseTree = (Node *) ctas;
		}
	}

	return transformStmt(pstate, parseTree);
}
```

## 具体实例
在 psql 中执行简单 SELECT 语句，使用 GDB 调试，查看 raw_parser() 函数返回值。
```bash
(gdb) print *(SelectStmt *)parsetree_list.head.data.ptr_value
$5 = {type = T_SelectStmt, distinctClause = 0x0, intoClause = 0x0, 
  targetList = 0xee8b10, fromClause = 0xee8bc8, whereClause = 0x0, 
  groupClause = 0x0, havingClause = 0x0, windowClause = 0x0, 
  valuesLists = 0x0, sortClause = 0x0, limitOffset = 0x0, 
  limitCount = 0x0, lockingClause = 0x0, withClause = 0x0, 
  op = SETOP_NONE, all = 0 '\000', larg = 0x0, rarg = 0x0}
```
结合 SelectStmt 结构体：
```c
typedef struct SelectStmt
{
	NodeTag		type;

	/*
	 * These fields are used only in "leaf" SelectStmts.
	 */
	List	   * ; /* NULL, list of DISTINCT ON exprs, or
								 * lcons(NIL,NIL) for all (SELECT DISTINCT) */
	IntoClause *intoClause;		/* target for SELECT INTO */
	List	   *targetList;		/* the target list (of ResTarget) */
	List	   *fromClause;		/* the FROM clause */
	Node	   *whereClause;	/* WHERE qualification */
	List	   *groupClause;	/* GROUP BY clauses */
	Node	   *havingClause;	/* HAVING conditional-expression */
	List	   *windowClause;	/* WINDOW window_name AS (...), ... */

	/*
	 * In a "leaf" node representing a VALUES list, the above fields are all
	 * null, and instead this field is set.  Note that the elements of the
	 * sublists are just expressions, without ResTarget decoration. Also note
	 * that a list element can be DEFAULT (represented as a SetToDefault
	 * node), regardless of the context of the VALUES list. It's up to parse
	 * analysis to reject that where not valid.
	 */
	List	   *valuesLists;	/* untransformed list of expression lists */

	/*
	 * These fields are used in both "leaf" SelectStmts and upper-level
	 * SelectStmts.
	 */
	List	   *sortClause;		/* sort clause (a list of SortBy's) */
	Node	   *limitOffset;	/* # of result tuples to skip */
	Node	   *limitCount;		/* # of result tuples to return */
	List	   *lockingClause;	/* FOR UPDATE (list of LockingClause's) */
	WithClause *withClause;		/* WITH clause */

	/*
	 * These fields are used only in upper-level SelectStmts.
	 */
	SetOperation op;			/* type of set op */
	bool		all;			/* ALL specified? */
	struct SelectStmt *larg;	/* left child */
	struct SelectStmt *rarg;	/* right child */
	/* Eventually add fields for CORRESPONDING spec here */
} SelectStmt;
```
其中比较重要的是 targetList 字段，GDB 返回的 targetList 结果如下：
```bash
(gdb) print *((SelectStmt *)parsetree_list.head.data.ptr_value).targetList
$10 = {type = T_List, length = 1, head = 0xee8af0, tail = 0xee8af0}
```
然后返回 gram.y，可以发现在 simple_select 语句中有 targetList 这一项，对应的是：
```yacc
opt_target_list: target_list						{ $$ = $1; }
			| /* EMPTY */							{ $$ = NIL; }
		;

target_list:
			target_el								{ $$ = list_make1($1); }
			| target_list ',' target_el				{ $$ = lappend($1, $3); }
		;

target_el:	a_expr AS ColLabel
				{
					$$ = makeNode(ResTarget);
					$$->name = $3;
					$$->indirection = NIL;
					$$->val = (Node *)$1;
					$$->location = @1;
				}
			/*
			 * We support omitting AS only for column labels that aren't
			 * any known keyword.  There is an ambiguity against postfix
			 * operators: is "a ! b" an infix expression, or a postfix
			 * expression and a column label?  We prefer to resolve this
			 * as an infix expression, which we accomplish by assigning
			 * IDENT a precedence higher than POSTFIXOP.
			 */
			| a_expr IDENT
				{
					$$ = makeNode(ResTarget);
					$$->name = $2;
					$$->indirection = NIL;
					$$->val = (Node *)$1;
					$$->location = @1;
				}
			| a_expr
				{
					$$ = makeNode(ResTarget);
					$$->name = NULL;
					$$->indirection = NIL;
					$$->val = (Node *)$1;
					$$->location = @1;
				}
			| '*'
				{
					ColumnRef *n = makeNode(ColumnRef);
					n->fields = list_make1(makeNode(A_Star));
					n->location = @1;

					$$ = makeNode(ResTarget);
					$$->name = NULL;
					$$->indirection = NIL;
					$$->val = (Node *)n;
					$$->location = @1;
				}
		;
```
应是 select clause 后跟的 * 或 a_expr 等。在我们的语句中他的长度是 1，在 GDB 中 targetList 信息如下：
```bash
(gdb) print *(TargetEntry *)(((SelectStmt *)(*parsetree_list.head).data.ptr_value).targetList)
$9 = {xpr = {type = T_List}, expr = 0x1f19aa0, resno = -25952, resname = 0x0, ressortgroupref = 32192320, resorigtbl = 0, resorigcol = 8, 
  resjunk = 0 '\000'}
```
TargetEntry 结构体是：
```c

/*--------------------
 * TargetEntry -
 *	   a target entry (used in query target lists)
 *
 * Strictly speaking, a TargetEntry isn't an expression node (since it can't
 * be evaluated by ExecEvalExpr).  But we treat it as one anyway, since in
 * very many places it's convenient to process a whole query targetlist as a
 * single expression tree.
 *
 * In a SELECT's targetlist, resno should always be equal to the item's
 * ordinal position (counting from 1).  However, in an INSERT or UPDATE
 * targetlist, resno represents the attribute number of the destination
 * column for the item; so there may be missing or out-of-order resnos.
 * It is even legal to have duplicated resnos; consider
 *		UPDATE table SET arraycol[1] = ..., arraycol[2] = ..., ...
 * The two meanings come together in the executor, because the planner
 * transforms INSERT/UPDATE tlists into a normalized form with exactly
 * one entry for each column of the destination table.  Before that's
 * happened, however, it is risky to assume that resno == position.
 * Generally get_tle_by_resno() should be used rather than list_nth()
 * to fetch tlist entries by resno, and only in SELECT should you assume
 * that resno is a unique identifier.
 *
 * resname is required to represent the correct column name in non-resjunk
 * entries of top-level SELECT targetlists, since it will be used as the
 * column title sent to the frontend.  In most other contexts it is only
 * a debugging aid, and may be wrong or even NULL.  (In particular, it may
 * be wrong in a tlist from a stored rule, if the referenced column has been
 * renamed by ALTER TABLE since the rule was made.  Also, the planner tends
 * to store NULL rather than look up a valid name for tlist entries in
 * non-toplevel plan nodes.)  In resjunk entries, resname should be either
 * a specific system-generated name (such as "ctid") or NULL; anything else
 * risks confusing ExecGetJunkAttribute!
 *
 * ressortgroupref is used in the representation of ORDER BY, GROUP BY, and
 * DISTINCT items.  Targetlist entries with ressortgroupref=0 are not
 * sort/group items.  If ressortgroupref>0, then this item is an ORDER BY,
 * GROUP BY, and/or DISTINCT target value.  No two entries in a targetlist
 * may have the same nonzero ressortgroupref --- but there is no particular
 * meaning to the nonzero values, except as tags.  (For example, one must
 * not assume that lower ressortgroupref means a more significant sort key.)
 * The order of the associated SortGroupClause lists determine the semantics.
 *
 * resorigtbl/resorigcol identify the source of the column, if it is a
 * simple reference to a column of a base table (or view).  If it is not
 * a simple reference, these fields are zeroes.
 *
 * If resjunk is true then the column is a working column (such as a sort key)
 * that should be removed from the final output of the query.  Resjunk columns
 * must have resnos that cannot duplicate any regular column's resno.  Also
 * note that there are places that assume resjunk columns come after non-junk
 * columns.
 *--------------------
 */
typedef struct TargetEntry
{
	Expr		xpr;
	Expr	   *expr;			/* expression to evaluate */
	AttrNumber	resno;			/* attribute number (see notes above) */
	char	   *resname;		/* name of the column (could be NULL) */
	Index		ressortgroupref;/* nonzero if referenced by a sort/group
								 * clause */
	Oid			resorigtbl;		/* OID of column's source table */
	AttrNumber	resorigcol;		/* column's number in source table */
	bool		resjunk;		/* set to true to eliminate the attribute from
								 * final target list */
} TargetEntry;
```