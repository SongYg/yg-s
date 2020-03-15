from .BinaryTree import BinTree


class BST(BinTree):
    def __init__(self, val=None, left=None, right=None):
        super(BST, self).__init__(val, left, right)

    @classmethod
    def find(cls, node, val):
        if not node:
            return None

        if node.val == val:
            return node
        elif node.val > val:
            cls._hot = node
            return cls.find(node.left, val)
        else:
            cls._hot = node
            return cls.find(node.right, val)
        return None

    @classmethod
    def insert(cls, node, val):
        cls._hot = None
        x = cls.find(node, val)
        if x:
            return None
        if not cls._hot:
            return BST(val)
        node_new = BST(val, None, None)

        if val < cls._hot.val:
            cls._hot.left = node_new
        else:
            cls._hot.right = node_new
        return node_new

    @classmethod
    def remove(cls, node, val) -> bool:
        def remove_at(node, parent):
            if node.left is None:
                if parent.left and parent.left.val == node.val:
                    parent.left = node.right
                else:
                    parent.right = node.right
            elif node.right is None:
                if parent.left and parent.left.val == node.val:
                    parent.left = node.right
                else:
                    parent.right = node.right
            else:
                succ = node.succ
                if not succ:
                    raise Exception("tree error")
                node, succ = succ, node
                remove_at(succ, parent)
        cls._hot = None
        x = cls.find(node, val)
        if x:
            remove_at(x, cls._hot)
            return True
        return False


def test_bst():
    root = BST(5)
    print(list(map(str, BST.inorder(root))))
    BST.insert(root, 2)
    BST.insert(root, 3)
    BST.insert(root, 4)
    BST.insert(root, 1)
    BST.insert(root, 7)
    BST.insert(root, 6)
    BST.insert(root, 8)
    print(list(map(str, BST.inorder(root))))
    BST.remove(root, 1)
    BST.remove(root, 6)
    print(list(map(str, BST.inorder(root))))


if __name__ == "__main__":
    test_bst()
