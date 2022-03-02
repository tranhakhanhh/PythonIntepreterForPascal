from scanner import Scanner
from tree import Tree
from tree import Node

debug=False



class Parser():
  cfg = {}
  scan_string = ""
  myTree = None
  myPointer = None
  myScanner = None
  CURRENT_FUNCTION_NAME = None #track of which function some current token belong in

  def validNumber(self, token):
    #return True if token is a valid number
    return token[0].isdigit()
    
  def validId(self, token):
    #return True if token is a valid character that can be used as names
    return 97 <= ord(token[0]) <= 122 or 65 <= ord(token[0]) <= 97 or ord(token[0]) == 95

  def id(self, node, token):
    #Checks validity of token then return the next token in line
    if self.validId(token):
      return self.myScanner.nextToken()
    else:
      raise Exception("Invalid id")

  def id_list(self, node, token):
    #<id_list> -> <id> <id_list_tail>
    #self.cfg["id_list"] = ["id id_list_tail"]
    node.setChildren(self.cfg["id_list"][0])
    token = self.id(node.getChildren()[0], token)
    token = self.id_list_tail(node.getChildren()[1], token)
    return token

  def id_list_tail(self, node, token):
    #<id_list_tail> -> E | ,<id><id_list_tail>
    #self.cfg["id_list_tail"] = ["", ", id id_list_tail"
    if token == ":":
      pass #do nothing
    else:
      node.setChildren(self.cfg["id_list_tail"][1])
      if token == ",":
        token = self.myScanner.nextToken()
      else:
        raise Exception("Parsing error")
      token = self.id(node.getChildren()[1], token)
      token = self.id_list_tail(node.getChildren()[2], token)
    return token
  
  def type(self, node, token):
    #Confirm valid type, then return next token
    if token in self.cfg["type"]:
      return self.myScanner.nextToken()
    else:
      raise Exception("type error")

  def body(self, node, token):
    #<body> -> <declaration_funcdef_list> begin <func_call>; end.
    #self.cfg["body"] = [ "declaration_funcdef_list begin func_call ; end ."]

    node.setChildren(self.cfg["body"][0])
    print("Token is:", token, node.getChildren()[0].name)
    token = self.declaration_funcdef_list(node.getChildren()[0], token)
    print(token)
    if token == "begin":
      token = self.myScanner.nextToken()
      token = self.func_call(node.getChildren()[2], token)
    else:
      raise Exception("Parsing error 1")
    print(token)
    if token == ";":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error 2")
    if token == "end":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error 3")
    if token == ".":
      return self.myScanner.nextToken()
    else:
      raise Exception("Parsing error 4")
  
  def declaration_funcdef_list(self, node, token):
    #<declaration_funcdef_list> -> <declaration_funcdef> <declaration_funcdef_list> | E
    #self.cfg["declaration_funcdef_list"] = [ "declaration_funcdef declaration_funcdef_list",""]
    print("In declaration_funcdef_list")
    if token not in ["var", "function"]: # if declaration_funcdef_list is empty
      print("token not in var, function", token)
      return token
    else:
      node.setChildren(self.cfg["declaration_funcdef_list"][0])
      token = self.declaration_funcdef(node.getChildren()[0], token)
      token = self.declaration_funcdef_list(node.getChildren()[1], token)
    return token
  
  def declaration_funcdef(self, node, token):
    print("declaration_funcdef", token)
    if token == "var": #it is declaration_chunk
      node.setChildren(self.cfg["declaration_funcdef"][0])
      token = self.declaration_chunk(node.getChildren()[0], token)
    elif token == "function": #it is func_def
      node.setChildren(self.cfg["declaration_funcdef"][1])
      token = self.func_def(node.getChildren()[0], token)
    else: #it is empty
      pass #do nothing
    return token
  
  def declaration_chunk(self, node, token):
    print("declaration_chunk", token)
    if token == "var":
      node.setChildren(self.cfg["declaration_chunk"][0])
      token = self.myScanner.nextToken()
      token = self.declare_list(node.getChildren()[1], token)
    else: # it is empty
      pass #do nothing
    return token
  
  def declare_list(self, node, token):
    print("declare_list", token)
  #<declare_list> -> <declare> <declare_list> | E
  #self.cfg["declare_list"] = [ "declare declare_list", ""]
    if self.validId(token) and token not in ["begin", "end", "var", "program", "function", "for", "to", "do", "if", "then", "else", "repeat", "until"]: #if declare_list is not empty:
      node.setChildren(self.cfg["declare_list"][0])
      token = self.declare(node.getChildren()[0], token)
      token = self.declare_list(node.getChildren()[1], token)
    else: # it is empty
      pass #do nothing
    return token

  def declare(self, node, token):
    print("declare", token)
    #<declare> -> <id_list>: <type>;
    #self.cfg["declare"] = [ "id_list : type ;"]
    node.setChildren(self.cfg["declare"][0])
    token = self.id_list(node.getChildren()[0], token)
    if token == ":":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    if token in self.cfg["type"]:
      token = self.myScanner.nextToken()
    else:
      raise Exception("type error")
    if token == ";":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    return token

  def func_def(self, node, token):
    print("func_def", token)
    #<func_def> -> function<id>(<para_list>):<type>;<declaration_chunk>begin<block_list><return_statement>end;
    #self.cfg["func_def"] = [ "function id ( para_list ) : type ; declaration_chunk begin block_list return_statement end ;"]
    node.setChildren(self.cfg["func_def"][0])
    if token == "function":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    if self.validId(token):
      self.CURRENT_FUNCTION_NAME = token
      self.cfg["fcn_names"].append(token)
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    if token == "(":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    token = self.para_list(node.getChildren()[3], token)

    if token == ")":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    if token == ":":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    if token in self.cfg["type"]:
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    if token == ";":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    token = self.declaration_chunk(node.getChildren()[8], token)

    if token == "begin":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    token = self.block_list(node.getChildren()[10], token)
    token = self.return_statement(node.getChildren()[11], token)

    if token == "end":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    print("IN func_def after end")
    if token == ";":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    print("IN func_def after ;")
    return token

  def para_list(self, node, token):
    print("para_list", token)
    #<para_list> -> <para> <para_list_tail> | E
    #self.cfg["para_list"] = [ "para para_list_tail", ""]
    if token == ")": #para list is empty
      return token
    else:
      node.setChildren(self.cfg["para_list"][0])
      token = self.para(node.getChildren()[0], token)
      token = self.para_list_tail(node.getChildren()[1], token)
    return token

  def para_list_tail(self, node, token):
    print("para_list_tail", token)
    #<para_list_tail> -> E | ,<para><para_list_tail>
    #self.cfg["para_list_tail"] = [ ", para para_list_tail", ""]
    if token == ")": #para list tail is empty
      return token
    else:
      node.setChildren(self.cfg["para_list_tail"][0])
      if token == ",":
        token = self.myScanner.nextToken()
      else:
        raise Exception("Parsing error")
      token = self.para(node.getChildren()[1], token)
      token = self.para_list_tail(node.getChildren()[2], token)
    return token

  def para(self, node, token):
    print("para", token)
    #<para> -> <id>:<type>
    #self.cfg["para"] = [ "id : type"]
    node.setChildren(self.cfg["para"][0])
    token = self.id(node.getChildren()[0], token)
    if token == ":":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    if token in self.cfg["type"]:
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    return token

  def block_list(self, node, token):
    print("block_list", token)
    #<block_list> -><block> <block_list> | E
    #self.cfg["block_list"] = [ "block block_list", ""]
    if token in ["end", "until"] or token == self.CURRENT_FUNCTION_NAME: #block list is empty
      return token
    else:
      node.setChildren(self.cfg["block_list"][0])
      token = self.block(node.getChildren()[0], token)
      token = self.block_list(node.getChildren()[1], token)
    return token

  def block(self, node, token):
    print("block", token)
    #<block> -> <assignment> | <func_call>; | begin <block_list> end; | <if_statement> | <for_loop> | <repeat_statement>
    #self.cfg["block"] = [ "assignment", "func_call ;","begin block_list end ;","if_statement","for_loop","repeat_statement"]
    if token in self.cfg["fcn_names"]:
      node.setChildren(self.cfg["block"][1])
      token=self.func_call(node.getChildren()[0],token)
      if token == ";":
        token = self.myScanner.nextToken()
      else:
        raise Exception("Parsing error")
    elif token == "begin":
      node.setChildren(self.cfg["block"][2])
      token = self.myScanner.nextToken()
      token = self.block_list(node.getChildren()[1], token)
      if token == "end":
        token = self.myScanner.nextToken()
      else:
        raise Exception("Parsing error")
      if token == ";":
        token = self.myScanner.nextToken()
      else:
        raise Exception("Parsing error")
    elif token == "if":
      node.setChildren(self.cfg["block"][3])
      token = self.if_statement(node.getChildren()[0], token)
    elif token == "for":
      node.setChildren(self.cfg["block"][4])
      token = self.for_loop(node.getChildren()[0], token)
    elif token == "repeat":
      node.setChildren(self.cfg["block"][5])
      token = self.repeat_statement(node.getChildren()[0], token)
    else:
      node.setChildren(self.cfg["block"][0])
      token = self.assignment(node.getChildren()[0], token)
    print("End of block", token)
    return token


  def for_loop(self, node, token):
    print("for_loop", token)
    #<for_loop> -> for <id>:=<expr> to <expr> do <assignment>
    #self.cfg["for_loop"] = [ "for id := expr to expr do assignment"]
    node.setChildren(self.cfg["for_loop"][0])
    if token == "for":
      token = self.myScanner.nextToken()
    else: 
      raise Exception("Parsing error")

    token = self.id(node.getChildren()[1], token)

    if token == ":=":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    token = self.expr(node.getChildren()[3], token)

    if token == "to":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    token = self.expr(node.getChildren()[5], token)

    if token == "do":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")

    token = self.assignment(node.getChildren()[7], token)
    
    return token

  
  def if_statement(self, node, token):  
    print("if_statement", token)  
    #<if_statement>  -> if <comparison> then <block> <if_statement_tail>
    #self.cfg["if_statement"] = [ "if comparison then block if_statement_tail"]

    node.setChildren(self.cfg["if_statement"][0])
    if token == "if":
      token = self.myScanner.nextToken()
      token = self.comparison(node.getChildren()[1], token)
    else:
      raise Exception("Parsing error")
    if token == "then":
      token = self.myScanner.nextToken()
      token = self.block(node.getChildren()[3], token)
      token = self.if_statement_tail(node.getChildren()[4], token)
    else:
      raise Exception("Parsing error")
    return token

  

  def if_statement_tail(self, node, token): 
    print("if_statement_tail", token)   
    #<if_statement_tail> -> E | else <block>
    #self.cfg["if_statement_tail"] = [ "","else block"]

    if token !="else": 
      return token
    else:
      node.setChildren(self.cfg["if_statement_tail"][1])
      if token == "else":
        token = self.myScanner.nextToken()
        token = self.block(node.getChildren()[1], token)
        print("in if_statement,", token)
      else:
        raise Exception("Parsing error")
    print("End of if statement", token)
    return token

  
  def comparison(self, node, token):
    print("comparison", token)
    #<comparison> -> <expr> <comp_op> <expr>
    #self.cfg["comparison"] = [ "expr comp_op expr"]
    node.setChildren(self.cfg["comparison"][0])
    token = self.expr(node.getChildren()[0], token)
    token = self.comp_op(node.getChildren()[1], token)
    token = self.expr(node.getChildren()[2], token)

    return token
  
  def comp_op(self,node, token):
    print("comp_op", token)
    #<comp_op> -> > | < | =
    #self.cfg["comp_op"] = [ ">","<","="]
    if token in self.cfg["comp_op"]: 
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    return token

  def repeat_statement(self, node, token):
    print("repeat_statement", token)
    #<repeat_statement> -> repeat <block_list> until <comparison>;
    #self.cfg["repeat_statement"] = [ "repeat block_list until comparison ;"]
    
    node.setChildren(self.cfg["repeat_statement"][0])
    if token == "repeat":
      token = self.myScanner.nextToken()
      token = self.block_list(node.getChildren()[1], token)
    else:
      raise Exception("Parsing error")
    if token == "until":
      token = self.myScanner.nextToken()
      token = self.comparison(node.getChildren()[3], token)
    else:
      raise Exception("Parsing error")
    if token == ";":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    return token

  def return_statement(self, node, token):
    print("return_statement", token)
    #<return_statement> -> <id> := <expr>;
    #self.cfg["return_statement"] = [ "id := expr ;"]
    node.setChildren(self.cfg["return_statement"][0])
    token = self.id(node.getChildren()[0], token)
    if token == ":=":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    token = self.expr(node.getChildren()[2], token)
    if token == ";":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    print("End of return_statement", token)
    return token

  def func_call(self, node, token):
    print("func_call", token)
    #<func_call> -> <id>(<argu_list>)
    #self.cfg["func_call"] = [ "id ( argu_list ) "]
    node.setChildren(self.cfg["return_statement"][0])
    if token in self.cfg["fcn_names"]:
      # check if function name has been defined
      token = self.myScanner.nextToken()
    else: 
      raise Exception("function not defined")
    if token == "(":
      token = self.myScanner.nextToken()
      token = self.argu_list(node.getChildren()[2], token)
    else:
      raise Exception("Parsing error")
    if token == ")":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    return token

  def argu_list(self, node, token): 
    print("argu_list", token)   
    #<argu_list> -> <expr> <argu_list_tail> | E
    #self.cfg["argu_list"] = [ "expr argu_list_tail",""]

    if token ==")": 
      return token
    else:
      node.setChildren(self.cfg["argu_list"][0])
      token = self.expr(node.getChildren()[0], token)
      token = self.argu_list_tail(node.getChildren()[1], token)
    return token
  
  def argu_list_tail(self, node, token):
    print("argu_list_tail", token)
    #<argu_list_tail> -> E | ,<expr><argu_list_tail>
    #self.cfg["argu_list_tail"] = [ ", expr argu_list_tail",""]
    if token ==")": 
      return token
    else:
      node.setChildren(self.cfg["argu_list_tail"][0])
      if token == ",":
        token = self.myScanner.nextToken()
      else:
        raise Exception("Parsing error")
      token = self.expr(node.getChildren()[1], token)
      token = self.argu_list_tail(node.getChildren()[2], token)
    return token


  def assignment(self, node, token):
    print("assignment", token)
    #<assignment> -> <id> := <expr>;
    #self.cfg["assignment"] = [ "id := expr ;"]
    node.setChildren(self.cfg["assignment"][0])
    token = self.id(node.getChildren()[0], token)
    if token == ":=":
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")  
    token = self.expr(node.getChildren()[2], token)
    if token == ";":
      token = self.myScanner.nextToken()
    else:
      print(token)
      raise Exception("Parsing error")  
    return token

  def expr(self, node, token):
    print("expr", token)
    #<expr> -> <term> <term_tail>
    #self.cfg["expr"] = [ "term term_tail"]
    node.setChildren(self.cfg["expr"][0])
    token = self.term(node.getChildren()[0], token)
    token = self.term_tail(node.getChildren()[1], token)  
    return token  


  def term_tail(self, node, token):
    print("term_tail", token)
    #<term_tail> -> <add_op> <term> <term_tail> | E
    #self.cfg["term_tail"] = [ "add_op term term_tail",""]
   
    if token in self.cfg["add_op"]:    
      node.setChildren(self.cfg["term_tail"][0])
      token = self.myScanner.nextToken()
      token = self.term(node.getChildren()[1], token)  
      token = self.term_tail(node.getChildren()[2], token)  
    return token  

  def term(self, node, token):
    print("term", token)
    #<term> -> <factor> <factor_tail>
    #self.cfg["term"] = [ "factor factor_tail"]
    node.setChildren(self.cfg["term"][0])
    token = self.factor(node.getChildren()[0], token)
    token = self.factor_tail(node.getChildren()[1], token)  
    return token  

  def factor_tail(self, node, token):
    print("factor_tail", token)
    #<factor_tail> -> <mult_op> <factor> <factor_tail> | E
    #self.cfg["factor_tail"] = [ "mult_op factor factor_tail",""]
   
    if token in self.cfg["mult_op"]:    
      node.setChildren(self.cfg["factor_tail"][0])
      token = self.mult_op(node.getChildren()[0], token)
      token = self.factor(node.getChildren()[1], token)  
      token = self.factor_tail(node.getChildren()[2], token)  
    return token  


  def factor(self, node, token):
    print("factor", token)
    #<factor> -> \(<expr>\) | id | number | <func_call> |<string>
    #self.cfg["factor"] = ["( expr )", "id", "number", "func_call","string"]
    if token == "(":
      node.setChildren(self.cfg["factor"][0])
      token = self.myScanner.nextToken()
      token = self.expr(node.getChildren()[1], token)
      if token == ")":
        token = self.myScanner.nextToken()
      else:
        raise Exception("Parsing error")
    elif token in self.cfg["fcn_names"]: 
      node.setChildren(self.cfg["factor"][3])
      token = self.func_call(node.getChildren()[0], token)
    elif self.validId(token):
      node.setChildren(self.cfg["factor"][1])
      # node.getChildren()[0].setChildren(token)
      token = self.myScanner.nextToken()
    elif self.validNumber(token):
      node.setChildren(self.cfg["factor"][2])
      #node.getChildren()[0].setChildren(token)
      token = self.myScanner.nextToken()
    elif token[0] == "'":
      node.setChildren(self.cfg["factor"][4])
      #node.getChildren()[0].setChildren(token)
      token = self.myScanner.nextToken()
    else:
      raise Exception("Parsing error")
    return token


  def __init__(self, scanS):
    #ATRIBUTE-RELATED
    self.cfg["fcn_names"]=["writeln", "length", "dec"]
    self.cfg["type"]=["string", "integer"] #currently support only types in our examples

    # NORMAL CFG
    # id list
    #<id_list> -> <id> <id_list_tail>
    self.cfg["id_list"] = ["id id_list_tail"]
    
    #<id_list_tail> -> E | ,<id><id_list_tail>
    self.cfg["id_list_tail"] = ["", ", id id_list_tail"]

    #<heading> -> program <id>; <body>
    self.cfg["heading"] = [ "program id ; body"]



    #<body> -> <declaration_funcdef_list> begin <func_call> ; end.
    self.cfg["body"] = [ "declaration_funcdef_list begin func_call ; end ."]



    #<declaration_funcdef_list> -><declaration_funcdef> <declaration_funcdef_list>| E
    self.cfg["declaration_funcdef_list"] = [ "declaration_funcdef declaration_funcdef_list",""]

    #<declaration_funcdef> ->  <declaration_chunk> | <func_def> |  E
    self.cfg["declaration_funcdef"] = [ "declaration_chunk","func_def",""]


    #<declaration_chunk> -> var <declare_list> | E
    self.cfg["declaration_chunk"] = [ "var declare_list",""]
    
    #<declare_list> -> <declare_list> <declare> | <declare>
    self.cfg["declare_list"] = [ "declare declare_list", ""]

    #<declare> -> <id_list>: <type>;
    self.cfg["declare"] = [ "id_list : type ;"]

    #<func_def> -> function<id>(<para_list>):<type>;<declaration_chunk>begin<block_list><return_statement>end;
    self.cfg["func_def"] = [ "function id ( para_list ) : type ; declaration_chunk begin block_list return_statement end ;"]

    #<para_list> -> <para> <para_list_tail> | E
    self.cfg["para_list"] = [ "para para_list_tail", ""]

    #<para_list_tail> -> E | ,<para><para_list_tail>
    self.cfg["para_list_tail"] = [ ", para para_list_tail", ""]

    #<para> -> <id>:<type>
    self.cfg["para"] = [ "id : type"]


    #<block_list> -><block_list> <block> | E
    self.cfg["block_list"] = [ "block block_list", ""]

    #<block> -> <assignment> | <func_call>; | begin <block_list> end; | <if_statement> | <for_loop> | <repeat_statement>
    self.cfg["block"] = [ "assignment", "func_call ;","begin block_list end ;","if_statement","for_loop","repeat_statement"]

    #<for_loop> -> for <id>:=<expr> to <expr> do <assignment>
    self.cfg["for_loop"] = [ "for id := expr to expr do assignment"]



    #<if_statement>  -> if <comparison> then <block> <if_statement_tail>
    self.cfg["if_statement"] = [ "if comparison then block if_statement_tail"]
    
    #<if_statement_tail> -> E | else <block>
    self.cfg["if_statement_tail"] = [ "","else block"]
    
    #<comparison> -> <expr> <comp_op> <expr>
    self.cfg["comparison"] = [ "expr comp_op expr"]
    
    #<comp_op> -> > | < | =
    self.cfg["comp_op"] = [ ">","<","="]

    #<repeat_statement> -> repeat <block_list> until <comparison>;
    self.cfg["repeat_statement"] = [ "repeat block_list until comparison ;"]

    #<return_statement> -> <id> := <expr>;
    self.cfg["return_statement"] = [ "id := expr ;"]



    #<func_call> -> <id>(<argu_list>)
    self.cfg["func_call"] = [ "id ( argu_list )"]
    
    #<argu_list> -> <expr> <argu_list_tail> | E
    self.cfg["argu_list"] = [ "expr argu_list_tail",""]
    
    #<argu_list_tail> -> E | ,<expr><argu_list_tail>
    self.cfg["argu_list_tail"] = [ ", expr argu_list_tail",""]
    



    #<assignment> -> <id> := <expr>;
    self.cfg["assignment"] = [ "id := expr ;"]

    #<expr> -> <term> <term_tail>
    self.cfg["expr"] = [ "term term_tail"]

    #<term_tail> -> <add_op> <term> <term_tail> | E
    self.cfg["term_tail"] = [ "add_op term term_tail",""]


    #<term> -> <factor> <factor_tail>
    self.cfg["term"] = [ "factor factor_tail"]

    #<factor_tail> -> <mult_op> <factor> <factor_tail> | E
    self.cfg["factor_tail"] = [ "mult_op factor factor_tail",""]

    #<factor> -> \(<expr>\) | id | number | <func_call> |<string>
    self.cfg["factor"] = ["( expr )", "id", "number", "func_call","string"]


    self.cfg["mult_op"] = ["/", "*"] #done
    self.cfg["add_op"] = [ "+", "-"] #done
    # self.cfg["number"] = r"([0-9]+\.?[0-9]*)" #done
    # self.cfg["id"] = r"([A-Za-z_]+[A-Za-z0-9_]*)" #done

    # Code to scan
    self.scan_string = scanS
    self.myScanner = Scanner(self.cfg)
    self.myScanner.startScan(scanS)
    t = self.myScanner.nextToken()
    if t != "$$":
        self.myTree = Tree("heading", self.cfg)
        self.myPointer = self.myTree.head
        self.myPointer.setChildren(self.cfg["heading"][0])
        if t == "program":
          t = self.myScanner.nextToken()
          t = self.id(self.myPointer.getChildren()[1], t)
        else:
          raise Exception("CANNOT PARSE")
        if t == ";":
          t = self.myScanner.nextToken()
          t = self.body(self.myPointer.getChildren()[3], t)
        else:
          raise Exception("CANNOT PARSE")


#test parser
if __name__ == "__main__":
  example_object = open("example4.txt")
  example = example_object.read()
  test = Parser(example)
  example_object.close()
