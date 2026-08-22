# 이중 연결 리스트

# Node : 데이터 하나와 앞 뒤 Node의 주소를 가지고 있는 상자
class Node:
    def __init__(self, data):
        self.data = data 
        self.prev = None
        self.next = None

# insert_front()는 new_node, head, 그리고 기존 head의 포인터 몇 개만 변경하기 때문에 데이터 개수에 관계없이 항상 일정한 횟수의 연산이 수행된다. 따라서 시간 복잡도는 O(1)이다.
class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def insert_front(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def insert_back(self, data):
        new_node = Node(data)

        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def remove_front(self):
        if self.head is None:
            return

        self.head = self.head.next
        
        if self.head is None:
            self.tail = None
        else:
            self.head.prev = None
        self.size -= 1

    def remove_back(self):
        if self.tail is None:
            return

        self.tail = self.tail.prev

        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None
        self.size -= 1

    def remove_node(self, node):
        if node is self.head:
            self.remove_front()
        elif node is self.tail:
            self.remove_back()
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
            self.size -=1

    def move_to_front(self, node):
        if node is self.head:
            return

        if node is self.tail:
            self.tail = node.prev
            node.prev.next = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev

        node.next = self.head
        node.prev = None
        self.head.prev = node
        self.head = node