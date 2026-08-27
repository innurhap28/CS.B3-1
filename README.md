# Mini Redis
---

Python으로 구현한 **CLI 기반 Mini Redis**입니다.

Redis의 핵심 기능을 직접 구현하면서 **해시맵(HashMap), 이중 연결 리스트(Doubly Linked List), 최소 힙(Min Heap)**의 동작 원리를 학습하고, 이를 조합하여 **LRU 캐시와 TTL 만료 관리**를 구현했습니다.

## 프로젝트 소개

Redis는 메모리에 데이터를 저장하는 Key-Value 데이터 저장소로, 캐시·세션 저장소·메시지 브로커 등 다양한 용도로 사용됩니다.

이 프로젝트에서는 Redis의 일부 핵심 기능을 직접 구현하여 다음과 같은 동작을 확인하는 것을 목표로 했습니다.

* Key-Value 데이터 저장 및 조회
* LRU 기반 데이터 제거
* TTL 기반 데이터 만료
* 메모리 사용량 관리
* CLI 환경에서 Redis 스타일 명령어 실행

## 주요 기능

### String 명령어

| 명령어             | 설명          |
| --------------- | ----------- |
| `SET key value [ttl_seconds]` | 키에 값 저장     |
| `GET key`       | 키의 값 조회     |
| `DEL key`       | 키 삭제        |
| `EXISTS key`    | 키 존재 여부 확인  |
| `DBSIZE`        | 저장된 키 개수 확인 |
| `KEYS`          | 전체 키 목록 확인  |

### 메모리 관리

| 명령어                          | 설명                 |
| ---------------------------- | ------------------ |
| `CONFIG SET maxmemory bytes` | 최대 메모리 사용량 설정      |
| `INFO memory`                | 메모리 사용량 및 제거된 키 확인 |

`maxmemory`를 초과하면 **LRU(Least Recently Used)** 정책에 따라 가장 오래 사용되지 않은 키부터 제거합니다.

### TTL 관리

| 명령어                  | 설명          |
| -------------------- | ----------- |
| `EXPIRE key seconds` | 키의 만료 시간 설정 |
| `TTL key`            | 남은 만료 시간 확인 |

TTL이 만료된 키는 명령어 실행 전에 확인하여 삭제하고, 존재하지 않는 키와 동일하게 처리합니다.

## 자료구조

### HashMap

Key-Value 데이터를 저장하기 위한 해시맵.

* 해시 함수 직접 구현
* 충돌 해결: **체이닝(Chaining)**
* `put`, `get`, `remove`, `contains`, `keys`, `size`
* 로드 팩터가 `0.75`를 초과하면 버킷을 2배 확장

### Doubly Linked List

LRU 순서를 관리하기 위한 이중 연결 리스트.

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

각 노드의 `prev`, `next`를 이용하여 삽입·삭제·이동을 **O(1)**에 처리합니다.

### Min Heap

TTL 만료 시간을 관리하기 위한 최소 힙입.

`(expire_at, key)` 형태로 데이터를 저장하여 가장 빨리 만료되는 키를 빠르게 확인할 수 있도록 구현했습니다.

주요 연산:

* `push`
* `pop`
* `peek`
* `size`
* `_heapify_up`
* `_heapify_down`

## LRU 동작 방식

LRU는 가장 오래 사용되지 않은 데이터를 먼저 제거하는 정책.

데이터가 저장되거나 조회되면 해당 키를 최근 사용 위치로 이동합니다.

```text
SET user:1
SET user:2
GET user:1

최근                                  오래됨
 ↓                                      ↓
user:1  ⇄  user:2
```

이후 `maxmemory`를 초과하면 가장 오래된 위치의 키부터 제거합니다.

```text
maxmemory 초과
       ↓
LRU에서 가장 오래된 키 확인
       ↓
HashMap에서 데이터 삭제
       ↓
LRU에서 노드 삭제
       ↓
used_memory 감소
       ↓
maxmemory 이하가 될 때까지 반복
```

단, 하나의 키와 값 자체가 `maxmemory`보다 큰 경우에는 저장하지 않고 OOM 에러를 반환합니다.

## TTL 동작 방식

`EXPIRE` 명령으로 키에 만료 시간을 설정합니다.

```text
EXPIRE user:1 10
        ↓
expire_at 계산
        ↓
Min Heap에 (expire_at, user:1) 저장
```

키를 조회하거나 TTL을 확인할 때 만료 여부를 확인합니다.

```text
현재 시간 >= expire_at
        ↓
키 만료
        ↓
데이터 삭제
        ↓
LRU / TTL 관련 정보도 정리
```

### TTL 반환 규칙

| 상황                  |            반환값 |
| ------------------- | -------------: |
| 키가 존재하지 않음          | `(integer) -2` |
| 키가 존재하지만 TTL 없음     | `(integer) -1` |
| TTL 존재              |           남은 초 |
| `EXPIRE` 성공         |  `(integer) 1` |
| 존재하지 않는 키에 `EXPIRE` |  `(integer) 0` |

## 메모리 관리

사용 메모리는 다음 공식으로 계산합니다.

```text
used_memory =
Σ (len(utf8(key)) + len(utf8(value)))
```

자료구조의 노드, 포인터, 버킷 등의 내부 오버헤드는 계산하지 않습니다.

예를 들어:

```text
key   = "user:1"
value = "Alice"

memory =
len("user:1".encode("utf-8"))
+
len("Alice".encode("utf-8"))
```

`SET` 이후 메모리 제한을 초과하면 LRU 정책에 따라 데이터를 제거합니다.

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

## 에러 처리

Redis 스타일의 에러 메시지를 사용합니다.

```text
mini-redis> GET
(error) ERR wrong number of arguments for 'GET' command

mini-redis> CONFIG SET maxmemory abc
(error) ERR value is not an integer or out of range

mini-redis> HELLO
(error) ERR unknown command 'HELLO'
```

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

각 자료구조를 독립적인 모듈로 분리하고, `MiniRedis`가 이를 조합하여 Redis의 핵심 기능을 처리하도록 구성했습니다.


## 기술 스택

* **Language:** Python
* **Interface:** CLI / REPL
* **Data Structures:** HashMap, Doubly Linked List, Min Heap
* **Cache Policy:** LRU
* **Expiration:** TTL


## 실행 방법

프로젝트 디렉터리에서 CLI를 실행합니다.

```bash
python cli.py
```

실행 후 다음과 같이 명령어를 입력할 수 있습니다.

```text
mini-redis> SET name Alice
OK

mini-redis> GET name
"Alice"

mini-redis> quit
```
