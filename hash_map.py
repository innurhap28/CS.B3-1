# 해시맵 (체이닝)
from doubly_linked_list import DoublyLinkedList

class HashMap:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self._size = 0
        self.buckets = [DoublyLinkedList() for _ in range(capacity)]

    def _hash(self, key):
        hash_value = 0
        for char in key:
            hash_value = hash_value * 31 + ord(char)
        return hash_value % self.capacity

    def _find_node(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        current = bucket.head.next
        while current is not bucket.tail:
            current_key, current_value = current.data
            if current_key == key:
                return bucket, current
            current = current.next
        return None, None

    # 같은 key라도 버킷 위치가 달라질 수 있으므로 새 버킷에 넣음
    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [DoublyLinkedList() for _ in range(self.capacity)]
        for bucket in old_buckets:
            current = bucket.head.next
            while current is not bucket.tail:
                key, value = current.data
                index = self._hash(key)
                self.buckets[index].insert_front((key, value))
                current = current.next

    def put(self, key, value):
        bucket, node = self._find_node(key)
        if node is not None:
            node.data = (key, value)
            return
        index = self._hash(key)
        bucket = self.buckets[index]
        bucket.insert_front((key, value))
        self._size += 1
        if self._size / self.capacity > 0.75:
            self._resize()

    def get(self, key):
        bucket, node = self._find_node(key)
        if node is not None:
            key, value = node.data
            return value
        return None

    def remove(self, key):
        bucket, node = self._find_node(key)
        if node is not None:
            key, value = node.data
            bucket.remove_node(node)
            self._size -= 1
            return value
        return None

    def contains(self, key):
        bucket, node = self._find_node(key)
        return node is not None

    def keys(self):
        result = []
        for bucket in self.buckets:
            current = bucket.head.next
            while current is not bucket.tail:
                current_key, current_value = current.data
                result.append(current_key)
                current = current.next
        return result

    def size(self):
        return self._size