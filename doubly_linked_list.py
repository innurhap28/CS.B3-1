# 이중 연결 리스트

# Node : 데이터 하나와 앞 뒤 Node의 주소를 가지고 있는 상자
class Node:
    def __init__(self, data):
        self.data = data 
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        # Sentinel Node 사용
        self.head = Node(None)
        self.tail = Node(None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    # 포인터 연결 전용 헬퍼 함수
    @staticmethod
    def _link(prev_node, new_node, next_node):
        new_node.prev = prev_node
        new_node.next = next_node
        prev_node.next = new_node
        next_node.prev = new_node

    @staticmethod
    def _unlink(node):
        node.prev.next = node.next
        node.next.prev = node.prev

    # new_node와 양쪽 노드의 포인터만 변경하기 때문에 데이터 개수에 관계없이 항상 일정한 횟수의 연산이 수행 -> 시간 복잡도는 O(1).
    def insert_front(self, data):
        new_node = Node(data)
        self._link(self.head, new_node, self.head.next)
        self.size += 1

    def insert_back(self, data):
        new_node = Node(data)
        self._link(self.tail.prev, new_node, self.tail)
        self.size += 1

    def remove_node(self, node):
        if node is self.head or node is self.tail or self.size == 0:
            return None
        self._unlink(node)
        data = node.data
        node.prev = None
        node.next = None
        self.size -= 1
        return data
    
    def remove_front(self):
        if self.size == 0:
            return None
        return self.remove_node(self.head.next)

    def remove_back(self):
        if self.size == 0:
            return None
        return self.remove_node(self.tail.prev)
    
    def move_to_front(self, node):
        if self.size == 0 or node.prev is self.head or node is self.head or node is self.tail:
            return
        self._unlink(node)
        self._link(self.head, node, self.head.next)