# 3개 자료구조를 통합하여 SET/GET/LRU/TTL 로직을 처리하는 핵심 클래스
from doubly_linked_list import DoublyLinkedList
from hash_map import HashMap
from heap import MinHeap

class MiniRedis:
    def __init__(self):
        self.data = HashMap()           # 실제 key-value 저장
        self.lru = DoublyLinkedList()   # LRU 순서 관리
        self.ttl = MinHeap()            # 만료 시간 관리

        self.maxmemory = 0
        self.used_memory = 0
        self.evicted_keys = 0

    def _delete_key(self, key):
        pass