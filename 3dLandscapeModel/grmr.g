start: (NEWLINE|stmt)+ ;

// Statements

@stmt : simple_stmt | compound_stmt ;

@simple_stmt : small_stmt (NEWLINE|EOF);

@small_stmt : assign_stmt
  | log_stmt
  | trigger_stmt
  | expr_stmt
  | return_stmt
  ;

@compound_stmt : when_stmt
  | if_stmt
  | while_stmt
  | funcdef_stmt
  | elseif_stmt
  | else_stmt
  ;

assign_stmt : name EQUAL expr_stmt ;
log_stmt : LOG expr_stmt ;
trigger_stmt : TRIGGER literal ON expr_stmt (WITH arglist)? ;
return_stmt : RETURN expr_stmt ;

expr_stmt : or_test ;

when_stmt : WHEN literal (HAS arglist)? DO suite ;
if_stmt : IF expr_stmt DO suite ;
elseif_stmt : ELSEIF expr_stmt DO suite ;
else_stmt : ELSE suite ;
while_stmt : WHILE expr_stmt DO suite ;
funcdef_stmt : FUNC name LPAR argnames RPAR suite ;

suite : NEWLINE (stmt|NEWLINE)* END ;

arglist : (expr_stmt COMMA)+? (expr_stmt COMMA?) ;
argnames : (name COMMA)+? (name COMMA?) ;

@molecule : atom
  | funccall
  ;

@atom : name
  | string
  | number
  | LPAR or_test RPAR
  | constant
  ;

@literal : name
  | constant
  | string
  | number
  ;

?or_test : and_test (OR and_test)* ;
?and_test : not_test (AND not_test)* ;
@not_test : not_expr | comparison ;
not_expr : NOT not_test ;
?comparison : expr (compare_symbol expr)* ;
?expr : term (add_symbol term)* ;

?term : factor (term_symbol factor)* ;

?factor : add_symbol factor
  | power
  | molecule
  ;
name : NAME ;
?power : molecule (POWER factor)? ;

funccall : molecule LPAR arglist? RPAR ;

compare_symbol : LESS
    | GREATER
    | EQEQUAL
    | GREATEREQUAL
    | LESSEQUAL
    | NOTEQUAL
    ;

term_symbol : STAR|SLASH|PERCENT ;
add_symbol : PLUS|MINUS ;

number: DEC_NUMBER | HEX_NUMBER | FLOAT_NUMBER ;
constant: TRUE | FALSE ;
string: STRING ;

%fragment I: '(?i)';    // Case Insensitive
%fragment QUOTE: '\'';
%fragment DBLQUOTE: '"';

DEC_NUMBER : '[0-9]\d*' ;
HEX_NUMBER : '0x[\da-f]' ;
FLOAT_NUMBER : '[0-9]\d*\.[1-9]\d*' ;

%fragment STRING_PREFIX: '(u|b|)r?';
%fragment STRING_INTERNAL: '.*?(?<!\\)(\\\\)*?' ;

STRING : STRING_PREFIX
            '(' DBLQUOTE '(?!"")' STRING_INTERNAL DBLQUOTE
            '|' QUOTE '(?!\'\')' STRING_INTERNAL QUOTE
            ')' ;

NEWLINE: '(\r?\n[\t ]*)+'    // Don't count on the + to prevent multiple NEWLINE tokens. It's just an optimization
    (%newline)
    ;
COMMENT: '\#(.*)(\r?\n[\t ]*)'(%ignore);

PLUS: '\+';
MINUS: '-';
STAR: '\*';
SLASH: '/';
POWER: '\^';

EQEQUAL: '==';
NOTEQUAL: '!=';
LESSEQUAL: '<=';
GREATEREQUAL: '>=';

COMMA: ',';
LPAR: '\(';
RPAR: '\)';
PERCENT: '%';
LESS: '<';
GREATER: '>';
EQUAL: '=';

WS: '[\t \f]+' (%ignore);
NAME: I '[a-z_.][a-z_.0-9]*'
    (%unless
        LOG: I 'Log';
        WHEN: I 'When';
        DO: I 'Do';
        WITH: I 'With';
        TRIGGER: I 'Trigger';
        ELSEIF: I 'ElseIf';
        ELSE: I 'Else';
        HAS: I 'Has';
        IF: I 'If';
        WHILE: I 'While';
        AND: I 'and';
        OR: I 'or';
        NOT: I 'not';
        END: I 'end';
        ON: I 'On';
        FUNC: I 'Function';
        RETURN: I 'Return';
        TRUE: I 'True';
        FALSE: I 'False';
    )
    ;

EOF: '<EOF>';