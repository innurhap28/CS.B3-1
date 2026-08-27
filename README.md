# Mini Redis

---

Python으로 구현한 **CLI 기반 Mini Redis**다.

Redis의 핵심 기능을 직접 구현하면서 **해시맵(HashMap), 이중 연결 리스트(Doubly Linked List), 최소 힙(Min Heap)**의 동작 원리를 학습하고, 이를 조합하여 **LRU 캐시와 TTL 만료 관리**를 구현했다.

## 프로젝트 소개

Redis는 메모리에 데이터를 저장하는 Key-Value 데이터 저장소로, 캐시·세션 저장소·메시지 브로커 등 다양한 용도로 사용된다.

이 프로젝트에서는 Redis의 일부 핵심 기능을 직접 구현하여 다음과 같은 동작을 확인하는 것을 목표로 했다.

* Key-Value 데이터 저장 및 조회
* LRU 기반 데이터 제거
* TTL 기반 데이터 만료
* 메모리 사용량 관리
* CLI 환경에서 Redis 스타일 명령어 실행
* 직접 구현한 자료구조를 조합한 데이터 관리

## 주요 기능

### String 명령어

| 명령어                           | 설명          |
| ----------------------------- | ----------- |
| `SET key value [ttl_seconds]` | 키에 값 저장     |
| `GET key`                     | 키의 값 조회     |
| `DEL key`                     | 키 삭제        |
| `EXISTS key`                  | 키 존재 여부 확인  |
| `DBSIZE`                      | 저장된 키 개수 확인 |
| `KEYS`                        | 전체 키 목록 확인  |

`SET`으로 기존 키를 덮어쓰는 경우 기존 TTL은 초기화한다.

`GET`은 키가 존재하고 만료되지 않은 경우에만 값을 반환하고 LRU 순서를 최근 사용 위치로 갱신한다.

### 메모리 관리

| 명령어                          | 설명                          |
| ---------------------------- | --------------------------- |
| `CONFIG SET maxmemory bytes` | 최대 메모리 사용량 설정               |
| `INFO memory`                | 현재 메모리 사용량 및 eviction 통계 확인 |

`maxmemory`를 초과하면 **LRU(Least Recently Used)** 정책에 따라 가장 오래 사용되지 않은 키부터 제거한다.

단일 Key-Value 엔트리 자체가 `maxmemory`보다 큰 경우 저장하지 않고 OOM 에러를 반환한다.

### TTL 관리

| 명령어                  | 설명             |
| -------------------- | -------------- |
| `EXPIRE key seconds` | 키의 만료 시간 설정    |
| `TTL key`            | 키의 남은 만료 시간 확인 |

TTL이 만료된 키는 명령어 실행 과정에서 만료 여부를 확인하여 삭제하고, 존재하지 않는 키와 동일하게 처리한다.

---

## 프로젝트 구조

```text
B3-1/
├── mini_redis.py
├── hash_map.py
├── doubly_linked_list.py
├── heap.py
├── CLI.py
├── main.py
└── README.md
```

각 자료구조를 독립적인 모듈로 분리하고, `MiniRedis`가 이를 조합하여 Redis의 핵심 기능을 처리하도록 구성했다.

```text
                 MiniRedis
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
     HashMap       LRU        Min Heap
        │           │           │
     데이터 저장   사용 순서    TTL 관리
```

### 자료구조의 역할

| 자료구조               | 역할                    |
| ------------------ | --------------------- |
| HashMap            | Key-Value 데이터 조회 및 저장 |
| Doubly Linked List | LRU 사용 순서 관리          |
| Min Heap           | TTL 만료 시간 관리          |

HashMap과 Doubly Linked List는 서로 다른 역할을 담당한다.

HashMap은 Key를 빠르게 찾기 위한 구조이고, Doubly Linked List는 데이터의 최근 사용 순서를 관리하기 위한 구조다.

`MiniRedis`에서는 HashMap에서 찾은 Node를 LRU 리스트에서도 직접 참조하여 두 자료구조를 연결한다.

따라서 데이터 Node의 소유권과 참조 관계를 일관되게 유지하는 것이 중요하다.

---

## 자료구조

### HashMap

Key-Value 데이터를 저장하기 위한 해시맵이다.

* 해시 함수 직접 구현
* 충돌 해결: **체이닝(Chaining)**
* `put`, `get`, `remove`, `contains`, `keys`, `size`
* 로드 팩터가 `0.75`를 초과하면 버킷을 2배 확장
* 리사이즈 과정에서 기존 Node를 재사용

#### 해시 함수

문자열 Key의 각 문자를 순회하면서 다음과 같은 방식으로 해시 값을 계산한다.

```text
hash = hash × 31 + ord(character)
```

계산된 값을 현재 bucket 개수로 나누어 bucket 위치를 결정한다.

```text
index = hash_value % capacity
```

여러 Key가 같은 bucket에 배치되는 충돌이 발생할 수 있기 때문에 **체이닝 방식**으로 충돌을 처리한다.

해시 함수의 베이스 값으로 31을 사용하여 문자열의 문자 순서를 반영하고, 최종적으로 `capacity`로 나누어 현재 버킷 범위 안의 인덱스를 얻도록 구현했다.

#### 체이닝

각 bucket에는 Doubly Linked List가 연결된다.

```text
buckets
│
├── bucket 0 → Node → Node
├── bucket 1 → Node
├── bucket 2 → Empty
├── bucket 3 → Node → Node
└── ...
```

충돌한 Key들은 같은 bucket의 연결 리스트에 저장한다.

#### HashMap 리사이즈와 Node 재사용

HashMap의 로드 팩터가 `0.75`를 초과하면 capacity를 2배로 늘리고 기존 데이터를 새로운 bucket 위치에 다시 배치한다.

이때 `(key, value)`를 이용해 새로운 Node를 생성하지 않고 **기존 Node 자체를 새로운 bucket에 재연결**한다.

```text
기존

Bucket 0
HEAD → Node A → Node B → TAIL


리사이즈


Bucket 2
HEAD → Node A → TAIL

Bucket 5
HEAD → Node B → TAIL
```

Node 자체를 재사용하기 때문에 리사이즈 과정에서 불필요한 Node 생성과 기존 Node의 복사를 줄일 수 있다.

새로운 Key를 `put`하는 경우에는 새로운 Node가 필요하지만, 리사이즈에서는 기존 Node를 그대로 이동시키는 방식으로 구현한다.

---

### Doubly Linked List

LRU 순서를 관리하기 위한 이중 연결 리스트다.

```text
HEAD
 ↓
[최근 사용] ⇄ [사용됨] ⇄ [오래됨]
                        ↓
                       TAIL
```

주요 연산:

* `insert_front`
* `insert_back`
* `remove_front`
* `remove_back`
* `remove_node`
* `move_to_front`

각 Node는 다음 세 가지 정보를 가진다.

```text
Node
├── data
├── prev
└── next
```

`prev`와 `next` 포인터를 이용하기 때문에 특정 Node를 알고 있다면 삽입·삭제·이동을 **O(1)**에 처리할 수 있다.

---

### Min Heap

TTL 만료 시간을 관리하기 위한 **최소 힙(Min Heap)**이다.

`(expire_at, key)` 형태의 데이터를 저장하여 가장 빨리 만료되는 키를 빠르게 확인할 수 있도록 구현했다.

주요 연산:

* `push`
* `pop`
* `peek`
* `size`
* `_heapify_up`
* `_heapify_down`

최소 힙에서는 가장 작은 `expire_at`을 가진 항목이 루트에 위치한다.

따라서 현재 시간보다 만료 시간이 작은 항목을 빠르게 확인할 수 있다.

---

## LRU 동작 방식

LRU는 가장 오래 사용되지 않은 데이터를 먼저 제거하는 정책이다.

데이터가 저장되거나 조회되면 해당 Key를 최근 사용 위치로 이동한다.

```text
SET user:1
SET user:2
GET user:1

최근                                  오래됨
 ↓                                      ↓
user:1  ⇄  user:2
```

`GET` 성공 시 HashMap에서 Node를 찾은 뒤 해당 Node를 LRU 리스트의 가장 앞으로 이동한다.

따라서 HashMap에서 데이터를 찾는 과정과 LRU 위치를 갱신하는 과정 모두 O(1)을 목표로 한다.

### LRU eviction

`maxmemory`를 초과하면 다음 과정을 수행한다.

```text
maxmemory 초과
       ↓
LRU에서 가장 오래된 Node 확인
       ↓
HashMap에서 데이터 삭제
       ↓
LRU에서 Node 삭제
       ↓
used_memory 감소
       ↓
evicted_keys 증가
       ↓
maxmemory 이하가 될 때까지 반복
```

eviction 과정에서 데이터가 실제로 삭제될 때 HashMap, LRU, 메모리 사용량이 함께 갱신되도록 구성했다.

삭제 실패와 같은 예외적인 상황에서는 데이터 구조 간 상태가 달라질 수 있으므로, eviction 과정에서는 삭제 대상이 실제로 존재하는지 확인하는 것이 중요하다.

---

## TTL 동작 방식

`EXPIRE` 명령으로 키에 만료 시간을 설정한다.

```text
EXPIRE user:1 10
        ↓
현재 시간 + 10초
        ↓
expire_at 계산
        ↓
Min Heap에 (expire_at, user:1) 저장
```

이후 명령 실행 과정에서 TTL 만료 여부를 확인한다.

```text
현재 시간 >= expire_at
        ↓
키 만료
        ↓
HashMap에서 삭제
        ↓
LRU에서 삭제
        ↓
used_memory 감소
```

### TTL Lazy Deletion

TTL이 변경될 때 기존 Heap 항목을 즉시 찾아 제거하지 않고 새로운 `(expire_at, key)` 항목을 추가할 수 있다.

이 경우 Heap에 동일한 Key에 대한 오래된 만료 정보와 새로운 만료 정보가 함께 존재할 수 있다.

따라서 만료 처리를 수행할 때 Heap에서 꺼낸 항목의 `expire_at`이 현재 Key에 실제로 적용된 만료 시간인지 확인하고, 이미 갱신된 오래된 항목이라면 실제 데이터를 삭제하지 않고 무시한다.

이 방식을 **Lazy Deletion**이라고 한다.

장점은 Heap 내부에서 기존 항목을 직접 찾아 삭제할 필요가 없다는 것이다. 반면 TTL을 반복적으로 갱신하면 오래된 Heap 항목이 남아 일시적으로 메모리를 더 사용할 수 있다.

### TTL과 LRU의 관계

TTL 만료로 삭제된 Key는 LRU 사용 순서를 갱신하지 않는다.

```text
만료 확인
   ↓
만료됨
   ↓
삭제
   ↓
(nil) 또는 -2 반환
```

반면 정상적인 `GET` 성공은 LRU를 최근 사용 위치로 이동한다.

---

## TTL 반환 규칙

| 상황                  |            반환값 |
| ------------------- | -------------: |
| 키가 존재하지 않음          | `(integer) -2` |
| 키가 존재하지만 TTL 없음     | `(integer) -1` |
| TTL 존재              |           남은 초 |
| `EXPIRE` 성공         |  `(integer) 1` |
| 존재하지 않는 키에 `EXPIRE` |  `(integer) 0` |

`EXPIRE`의 seconds가 0 이하인 경우에는 즉시 만료되는 것으로 처리할 수 있다.

---

## 메모리 관리

사용 메모리는 과제에서 지정한 다음 공식으로 계산한다.

```text
used_memory =
Σ (len(utf8(key)) + len(utf8(value)))
```

예를 들어:

```text
key   = "user:1"
value = "Alice"

memory =
len("user:1".encode("utf-8"))
+
len("Alice".encode("utf-8"))
```

자료구조의 Node, 포인터, bucket 등의 내부 오버헤드는 계산하지 않는다.

### maxmemory

`maxmemory`가 0이면 메모리 제한이 없는 것으로 처리한다.

`SET` 이후 `used_memory`가 `maxmemory`를 초과하면 LRU eviction을 수행하여 제한 이하가 될 때까지 가장 오래 사용되지 않은 Key부터 제거한다.

단일 Key-Value 엔트리 자체가 `maxmemory`보다 큰 경우에는 저장하지 않고 OOM 에러를 반환한다.

### INFO memory

`INFO memory`에서는 다음 정보를 확인할 수 있다.

```text
used_memory:<number>
maxmemory:<number>
evicted_keys:<number>
```

`evicted_keys`는 maxmemory 제한으로 인해 LRU 정책에 따라 제거된 Key의 누적 개수다.

---

## 메모리 모델과 비교 기준

이 프로젝트의 `used_memory`는 실제 Python 객체가 사용하는 전체 메모리를 측정하는 값이 아니라 **Key와 Value의 UTF-8 바이트 크기만 계산하는 논리적인 메모리 모델**이다.

따라서 다음 항목은 계산에서 제외한다.

```text
Node 객체
prev / next 포인터
HashMap bucket 배열
Doubly Linked List Sentinel Node
Min Heap 내부 구조
Python 객체 자체의 메모리 오버헤드
```

이 모델은 자료구조 구현에 따른 Python 객체의 메모리 차이가 결과에 영향을 주지 않도록 하기 위한 것이다.

만약 Node, 포인터, bucket 등의 내부 오버헤드까지 포함하는 방식으로 모델을 변경한다면 기존 `used_memory` 값과 직접 비교하기 어렵다.

따라서 모델 변경 시에는 모든 테스트 데이터에 동일한 메모리 산정 기준을 적용하고, 기존 결과와 새로운 결과를 별도로 비교해야 한다.

즉, **메모리 모델이 변경되면 eviction 발생 시점과 `evicted_keys` 결과도 달라질 수 있으므로 동일한 기준으로 결과를 보정하여 비교해야 한다.**

---

## LFU 전환 설계

현재 eviction 정책은 **LRU**다.

LRU는 최근에 사용된 데이터와 오래 사용되지 않은 데이터를 구분하기에 적합하지만, 사용 빈도가 높은 데이터인지 여부는 직접 반영하지 않는다.

향후 LFU(Least Frequently Used) 정책으로 전환한다면 각 Node에 사용 빈도를 나타내는 `frequency` 정보를 추가해야 한다.

```text
Node
├── key
├── value
└── frequency
```

`GET`이나 `SET`으로 Key가 사용될 때 `frequency`를 증가시킨다.

또한 단순히 하나의 LRU 리스트를 사용하는 대신 빈도별로 데이터를 관리할 수 있는 구조가 필요하다.

```text
frequency 1 → Node → Node
frequency 2 → Node
frequency 3 → Node → Node
```

eviction 시에는 가장 낮은 frequency를 가진 그룹에서 제거 대상을 선택해야 한다.

동일한 frequency를 가진 Key가 여러 개라면 추가적인 정책이 필요하다. 예를 들어 같은 빈도 안에서는 LRU 순서를 적용하여 오래 사용되지 않은 Key를 제거할 수 있다.

따라서 LRU에서 LFU로 전환할 경우 다음과 같은 변경이 필요하다.

1. Node에 `frequency` 추가
2. Key 사용 시 frequency 증가
3. frequency별 데이터 관리 구조 추가
4. eviction 정책을 최소 frequency 기준으로 변경
5. 동일 frequency에 대한 tie-break 정책 결정
6. 기존 LRU와 LFU의 성능 및 eviction 결과 비교

현재 프로젝트에서는 요구사항에 따라 LRU를 사용하고 있으며 LFU는 설계 확장 대상으로 정의한다.

---

## 대규모 데이터에서의 병목

현재 구현은 학습 목적으로 단일 프로세스와 CLI 환경을 기준으로 한다.

약 10만 개 이상의 Key를 저장하는 대규모 상황에서는 다음과 같은 병목을 예상할 수 있다.

### 1. HashMap 리사이즈

로드 팩터가 0.75를 초과하면 전체 데이터를 새로운 bucket에 다시 배치해야 한다.

```text
capacity 증가
      ↓
전체 bucket 순회
      ↓
모든 Node 재해싱
      ↓
새 bucket으로 이동
```

따라서 리사이즈가 발생하는 순간 전체 데이터에 대한 작업이 필요하다.

Node 재사용 방식을 사용하면 불필요한 Node 객체 생성을 줄일 수 있지만, 모든 Node를 다시 순회하는 비용 자체는 남아 있다.

### 2. TTL Heap 증가

TTL을 자주 갱신하면 Lazy Deletion으로 인해 이미 유효하지 않은 Heap 항목이 누적될 수 있다.

```text
EXPIRE key 10
EXPIRE key 20
EXPIRE key 30
```

위와 같이 TTL이 반복적으로 변경되면 하나의 Key에 대해 여러 Heap 항목이 존재할 수 있다.

따라서 매우 많은 TTL 갱신이 발생하는 환경에서는 Heap 크기가 커지는 문제가 발생할 수 있다.

### 3. KEYS 명령어

현재 `KEYS`는 전체 bucket을 순회하여 모든 Key를 확인한다.

따라서 저장된 Key의 수가 많아질수록 실행 시간이 증가한다.

```text
KEYS
 ↓
모든 bucket 순회
 ↓
모든 Node 확인
 ↓
Key 목록 생성
```

대규모 환경에서는 전체 데이터를 순회하는 작업이 병목이 될 수 있다.

### 4. CLI / I/O

현재 프로젝트는 네트워크 서버가 아닌 CLI 기반 REPL이므로 입력과 출력이 한 번에 처리된다.

대규모 요청을 처리하는 실제 Redis와 달리 네트워크 처리, 비동기 I/O, 여러 클라이언트의 동시 요청 처리는 구현하지 않았다.

향후 확장한다면 다음과 같은 방법을 고려할 수 있다.

* HashMap 데이터를 여러 shard로 분리
* 요청을 여러 worker에서 처리
* 네트워크 I/O를 비동기 방식으로 처리
* 전체 Key를 순회하는 명령의 사용 제한
* TTL 정리 작업을 요청 처리와 분리

현재 과제에서는 멀티스레딩, 락, 네트워크 통신을 요구하지 않기 때문에 이러한 기능은 구현하지 않고 설계 관점에서만 고려한다.

---

## CLI 사용 예시

```text
mini-redis> CONFIG SET maxmemory 30
OK

mini-redis> SET user:1 "Alice"
OK

mini-redis> SET user:2 "Bob"
OK

mini-redis> GET user:1
"Alice"

mini-redis> EXISTS user:1
(integer) 1

mini-redis> DBSIZE
(integer) 2

mini-redis> EXPIRE user:1 10
(integer) 1

mini-redis> TTL user:1
(integer) 9

mini-redis> INFO memory
used_memory:18
maxmemory:30
evicted_keys:0

mini-redis> DEL user:1
(integer) 1
```

### LRU eviction 예시

```text
mini-redis> CONFIG SET maxmemory 20
OK

mini-redis> SET user:1 Alice
OK

mini-redis> SET user:2 Bob
OK

mini-redis> GET user:1
"Alice"

mini-redis> SET user:3 Charlie
OK
```

메모리 제한을 초과하면 LRU 기준으로 가장 오래 사용되지 않은 Key부터 제거한다.

---

## 에러 처리

Redis 스타일의 에러 메시지를 사용한다.

```text
mini-redis> GET
(error) ERR wrong number of arguments for 'GET' command

mini-redis> CONFIG SET maxmemory abc
(error) ERR value is not an integer or out of range

mini-redis> HELLO
(error) ERR unknown command 'HELLO'
```

주요 에러 유형:

| 상황       | 출력                                                               |
| -------- | ---------------------------------------------------------------- |
| 잘못된 명령어  | `(error) ERR unknown command '<cmd>'`                            |
| 인자 개수 오류 | `(error) ERR wrong number of arguments for '<cmd>' command`      |
| 정수 파싱 실패 | `(error) ERR value is not an integer or out of range`            |
| 메모리 초과   | `(error) OOM command not allowed when used_memory > 'maxmemory'` |

CLI에서는 `exit` 또는 `quit`을 입력하면 프로그램을 종료한다.

---

## 시간 복잡도

| 연산                  | 평균 시간 복잡도 |
| ------------------- | --------: |
| HashMap `get`       |      O(1) |
| HashMap `put`       |      O(1) |
| HashMap `remove`    |      O(1) |
| LRU `move_to_front` |      O(1) |
| LRU `remove_node`   |      O(1) |
| Heap `push`         |  O(log n) |
| Heap `pop`          |  O(log n) |
| Heap `peek`         |      O(1) |
| HashMap resize      |      O(n) |
| `KEYS`              |      O(n) |

HashMap의 경우 평균적인 해시 분포를 가정한다.

리사이즈는 모든 기존 Node를 새로운 bucket 위치로 이동해야 하므로 O(n)의 비용이 발생한다.

---

## 기술 스택

* **Language:** Python
* **Interface:** CLI / REPL
* **Data Structures:** HashMap, Doubly Linked List, Min Heap
* **Cache Policy:** LRU
* **Expiration:** TTL
* **Collision Resolution:** Chaining

---

## 실행 방법

프로젝트 디렉터리에서 CLI를 실행한다.

```bash
python CLI.py
```

실행 후 다음과 같이 명령어를 입력할 수 있다.

```text
mini-redis> SET name Alice
OK

mini-redis> GET name
"Alice"

mini-redis> quit
```
