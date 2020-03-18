from .BST import BST


class AvlTree(BST):
    def __init__(self, val=None, left=None, right=None):
        super(AvlTree, self).__init__(val, left, right)

    @classmethod
    def factor(cls, node):
        return cls.stature(node.left) - cls.stature(node.right)

    @classmethod
    def balanced(cls, node):
        return cls.stature(node.left) == cls.stature(node.right)

    @classmethod
    def avlBalanced(cls, node):
        return cls.factor(node) > -2 and cls.factor(node) < 2

    @classmethod
    def insert(cls, node, val):
        cls._hot = None
        x = cls.find(node, val)
        if x:
            return None
        if not cls._hot:
            return BST(val)
        node_new = BST(val, None, None)

        

    @classmethod
    def remove(cls, node, val):
        pass
