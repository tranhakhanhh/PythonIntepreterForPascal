from parser import *
from scanner import *

debug = False
metadata={}

class Interpreter():
  codeTree = None
  att = {}
  start = 0
  scope_stack = []
  varss = {}
  scope_stack.append(varss)
  fcns = {}



  def setNum(self, node):
    node.value = float(node.getChildren()[0].name)

  def setOp(self, node):
    node.value = node.getChildren()[0].name
    print(node.toString())
    print(node.getChildren()[0].toString())

  def setId(self, node):
    if node.parent.name == "factor" or (node.parent.name == "parameter" and node.myNum == 2):
      if node.getChildren()[0].name not in self.varss:
        print("Error--id not previously created")
        return None
      node.value = self.varss[ node.getChildren()[0].name ]
      if debug:
        print(self.varss, node.value)
    elif node.parent.name == "assignment" or node.parent.name == "parameter":
      if node.getChildren()[0].name not in self.varss:
        self.varss[node.getChildren()[0].name] = None 
        node.value = node.getChildren()[0].name

  def create_fcn(self, node):
    node.getChildren()[1].value = node.getChildren()[1].getChildren()[0].name
    if debug:
      print(8, node.getChildren()[8].name )#[9].getChildren() )
    self.fcns[node.getChildren()[1].value] = node.getChildren()[8]

    # return sets the value of retVal at this scope to be the set of values from stmt_b stmt_b_tail

  def parameter(self, node, args):
    self.att["id"](node.getChildren()[0])
    if debug:
      print("parameter", node.getChildren()[0].value, args, self.varss)
    if len(args) > 0:
      self.varss[node.getChildren()[0].value] = args[0]
      if debug:
        print(self.varss)
    elif len(node.getChildren()) > 1:
      self.att["id"](node.getChildren()[2])
      self.varss[node.getChildren()[0].value] = node.getChildren()[2].value
    else:
      print("Something happened in parameter mapping. Go check it out.")

  def para_list_tail(self, node, args):
    if len(node.getChildren()) > 0:
      self.att["parameter"](node.getChildren()[1], args)
      if len(node.getChildren()[2].getChildren()) > 0:
        if len(args) > 0:
          self.para_list_tail(node.getChildren()[2], args[1:])
        else:
          self.para_list_tail(node.getChildren()[2], args)

  def para_list(self, node, args):
    if len(node.getChildren()) > 0:
      self.att["parameter"](node.getChildren()[0], args)
      if len(node.getChildren()[1].getChildren()) > 0:
        if len(args) > 0:
          self.para_list_tail(node.getChildren()[1], args[1:])
        else:
          self.para_list_tail(node.getChildren()[1], args)

  def assignment(self, node):
    self.att["id"](node.getChildren()[0])
    self.att["expr"](node.getChildren()[2])
    self.varss[node.getChildren()[0].value] = node.getChildren()[2].value

  def stmt_a_list(self, node):
    if len(node.getChildren()) > 0:
      self.att["stmt_a"](node.getChildren()[0])
      self.att["stmt_a_list"](node.getChildren()[1])

  def stmt_a(self, node):
    if debug:
      print(node.name, len(node.getChildren()))
    if node.getChildren()[0].name == "assignment":
      self.att["assignment"](node.getChildren()[0])
    elif node.getChildren()[0].name == "fcn_call":
      self.att["fcn_call"](node.getChildren()[0])
    elif node.getChildren()[0].name == "return":
      self.att["stmt_b"](node.getChildren()[1])
      self.varss["retVal"] = node.getChildren()[1].value

  def userDefinedFcn(self, node, args):
    newVars = {}
    for key, val in self.varss.items():
      newVars[key] = val.copy()
    if debug:
      print(newVars)
    #newVars.extend(self.varss)
    self.scope_stack.append(newVars)
    self.varss = newVars
    self.varss["retVal"] = None #first step is to set a default return value
    #do assignment from parameters to args here
    p = node.parent
    if len(p.getChildren()[3].getChildren()) > 0:
      self.att["para_list"](p.getChildren()[3], args)
    # call each stmt until done
    self.att["stmt_a"](node)
    if len(p.getChildren()[9].getChildren()) > 0 and self.varss["retVal"] == None:
      self.att["stmt_a_list"](p.getChildren()[9])
    #last step is to remove the top set of scope
    if debug:
      print(self.scope_stack)
    fcnVars = self.scope_stack.pop(-1)
    self.varss = self.scope_stack[-1]
    return fcnVars["retVal"]

  def stmt_b_tail(self, node):
    if len(node.getChildren()) == 0:
      node.value = []
    else:
      self.att["expr"](node.getChildren()[1])
      node.value = [ node.getChildren()[1].value ]
      if len(node.getChildren()[2].getChildren() != 0):
        self.att["stmt_b_tail"](node.getChildren()[2])
        node.value.extend(node.getChildren()[2].value)

  def stmt_b(self,node):
      self.att["expr"](node.getChildren()[0])
      node.value = [ node.getChildren()[0].value ]
      if len(node.getChildren()[1].getChildren() ) != 0:
        self.att["stmt_b_tail"](node.getChildren()[1])
        node.value.extend(node.getChildren()[1].value)
      if debug:
        print("stmt_b", node.value)

  def evaluateArgs(self, node):
    print(node.name, len(node.getChildren()), node.getChildren()[0].name)
    if len(node.getChildren()) == 0:
      node.value = []
      return []
    self.att["expr"](node.getChildren()[0])
    node.value = [ node.getChildren()[0].value ]
    print(node.value)
    if len(node.getChildren()[1].getChildren()) != 0:
      self.att["stmt_b_tail"](node.getChildren()[1])
      node.value.extend(node.getChildren()[1].value)
    return node.value

  def FcnHandler(self, node ):
    node.getChildren()[0].name = node.getChildren()[0].getChildren()[0].name
    myFcn = node.getChildren()[0].getChildren()[0].name
    if(debug):
      print(myFcn)
    
    if myFcn == "print":
      print(node.getChildren()[2].name)
      args = self.evaluateArgs(node.getChildren()[2])
      print(args)
      a = ""
      for i in range(len(args)):
        a = a + str(args[i])
        if i < len(args)-1:
          a = a + " "
      print(a)
    else:
      print("Going on a bear hunt!")
      args = self.att["args_list"](node.getChildren()[2])
      print("args", args, node.getChildren()[0].name, self.fcns, self.fcns[ node.getChildren()[0].name ].name)
      output = self.userDefinedFcn(self.fcns[node.getChildren()[0].name], args)
      if len(output) == 1:
        output = output.pop(0)
      node.value = output


  def factor(self, node):
    if node.getChildren()[0].name == "id":
      self.att["id"](node.getChildren()[0])
      print("found an id")
      node.value = node.getChildren()[0].value
    elif node.getChildren()[0].name == "number":
      self.att["number"](node.getChildren()[0])
      node.value = node.getChildren()[0].value
    elif node.getChildren()[0].name == "fcn_call":
      self.att["fcn_call"](node.getChildren()[0])
      node.value = node.getChildren()[0].value
    elif node.getChildren()[1].name == "expr":
      self.att["expr"](node.getChildren()[1])
      node.value = node.getChildren()[1].value
    print("factor value", node.value)

  def term_tail(self, node):
    if len(node.getChildren()) == 0:
      node.Value = None
      return
    self.att["add_op"](node.getChildren()[0])
    self.att["term"](node.getChildren()[1])
    m = None
    q = node.getChildren()[1].value
    p = node.parent
    if p.name == "expr":
      m = p.getChildren()[0].value
    elif p.name == "term_tail":
      m = p.getChildren()[1].value
    if len(node.getChildren()[2].getChildren()) != 0:
      self.att["term_tail"](node.getChildren()[2])
      q = node.getChildren()[2].value
      
    if node.getChildren()[0].value == "+":
       node.Value = m + q
    else:
      node.Value = m - q

  def term(self, node):
    self.att["factor"](node.getChildren()[0])
    print(-1, "term", node.getChildren()[0].value)
    if len(node.getChildren()[1].getChildren()) == 0:
      node.value = node.getChildren()[0].value
      print(0, "term", node.value)
    else:
      self.att["factor_tail"](node.getChildren()[1])
      node.value = node.getChildren()[1].value
      print(1, "term", node.value)

  def expr(self, node):
    self.att["term"](node.getChildren()[0])
    if len(node.getChildren()[1].getChildren()) == 0:
      node.value = node.getChildren()[0].value
      print(0, "expr", node.value)
    else:
      self.att["term_tail"](node.getChildren()[1])
      node.value = node.getChildren()[1].value
      print(1, "expr", node.value)
    
  
  def factor_tail(self, node):
    """This is where I stopped working, 5/7/2021 10:30 pm"""
    if len(node.getChildren()) == 0:
      node.Value = None
      return
    self.att["mult_op"](node.getChildren()[0])
    self.att["factor"](node.getChildren()[1])
    m = None
    q = node.getChildren()[1].value
    print(q, type(q))
    p = node.parent
    if p.name == "term":
      m = p.getChildren()[0].value
    elif p.name == "factor_tail":
      m = p.getChildren()[1].value
    if len(node.getChildren()[2].getChildren()) != 0:
      self.att["factor_tail"](node.getChildren()[2])
      q = node.getChildren()[2].value
    print(m, type(m), q, type(q))
    print(node.name, len(node.getChildren()[2].getChildren()),p.name, p.getChildren()[0].name)
    if node.getChildren()[0].value == "/":
      node.value = m / q
    else:
      node.value = m * q
    print(node.value)

  def stmt(self, node):
    print(node.getChildren()[0].name)
    self.att[node.getChildren()[0].name](node.getChildren()[0])

  def stmt_list(self, node):
    print( len(node.getChildren()))
    if len(node.getChildren()) > 0:
      self.att["stmt"](node.getChildren()[0])
      self.att["stmt_list"](node.getChildren()[2])

  def __init__(self, s):
    self.att["number"] = self.setNum
    self.att["add_op"] = self.setOp
    self.att["mult_op"] = self.setOp
    self.att["id"] = self.setId
    self.att["factor"] = self.factor
    self.att["factor_tail"] = self.factor_tail
    self.att["term"] = self.term
    self.att["term_tail"] = self.term_tail
    self.att["expr"] = self.expr
    self.att["fcn_call"] = self.FcnHandler
    self.att["args_list"] = self.evaluateArgs
    self.att["args_list_tail"] = self.stmt_b_tail
    self.att["stmt_b_tail"] = self.stmt_b_tail
    self.att["parameter"] = self.parameter
    self.att["para_list"] = self.para_list
    self.att["para_list_tail"] = self.para_list_tail
    self.att["create_fcn"] = self.create_fcn
    self.att["assignment"] = self.assignment
    self.att["stmt"] = self.stmt
    self.att["stmt_a"] = self.stmt_a
    self.att["stmt_b"] = self.stmt_b
    self.att["stmt_list"] = self.stmt_list
    self.att["stmt_a_list"] = self.stmt_a_list
    self.codeTree = Parser(s)
    print(self.codeTree.myTree.toString())
    if len(self.codeTree.myTree.head.getChildren()[0].getChildren()) > 0:
      self.att[self.codeTree.myTree.head.getChildren()[0].name](self.codeTree.myTree.head.getChildren()[0])
    # > 0:
    #  self.att[self.codeTree.myTree.head.getChildren()[0].name](self.codeTree.myTree.head.getChildren()[0])
    #self.start = 0

  
  def postFixWalkthrough(self, walkthroughPointer):
    childNum = 0
    while childNum < len(walkthroughPointer.getChildren()):
      self.postFixWalkthrough(walkthroughPointer.getChildren()[childNum])
      childNum += 1
    print(walkthroughPointer.name)
    #visit my node

  def postFix(self):
    self.postFixWalkthrough(self.codeTree.head)

  def findVars(self, walkthroughPointer, treeVars):
    if walkthroughPointer.name == "id":
      v = walkthroughPointer.getChildren()[0].name
      if v not in treeVars:
        treeVars.append(v)
    else:
      childNum = 0
      while childNum < len(walkthroughPointer.getChildren()):
        self.findVars(walkthroughPointer.getChildren()[childNum], treeVars)
        childNum += 1
    #visit my node

  def findAllVars(self):
    treeVars = []
    self.findVars(self.codeTree.head, treeVars)
    return treeVars


if __name__ == "__main__":
  example_object = open("example1.txt")
  example = example_object.read()
  test = Interpreter(example)
  example_object.close()




