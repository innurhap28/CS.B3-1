# 해시맵 (체이닝)
from doubly_linked_list import DoublyLinkedList

class HashMap:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self._size = 0
        self.buckets = [DoublyLinkedList() for _ in range(capacity)]

    def _hash(self, key):
        # 더 공부하기 : Horner's method
        hash_value = 0
        for char in str(key):
            hash_value = hash_value * 31 + ord(char)
        return hash_value % self.capacity

    def _find_node(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        current = bucket.head.next
        while current is not bucket.tail:
            current_key, _ = current.data
            if current_key == key:
                return bucket, current
            current = current.next
        return bucket, None

    # capacity가 변경되면 버킷 위치가 달라질 수 있으므로 새 버킷에 다시 해싱
    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [DoublyLinkedList() for _ in range(self.capacity)]
        for bucket in old_buckets:
            for key, value in bucket:
                index = self._hash(key)
                self.buckets[index].insert_front((key, value))

    def put(self, key, value):
        bucket, node = self._find_node(key)
        if node is not None:
            node.data = (key, value)
            return
        # _find_node에서 받아온 bucket에 바로 삽입
        bucket.insert_front((key, value))
        self._size += 1
        if self._size / self.capacity > 0.75:
            self._resize()

    def get(self, key):
        _, node = self._find_node(key)
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
        _, node = self._find_node(key)
        return node is not None

    def keys(self):
        all_keys = []
        for bucket in self.buckets:
            for key, value in bucket:
                all_keys.append(key)  # DLL 클래스의 __iter__ 덕분에 간소화됨!
        return all_keys

    def size(self):
        return self._size