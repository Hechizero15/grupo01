# Este archivo proporciona el soporte de ejecucion para correr un programa basico
# Se asume que el programa ha sido analizado utilizando gdosparse.py

import sys
import math
import random

class GdosInterpreter:

    # Inicializa el interprete. El programa es un diccionario
    # contiene asignaciones (linea,comando)
    def __init__(self,prog):
         self.prog = prog

         self.functions = {           # Construccion de tablas de funciones
             'sen' : lambda z: math.sin(self.eval(z)),
             'cos' : lambda z: math.cos(self.eval(z)),
             'tan' : lambda z: math.tan(self.eval(z)),
             'ctan' : lambda z: math.atan(self.eval(z)),
             'exp' : lambda z: math.exp(self.eval(z)),
             'abs' : lambda z: abs(self.eval(z)),
             'log' : lambda z: math.log(self.eval(z)),
             'raiz' : lambda z: math.sqrt(self.eval(z)),
             'int' : lambda z: int(self.eval(z)),
             'rnd' : lambda z: random.random()
         }

    # funcion que recoge todas los comandos
    def collect_data(self):
         self.data = []
         for lineno in self.stat:
              if self.prog[lineno][0] == 'DATO':
                  self.data = self.data + self.prog[lineno][1]
         self.dc = 0                  # Inicializa el contador de datos

    # funcion que chequea la instruccion FIN
    def check_end(self):
         has_end = 0
         for lineno in self.stat:
             if self.prog[lineno][0] == 'FIN' and not has_end:
                  has_end = lineno
         if not has_end:
             print("Falta la instrucion FIN")
             self.error = 1
             return
         if has_end != lineno:
             print("FIN no esta al final")
             self.error = 1

    # funcion que cheque los bucles
    def check_loops(self):
         for pc in range(len(self.stat)):
             lineno = self.stat[pc]
             if self.prog[lineno][0] == 'PARA':
                  forinst = self.prog[lineno]
                  loopvar = forinst[1]
                  for i in range(pc+1,len(self.stat)):
                       if self.prog[self.stat[i]][0] == 'PROX':
                            nextvar = self.prog[self.stat[i]][1]
                            if nextvar != loopvar: continue
                            self.loopend[pc] = i
                            break
                  else:
                       print("comando 'PARA' sin comando 'PROX' en la linea >> %s" % self.stat[pc])
                       self.error = 1
                  
    # Evalua una expresion
    def eval(self,expr):
        etype = expr[0]
        if etype == 'NUM': return expr[1]
        elif etype == 'GRUPO': return self.eval(expr[1])
        elif etype == 'UNARY':
             if expr[1] == '-': return -self.eval(expr[2])
        elif etype == 'BINOP':
             if expr[1] == '+': return self.eval(expr[2])+self.eval(expr[3])
             elif expr[1] == '-': return self.eval(expr[2])-self.eval(expr[3])
             elif expr[1] == '*': return self.eval(expr[2])*self.eval(expr[3])
             elif expr[1] == '/': return float(self.eval(expr[2]))/self.eval(expr[3])
             elif expr[1] == '^': return abs(self.eval(expr[2]))**self.eval(expr[3])
        elif etype == 'VAR':
             var,dim1,dim2 = expr[1]
             if not dim1 and not dim2:
                  if var in self.vars:
                       return self.vars[var]
                  else:
                       print("Variable no definida >> %s en la linea >> %s" % (var, self.stat[self.pc]))
                       raise RuntimeError
             # puede ser una busqueda de lista o una evaluacion de la funcion
             if dim1 and not dim2:
                if var in self.functions:
                      # Una funcion
                      return self.functions[var](dim1)
                else:
                      # Evaluacion de una lista
                      if var in self.lists:
                            dim1val = self.eval(dim1)
                            if dim1val < 1 or dim1val > len(self.lists[var]):
                                 print("Indice de lista fuera del limite en la linea >> %s" % self.stat[self.pc])
                                 raise RuntimeError
                            return self.lists[var][dim1val-1]
             if dim1 and dim2:
                 if var in self.tables:
                      dim1val = self.eval(dim1)
                      dim2val = self.eval(dim2)
                      if dim1val < 1 or dim1val > len(self.tables[var]) or dim2val < 1 or dim2val > len(self.tables[var][0]):
                           print("Indice de tabla fuera de limite en la linea >> %s" % self.stat[self.pc])
                           raise RuntimeError
                      return self.tables[var][dim1val-1][dim2val-1]
             print("Variable indefinida >> %s en la linea >> %s" % (var, self.stat[self.pc]))
             raise RuntimeError

    # Evalua una expresion relacional
    def releval(self,expr):
         etype = expr[1]
         lhs   = self.eval(expr[2])
         rhs   = self.eval(expr[3])
         if etype == '<':
             if lhs < rhs: return 1
             else: return 0

         elif etype == '<=':
             if lhs <= rhs: return 1
             else: return 0

         elif etype == '>':
             if lhs > rhs: return 1
             else: return 0

         elif etype == '>=':
             if lhs >= rhs: return 1
             else: return 0

         elif etype == '=':
             if lhs == rhs: return 1
             else: return 0

         elif etype == '<>':
             if lhs != rhs: return 1
             else: return 0

    # Asignaciones
    def assign(self,target,value):
        var, dim1, dim2 = target
        if not dim1 and not dim2:
            self.vars[var] = self.eval(value)
        elif dim1 and not dim2:
            # Lista de asignaciones
            dim1val = self.eval(dim1)
            if not var in self.lists:
                 self.lists[var] = [0]*10

            if dim1val > len(self.lists[var]):
                 print ("Dimension demasiado grande en la linea >> %s" % self.stat[self.pc])
                 raise RuntimeError
            self.lists[var][dim1val-1] = self.eval(value)
        elif dim1 and dim2:
            dim1val = self.eval(dim1)
            dim2val = self.eval(dim2)
            if not var in self.tables:
                 temp = [0]*10
                 v = []
                 for i in range(10): v.append(temp[:])
                 self.tables[var] = v
            # la variable ya existe
            if dim1val > len(self.tables[var]) or dim2val > len(self.tables[var][0]):
                 print("Dimension demasiado grande en la linea >> %s" % self.stat[self.pc])
                 raise RuntimeError
            self.tables[var][dim1val-1][dim2val-1] = self.eval(value)

    # cambiar el numero de linea actual
    def goto(self,linenum):
         if not linenum in self.prog:
              print("Numero de linea indefinido >> %d en la linea >> %d" % (linenum, self.stat[self.pc]))
              raise RuntimeError
         self.pc = self.stat.index(linenum)

    # funcion para Correr el programa
    def run(self):
        self.vars   = { }            # todas las variables
        self.lists  = { }            # Lista de variables
        self.tables = { }            # Tablas
        self.loops  = [ ]            # bucles activos
        self.loopend= { }            # mapeo diciendo donde estan los finales de bucles
        self.gosub  = None           # punto de retorno de subrutinas
        self.error  = 0              # Indicador de errores de programa

        self.stat = list(self.prog)  # lista ordenada con todos los numeros de linea
        self.stat.sort()
        self.pc = 0                  # contador del pgrama que esta corriendo

        # Prioridad de procesamiento al correr

        self.collect_data()          
        self.check_end()
        self.check_loops()

        if self.error: raise RuntimeError

        while 1:
            line  = self.stat[self.pc]
            instr = self.prog[line]
            
            op = instr[0]

            # instrucciones FIN y PARE
            if op == 'FIN' or op == 'PARE':
                 break           # finalizamos

            # instruccion CONTINUAR
            elif op == 'CONTINUAR':
                 newline = instr[1]
                 self.goto(newline)
                 continue

            # instruccion IMPRIMIR
            elif op == 'IMPRIMIR':
                 plist = instr[1]
                 out = ""
                 for label,val in plist:
                     if out:
                          out += ' '*(15 - (len(out) % 15))
                     out += label
                     if val:
                          if label: out += " "
                          eval = self.eval(val)
                          out += str(eval)
                 sys.stdout.write(out)
                 end = instr[2]
                 if not (end == ',' or end == ';'): 
                     sys.stdout.write("\n")
                 if end == ',': sys.stdout.write(" "*(15-(len(out) % 15)))
                 if end == ';': sys.stdout.write(" "*(3-(len(out) % 3)))
                     
            # instruccion LET
            elif op == 'LET':
                 target = instr[1]
                 value  = instr[2]
                 self.assign(target,value)

            # instruccion LEER
            elif op == 'LEER':
                 for target in instr[1]:
                      if self.dc < len(self.data):
                          value = ('NUM',self.data[self.dc])
                          self.assign(target,value)
                          self.dc += 1
                      else:
                          # no mas datos.  final del programa
                          return
            elif op == 'SI':
                 relop = instr[1]
                 newline = instr[2]
                 if (self.releval(relop)):
                     self.goto(newline)
                     continue

            elif op == 'PARA':
                 loopvar = instr[1]
                 initval = instr[2]
                 finval  = instr[3]
                 stepval = instr[4]
              
                 # chequea para ver sis e trata de un nuebo bucle
                 if not self.loops or self.loops[-1][0] != self.pc:
                        # Una nueva linea. hacemos la asignacion inicial
                        newvalue = initval
                        self.assign((loopvar,None,None),initval)
                        if not stepval: stepval = ('NUM',1)
                        stepval = self.eval(stepval)    # evalua la etapa aqui
                        self.loops.append((self.pc,stepval))
                 else:
                        # es la repeticion del bucle anterior
                        # actualiza el valor de la variable del bucle de acuerdo a la etapa
                        stepval = ('NUM',self.loops[-1][1])
                        newvalue = ('BINOP','+',('VAR',(loopvar,None,None)),stepval)

                 if self.loops[-1][1] < 0: relop = '>='
                 else: relop = '<='
                 if not self.releval(('RELOP',relop,newvalue,finval)):
                      # Bucle completo. pasamos a la siguiente etapa
                      self.pc = self.loopend[self.pc]
                      self.loops.pop()
                 else:
                      self.assign((loopvar,None,None),newvalue)

            elif op == 'PROX':
                 if not self.loops:
                       print("Comando 'PROX' sin comando 'PARA' en la linea >> %s" % line)
                       return
 
                 nextvar = instr[1]
                 self.pc = self.loops[-1][0]
                 loopinst = self.prog[self.stat[self.pc]]
                 forvar = loopinst[1]
                 if nextvar != forvar:
                       print("Comando 'PROX' sin contexto en la linea >> %s" % line)
                       return
                 continue
            elif op == 'GOSUB':
                 newline = instr[1]
                 if self.gosub:
                       print("Listo en una subrutina en la linea >> %s" % line)
                       return
                 self.gosub = self.stat[self.pc]
                 self.goto(newline)
                 continue

            elif op == 'RETORNA':
                 if not self.gosub:
                      print("Comando 'RETORNA' sin subrutina en la linea >> %s" % line)
                      return
                 self.goto(self.gosub)
                 self.gosub = None

            elif op == 'FUNC':
                 fname = instr[1]
                 pname = instr[2]
                 expr  = instr[3]
                 def eval_func(pvalue,name=pname,self=self,expr=expr):
                      self.assign((pname,None,None),pvalue)
                      return self.eval(expr)
                 self.functions[fname] = eval_func

            elif op == 'DIM':
                 for vname,x,y in instr[1]:
                     if y == 0:
                          # variable de una dimension 
                          self.lists[vname] = [0]*x
                     else:
                          # variable de dos dimensiones
                          temp = [0]*y
                          v = []
                          for i in range(x):
                              v.append(temp[:])
                          self.tables[vname] = v

            self.pc += 1         

    # funciones de utilidad para la inclusion del programa
    def expr_str(self,expr):
        etype = expr[0]
        if etype == 'NUM': return str(expr[1])
        elif etype == 'GRUPO': return "(%s)" % self.expr_str(expr[1])
        elif etype == 'UNARY':
             if expr[1] == '-': return "-"+str(expr[2])
        elif etype == 'BINOP':
             return "%s %s %s" % (self.expr_str(expr[2]),expr[1],self.expr_str(expr[3]))
        elif etype == 'VAR':
              return self.var_str(expr[1])

    def relexpr_str(self,expr):
         return "%s %s %s" % (self.expr_str(expr[2]),expr[1],self.expr_str(expr[3]))

    def var_str(self,var):
         varname,dim1,dim2 = var
         if not dim1 and not dim2: return varname
         if dim1 and not dim2: return "%s(%s)" % (varname, self.expr_str(dim1))
         return "%s(%s,%s)" % (varname, self.expr_str(dim1),self.expr_str(dim2))

    # Crear un listado de programas
    def list(self):
         stat = list(self.prog)      # lista ordenada de todos los numeros de linea
         stat.sort()
         for line in stat:
             instr = self.prog[line]
             op = instr[0]
             if op in ['FIN','PARE','RETORNA']:
                   print("%s %s" % (line, op))
                   continue
             elif op == 'coment':
                   print("%s %s" % (line, instr[1]))
             elif op == 'IMPRIMIR':
                   _out = "%s %s " % (line, op)
                   first = 1
                   for p in instr[1]:
                         if not first: _out += ", "
                         if p[0] and p[1]: _out += '"%s"%s' % (p[0],self.expr_str(p[1]))
                         elif p[1]: _out += self.expr_str(p[1])
                         else: _out += '"%s"' % (p[0],)
                         first = 0
                   if instr[2]: _out += instr[2]
                   print(_out)
             elif op == 'LET':
                   print("%s LET %s = %s" % (line,self.var_str(instr[1]),self.expr_str(instr[2])))
             elif op == 'LEER':
                   _out = "%s LEER " % line
                   first = 1
                   for r in instr[1]:
                         if not first: _out += ","
                         _out += self.var_str(r)
                         first = 0
                   print(_out)
             elif op == 'SI':
                   print("%s SI %s ENTONCES %d" % (line,self.relexpr_str(instr[1]),instr[2]))
             elif op == 'CONTINUAR' or op == 'GOSUB':
                   print("%s %s %s" % (line, op, instr[1]))
             elif op == 'PARA':
                   _out = "%s PARA %s = %s A %s" % (line,instr[1],self.expr_str(instr[2]),self.expr_str(instr[3]))
                   if instr[4]: _out += " ETAPA %s" % (self.expr_str(instr[4]))
                   print(_out)
             elif op == 'PROX':
                   print("%s PROX %s" % (line, instr[1]))
             elif op == 'FUNC':
                   print("%s DEF %s(%s) = %s" % (line,instr[1],instr[2],self.expr_str(instr[3])))
             elif op == 'DIM':
                   _out = "%s DIM " % line
                   first = 1
                   for vname,x,y in instr[1]:
                         if not first: _out += ","
                         first = 0
                         if y == 0:
                               _out += "%s(%d)" % (vname,x)
                         else:
                               _out += "%s(%d,%d)" % (vname,x,y)
                         
                   print(_out)
             elif op == 'DATO':
                   _out = "%s DATO " % line
                   first = 1
                   for v in instr[1]:
                        if not first: _out += ","
                        first = 0
                        _out += v
                   print(_out)

    # borra el programa actual
    def new(self):
         self.prog = {}
 
    # adiciona una instruccion
    def add_statements(self,prog):
         for line,stat in prog.items():
              self.prog[line] = stat

    # borra una instriccion
    def del_line(self,lineno):
         try:
             del self.prog[lineno]
         except KeyError:
             pass