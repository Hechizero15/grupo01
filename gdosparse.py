# Implementacion de Gdos basado en el lenguaje Dartmouth BASIC (1964)

from ply import *
import gdoslex

tokens = gdoslex.tokens

precedence = (
               ('left', 'MAS','MENOS'),
               ('left', 'POR','DIVIDE'),
               ('left', 'ELEVADO'),
               ('right','UMINUS')
)

def p_program(p):
    '''program : program statement
               | statement'''

    if len(p) == 2 and p[1]:
       p[0] = { }
       line,stat = p[1]
       p[0][line] = stat
    elif len(p) ==3:
       p[0] = p[1]
       if not p[0]: p[0] = { }
       if p[2]:
           line,stat = p[2]
           p[0][line] = stat

def p_program_error(p):
    '''program : error'''
    p[0] = None
    p.parser.error = 1

def p_statement(p):
    '''statement : ENTERO command NLINEA'''
    if isinstance(p[2],str):
        print("%s %s %s" % (p[2],"en la linea", p[1]))
        p[0] = None
        p.parser.error = 1
    else:
        lineno = int(p[1])
        p[0] = (lineno,p[2])

def p_statement_interactive(p):
    '''statement : CORRER NLINEA
                 | LISTA NLINEA
                 | NUEVO NLINEA'''
    p[0] = (0, (p[1],0))

def p_statement_blank(p):
    '''statement : ENTERO NLINEA'''
    p[0] = (0,('BLANK',int(p[1])))

def p_statement_bad(p):
    '''statement : ENTERO error NLINEA'''
    print("Comando formado erroneamente en la linea >> %s" % p[1])
    p[0] = None
    p.parser.error = 1

def p_statement_newline(p):
    '''statement : NLINEA'''
    p[0] = None

def p_command_let(p):
    '''command : LET variable IGUAL expr'''
    p[0] = ('LET',p[2],p[4])

def p_command_let_bad(p):
    '''command : LET variable IGUAL error'''
    p[0] = "expresion mala en LET"

def p_command_read(p):
    '''command : LEER varlist'''
    p[0] = ('LEER',p[2])

def p_command_read_bad(p):
    '''command : LEER error'''
    p[0] = "Lista de variables formadas erroneamente en el LEER"

def p_command_data(p):
    '''command : DATO numlist'''
    p[0] = ('DATO',p[2])

def p_command_data_bad(p):
    '''command : DATO error'''
    p[0] = "Lista de numeros formadas erroneamente en el DATO"

def p_command_print(p):
    '''command : IMPRIMIR plist optend'''
    p[0] = ('IMPRIMIR',p[2],p[3])

def p_command_print_bad(p):
    '''command : IMPRIMIR error'''
    p[0] = "Comando IMPRIMIR formado erroneamente"

def p_optend(p):
    '''optend : COMA 
              | PCOMA
              |'''
    if len(p)  == 2:
         p[0] = p[1]
    else:
         p[0] = None

def p_command_print_empty(p):
    '''command : IMPRIMIR'''
    p[0] = ('IMPRIMIR',[],None)

def p_command_goto(p):
    '''command : CONTINUAR ENTERO'''
    p[0] = ('CONTINUAR',int(p[2]))

def p_command_goto_bad(p):
    '''command : CONTINUAR error'''
    p[0] = "Numero de linea invalIDo en CONTINUAR"

def p_command_if(p):
    '''command : SI relexpr ENTONCES ENTERO'''
    p[0] = ('SI',p[2],int(p[4]))

def p_command_if_bad(p):
    '''command : SI error ENTONCES ENTERO'''
    p[0] = "expresion relacinal mala"

def p_command_if_bad2(p):
    '''command : SI relexpr ENTONCES error'''
    p[0] = "Numero de linea invalido en el ENTONCES"

def p_command_for(p):
    '''command : PARA ID IGUAL expr A expr optstep'''
    p[0] = ('PARA',p[2],p[4],p[6],p[7])

def p_command_for_bad_initial(p):
    '''command : PARA ID IGUAL error A expr optstep'''
    p[0] = "valor inicial malo para comando 'PARA'"

def p_command_for_bad_FINal(p):
    '''command : PARA ID IGUAL expr A error optstep'''
    p[0] = "valor final malo para comando 'PARA'"

def p_command_for_bad_step(p):
    '''command : PARA ID IGUAL expr A expr ETAPA error'''
    p[0] = "ETAPA formada erroneamente en comando 'PARA'"

def p_optstep(p):
    '''optstep : ETAPA expr
               | empty'''
    if len(p) == 3:
       p[0] = p[2]
    else:
       p[0] = None
    
def p_command_next(p):
    '''command : PROX ID'''

    p[0] = ('PROX',p[2])

def p_command_next_bad(p):
    '''command : PROX error'''
    p[0] = "PROX erroneo"

def p_command_fin(p):
    '''command : FIN'''
    p[0] = ('FIN',)

def p_command_rem(p):
    '''command : coment'''
    p[0] = ('coment',p[1])

def p_command_stop(p):
    '''command : PARE'''
    p[0] = ('PARE',)

def p_command_def(p):
    '''command : DEF ID IPAREN ID DPAREN IGUAL expr'''
    p[0] = ('FUNC',p[2],p[4],p[7])

def p_command_def_bad_rhs(p):
    '''command : DEF ID IPAREN ID DPAREN IGUAL error'''
    p[0] = "BAD EXPRESSION IN DEF STATEMENT"

def p_command_def_bad_arg(p):
    '''command : DEF ID IPAREN error DPAREN IGUAL expr'''
    p[0] = "BAD ARGUMENT IN DEF STATEMENT"

def p_command_gosub(p):
    '''command : GOSUB ENTERO'''
    p[0] = ('GOSUB',int(p[2]))

def p_command_gosub_bad(p):
    '''command : GOSUB error'''
    p[0] = "INVALID LINE NUMBER IN GOSUB"

def p_command_return(p):
    '''command : RETORNA'''
    p[0] = ('RETORNA',)

def p_command_dim(p):
    '''command : DIM dimlist'''
    p[0] = ('DIM',p[2])

def p_command_dim_bad(p):
    '''command : DIM error'''
    p[0] = "MALFORMED VARIABLE LIST IN DIM"

def p_dimlist(p):
    '''dimlist : dimlist COMA dimitem
               | dimitem'''
    if len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    else:
        p[0] = [p[1]]

def p_dimitem_single(p):
    '''dimitem : ID IPAREN ENTERO DPAREN'''
    p[0] = (p[1],eval(p[3]),0)

def p_dimitem_double(p):
    '''dimitem : ID IPAREN ENTERO COMA ENTERO DPAREN'''
    p[0] = (p[1],eval(p[3]),eval(p[5]))

def p_expr_binary(p):
    '''expr : expr MAS expr
            | expr MENOS expr
            | expr POR expr
            | expr DIVIDE expr
            | expr ELEVADO expr'''

    p[0] = ('binop',p[2],p[1],p[3])

def p_expr_number(p):
    '''expr : ENTERO
            | DECIMAL'''
    p[0] = ('NUM',eval(p[1]))

def p_expr_variable(p):
    '''expr : variable'''
    p[0] = ('VAR',p[1])

def p_expr_group(p):
    '''expr : IPAREN expr DPAREN'''
    p[0] = ('GRUPO',p[2])

def p_expr_unary(p):
    '''expr : MENOS expr %prec UMINUS'''
    p[0] = ('UNARY','-',p[2])

def p_relexpr(p):
    '''relexpr : expr MENOR expr
               | expr MENIGU expr
               | expr MAYOR expr
               | expr MAYIGU expr
               | expr IGUAL expr
               | expr DIFE expr'''
    p[0] = ('relop',p[2],p[1],p[3])

def p_variable(p):
    '''variable : ID
              | ID IPAREN expr DPAREN
              | ID IPAREN expr COMA expr DPAREN'''
    if len(p) == 2:
       p[0] = (p[1],None,None)
    elif len(p) == 5:
       p[0] = (p[1],p[3],None)
    else:
       p[0] = (p[1],p[3],p[5])

def p_varlist(p):
    '''varlist : varlist COMA variable
               | variable'''
    if len(p) > 2:
       p[0] = p[1]
       p[0].append(p[3])
    else:
       p[0] = [p[1]]


def p_numlist(p):
    '''numlist : numlist COMA number
               | number'''

    if len(p) > 2:
       p[0] = p[1]
       p[0].append(p[3])
    else:
       p[0] = [p[1]]

def p_number(p):
    '''number  : ENTERO
               | DECIMAL'''
    p[0] = eval(p[1])

def p_number_signed(p):
    '''number  : MENOS ENTERO
               | MENOS DECIMAL'''
    p[0] = eval("-"+p[2])

def p_plist(p):
    '''plist   : plist COMA pitem
               | pitem'''
    if len(p) > 3:
       p[0] = p[1]
       p[0].append(p[3])
    else:
       p[0] = [p[1]]

def p_item_string(p):
    '''pitem : CADENAT'''
    p[0] = (p[1][1:-1],None)

def p_item_string_expr(p):
    '''pitem : CADENAT expr'''
    p[0] = (p[1][1:-1],p[2])

def p_item_expr(p):
    '''pitem : expr'''
    p[0] = ("",p[1])

def p_empty(p):
    '''empty : '''

def p_error(p):
    if not p:
        print("SYNTAX ERROR AT EOF")

bparser = yacc.yacc()

def parse(data,debug=0):
    bparser.error = 0
    p = bparser.parse(data,debug=debug)
    if bparser.error: return None
    return p