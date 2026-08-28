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
        self._size = 0

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
        self._size += 1
        return new_node

    # 기존 Node를 다른 리스트로 옮길 때 사용
    def insert_node_front(self, node):
        self._link(self.head, node, self.head.next)
        self._size += 1

    def insert_back(self, data):
        new_node = Node(data)
        self._link(self.tail.prev, new_node, self.tail)
        self._size += 1

    def remove_node(self, node):
        if node is self.head or node is self.tail or self._size == 0:
            return None
        self._unlink(node)
        data = node.data
        node.prev = None
        node.next = None
        self._size -= 1
        return data
    
    def remove_front(self):
        if self._size == 0:
            return None
        return self.remove_node(self.head.next)

    def remove_back(self):
        if self._size == 0:
            return None
        return self.remove_node(self.tail.prev)
    
    def move_to_front(self, node):
        if self._size == 0 or node.prev is self.head or node is self.head or node is self.tail:
            return
        self._unlink(node)
        self._link(self.head, node, self.head.next)

    # `for item in 리스트:` 문법을 사용할 수 있게 해줌
    # 리스트 내부의 전체 Key나 Value를 순회할 때 코드가 매우 간결해짐
    def __iter__(self):
        curr = self.head.next
        while curr is not self.tail:
            yield curr.data
            curr = curr.next

    # `print(리스트)` 했을 때 예쁘고 알기 쉽게 출력해줌
    # LRU 캐시의 데이터가 순서대로 잘 이동하고 있는지 눈으로 바로 확인 가능
    def __repr__(self):
        nodes = [str(data) for data in self]
        return " -> ".join(nodes) if nodes else "Empty List"

    def __len__(self):
        return self._size