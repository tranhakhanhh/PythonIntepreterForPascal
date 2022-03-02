class Node():
  name = ""
  children = []
  childNames = []
  parent = None
  value = None
  myNum = -1

  def __init__(self, named):
    self.name = named
    self.children = []
    self.childNames = []
    
  
  def setChildren(self, childrn):
    ch = childrn.split(" ")
    for node in ch:
      self.children.append(Node(node))
      self.children[-1].parent = self
      self.children[-1].myNum = len(self.children)-1
    self.childNames = ch
  
  def getChildren(self):
    return self.children

  def toString(self):
    s = self.name + ":" + str(self.childNames) + "\n"
    for node in self.children:
      s += node.toString()
    return s

class Tree():
  head = None
  cfg = {}

  def __init__(self, named, contextFree):
    self.head = Node(named)
    self.cfg = contextFree
  
  def toString(self):
    return self.head.toString()