# 3개 자료구조를 통합하여 SET/GET/LRU/TTL 로직을 처리하는 핵심 클래스
from doubly_linked_list import DoublyLinkedList, Node
from hash_map import HashMap
from heap import MinHeap
import time

class MiniRedis:
    def __init__(self):
        self.data = HashMap()           # 실제 key-value 저장
        self.lru = DoublyLinkedList()   # LRU 순서 관리
        self.ttl_heap = MinHeap()            # 만료 시간 관리

        self.maxmemory = 0
        self.used_memory = 0
        self.evicted_keys = 0

    def _delete_key(self, key):
        node = self.data.get(key)
        if node:
            _, value = node.data
            self.data.remove(key)
            self.lru.remove_node(node)
            self.used_memory -= self._calculate_memory(key,value)
            return True
        return False

    def _calculate_memory(self, key, value):
        key_bytes = len(str(key).encode("utf-8"))
        val_bytes = len(str(value).encode("utf-8"))
        return key_bytes + val_bytes

    def _evict_if_needed(self):
        """
        maxmemory 초과 시 가장 오래 전에 사용된 데이터(tail 쪽) 삭제
        """
        if self.maxmemory <= 0:
            return

        while self.used_memory > self.maxmemory and len(self.lru) > 0:
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
        while self.ttl_heap.size() > 0:
            expired_at, key = self.ttl_heap.peek()
            if expired_at <= current_time:
                self.ttl_heap.pop()
                if self.data.contains(key):
                    self._delete_key(key)
            else:
                break

    def set(self, key, value, ttl_seconds=None):

        entry_memory = self._calculate_memory(key, value)
        if self.maxmemory > 0 and entry_memory > self.maxmemory:
            return "(error) OOM command not allowed when used_memory > maxmemory"

        if self.data.contains(key):
            self._delete_key(key)

        new_node = Node((key, value))
        self.data.put(key, new_node)
        self.lru.insert_front(new_node)
        self.used_memory += entry_memory

        if ttl_seconds is not None:
            expire_at = time.time() + float(ttl_seconds)
            self.ttl_heap.push((expire_at, key))

        self._evict_if_needed()
        return "OK"

    def get(self, key):
        self._clean_expired()
        node = self.data.get(key)
        if node:
            self.lru.move_to_front(node)
            _, value = node.data
            return value
        return None

    def delete(self, key):
        self._clean_expired()
        if key is None:
            return "(integer) 0"

        is_deleted = self._delete_key(key)
        if is_deleted:
            return "(integer) 1"
        else:
            return "(integer) 0"

    def exists(self, key):
        self._clean_expired()
        if self.data.contains(key):
            return "(integer) 1"
        return "(integer) 0"

    def dbsize(self):
        self._clean_expired()
        return self.data.size()

    def keys(self):
        self._clean_expired()
        return self.data.keys()

    def expire(self, key, seconds):
        self._clean_expired()
        if not self.data.contains(key):
            return "(integer) 0"

        try:
            sec = float(seconds)
            if sec <= 0:
                self._delete_key(key)
                return "(integer) 1"
            expire_at = time.time() + sec
            self.ttl_heap.push((expire_at, key))
            return "(integer) 1"
        except (ValueError, TypeError):
            return "(error) ERR value is not an integer or out of range"

    def ttl(self, key):
        self._clean_expired()
        if not self.data.contains(key):
            return "(integer) -2"

        expire_at = self.ttl_heap.find_expire_at(key)
        if expire_at is not None:
            remaining_sec = int(expire_at - time.time())
            return f"(integer) {max(0, remaining_sec)}"
        return "(integer) -1"

    def config_set(self, bytes):
        try:
            maxmemory = int(bytes)
            if maxmemory >= 0:
                self.maxmemory = maxmemory
                self._evict_if_needed()
                return "OK"
        except (ValueError, TypeError):
            pass
        return "(error) ERR value is not an integer or out of range"

    def info_memory(self):
        return (
            f"used_memory:{self.used_memory}\n"
            f"maxmemory:{self.maxmemory}\n"
            f"evicted_keys:{self.evicted_keys}"
        )