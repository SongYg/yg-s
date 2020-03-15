from abc import abstractclassmethod, ABCMeta


class BinTree(metaclass=ABCMeta):
    _hot = None

    def __init__(self, val=None, left=None, right=None, parent=None):
        self.val = val
        self.left = left
        self.right = right
        self.parent = parent
        self._succ = None

    @classmethod
    @abstractclassmethod
    def find(self, val):
        pass

    @classmethod
    @abstractclassmethod
    def insert(self, node):
        pass

    @classmethod
    @abstractclassmethod
    def remove(self, node):
        pass

    @property
    def succ(self):
        _hot = self
        node = self.right
        while node:
            if node.left:
                _hot = node
                node = node.left
            return node
        return None

    def __str__(self):
        return str(self.val)

    @classmethod
    def inorder(cls, node):
        res = []

        def helper(node):
            if node:
                helper(node.left)
                res.append(node)
                helper(node.right)
        helper(node)
        return res

    @classmethod
    def stature(cls, node):
        height = -1

        def helper(node, h):
            if node:
                height = max([height, h])
                helper(node.left, h+1)
                helper(node.right, h+1)
        helper(node, 0)
        return height
