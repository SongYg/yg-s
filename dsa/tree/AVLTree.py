from .BST import BST


class AVLTree(BST):
    def __init__(self, val=None, left=None, right=None):
        super(AVLTree, self).__init__(val, left, right)

    @classmethod
    def insert(cls, node, val):
        pass

    @classmethod
    def remove(cls, node, val):
        pass

    def factor(self):
        return self.stature(self.left) - self.stature(self.right)

    def balanced(self):
        return self.stature(self.left) == self.stature(self.right)
