# implementacion de un lenguaje basico (gdos), basado en BASIC, con la finalidad de comprobar el interprete

from ply import *

keywords = (
    'LET','LEER','DATO','IMPRIMIR','CONTINUAR','SI','ENTONCES','PARA','PROX','A','ETAPA',
    'FIN','PARE','DEF','GOSUB','DIM','coment','RETORNA','CORRER','LISTA','NUEVO',
)

tokens = keywords + (
     'IGUAL','MAS','MENOS','POR','DIVIDE','ELEVADO',
     'IPAREN','DPAREN','MENOR','MENIGU','MAYOR','MAYIGU','DIFE',
     'COMA','PCOMA', 'ENTERO','DECIMAL', 'CADENAT',
     'ID','NLINEA'
)

t_ignore = ' \t'

def t_coment(t):
    r'coment .*'
    return t

def t_ID(t):
    r'[A-Z][A-Z0-9]*'
    if t.value in keywords:
        t.type = t.value
    return t
    
t_IGUAL  = r'='
t_MAS    = r'\+'
t_MENOS   = r'-'
t_POR   = r'\*'
t_ELEVADO   = r'\^'
t_DIVIDE  = r'/'
t_IPAREN  = r'\('
t_DPAREN  = r'\)'
t_MENOR      = r'<'
t_MENIGU      = r'<='
t_MAYOR      = r'>'
t_MAYIGU      = r'>='
t_DIFE      = r'<>'
t_COMA   = r'\,'
t_PCOMA    = r';'
t_ENTERO = r'\d+'    
t_DECIMAL   = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
t_CADENAT  = r'\".*?\"'

def t_NLINEA(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(t):
    print("Caracter Ilegal: %s" % t.value[0])
    t.lexer.skip(1)

lex.lex(debug=0)