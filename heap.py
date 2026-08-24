# 최소 힙 (TTL 관리)

class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        result = self.heap[0]
        last_item = self.heap.pop()
        if self.heap:
            self.heap[0] = last_item
            self._heapify_down(0)
        return result

    def peek(self):
        if not self.heap:
            return None
        return self.heap[0]

    def size(self):
        return len(self.heap)

    def _heapify_up(self, index):
        while index > 0:
            parent_index = (index - 1) // 2
            if self.heap[index] < self.heap[parent_index]:
                self.heap[index], self.heap[parent_index] = (
                    self.heap[parent_index],
                    self.heap[index]
                )
                index = parent_index
            else:
                break

    def _heapify_down(self, index):
        length = len(self.heap)
        while True:
            left_child = index * 2 + 1
            right_child = index * 2 + 2
            smallest = index    # 현재 노드가 가장 작다고 가정
            if left_child < length and self.heap[left_child] < self.heap[smallest]: 
                # 왼쪽 자식이 존재하고, 현재 노드보다 작다면 smallest를 왼쪽 자식으로 변경
                smallest = left_child
            if right_child < length and self.heap[right_child] < self.heap[smallest]:
                smallest = right_child
            if smallest == index:
                break
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            index = smallest
