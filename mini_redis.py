# 3개 자료구조를 통합하여 SET/GET/LRU/TTL 로직을 처리하는 핵심 클래스
from doubly_linked_list import DoublyLinkedList, Node
from hash_map import HashMap
from heap import MinHeap
import time

class MiniRedis:
    def __init__(self):
        self.data = HashMap()           # 실제 key-value 저장
        self.lru = DoublyLinkedList()   # LRU 순서 관리
        self.ttl = MinHeap()            # 만료 시간 관리

        self.maxmemory = 0
        self.used_memory = 0
        self.evicted_keys = 0

    def _delete_key(self, key):
        node = self.data.get(key)
        if node:
            _, value = node.data
            self.data.remove(key)
            self.lru.remove_node(node)

            key_bytes = len(str(key).encode("utf-8"))
            val_bytes = len(str(value).encode("utf-8"))
            self.used_memory -= (key_bytes + val_bytes)

    def _calculate_memory(self, key, value):
        pass

    def _evict_if_needed(self):
        """
        maxmemory 초과 시 가장 오래 전에 사용된 데이터(tail 쪽) 삭제
        """
        if self.maxmemory <= 0:
            return

        while self.used_memory > self.maxmemory and self.lru._size > 0:
            oldest_node = self.lru.tail.prev
            if oldest_node is not self.lru.head:
                evicted_key, _ = oldest_node.data
                self._delete_key(evicted_key)
                self.evicted_keys += 1

    def _clean_expired(self):
        """
        만료 시간이 지난 키들을 힙에서 꺼내어 삭제
        """
        current_time = time.time()
        while self.ttl:
            expired_at, key = self.ttl.peek()
            if expired_at <= current_time:
                self.ttl.pop()
                self._delete_key(key)
            else:
                break

    def set(self, key, value, ttl_seconds=None):
        if self.data.contains(key):
            self._delete_key(key)

        new_node = Node((key, value))
        self.data.put(key, new_node)
        self.lru.insert_front(new_node)

        key_bytes = len(str(key).encode("utf-8"))
        val_bytes = len(str(value).encode("utf-8"))
        self.used_memory += (key_bytes + val_bytes)

        if ttl_seconds is not None:
            expire_at = time.time() + ttl_seconds
            self.ttl.push((expire_at, key))

        self._evict_if_needed()

    def get(self, key):
        self._clean_expired()
        node = self.data.get(key)
        if node:
            self.lru.move_to_front(node)
            _, value = node.data
            return value
        return None

    def delete(self, key):
        pass

    def exists(self, key):
        pass

    def dbsize(self):
        pass

    def keys(self):
        pass

    def expire(self, key, seconds):
        pass

    def ttl(self, key):
        pass

    def config_set(self, _):
        pass