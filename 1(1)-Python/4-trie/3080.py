from lib import Trie
import sys


"""
TODO:
- 일단 lib.py의 Trie Class부터 구현하기
- main 구현하기

힌트: 한 글자짜리 자료에도 그냥 str을 쓰기에는 메모리가 아깝다...
"""
MOD = 1000000007
MAX_N = 3001

def main() -> None:
    # 구현하세요!
    input_data = sys.stdin.readline
    n = int(input_data())
    names = [input_data().strip() for _ in range(n)]

    trie: Trie[str] = Trie()
    for name in names:
        trie.push(name)

    fact = [1] * (MAX_N + 1)
    for i in range(1, MAX_N + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * (MAX_N + 1)
    inv_fact[MAX_N] = pow(fact[MAX_N], MOD - 2, MOD)
    for i in range(MAX_N, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD

    size = [0] * len(trie)
    ways = [1] * len(trie)

    for idx in range(len(trie) - 1, -1, -1):
        node = trie[idx]
        total = 1 if node.is_end else 0
        numerator = 1
        denom_inv = 1
        for child_idx in node.children:
            total += size[child_idx]
            numerator = numerator * ways[child_idx] % MOD
            denom_inv = denom_inv * inv_fact[size[child_idx]] % MOD
        size[idx] = total
        ways[idx] = fact[total] * denom_inv % MOD * numerator % MOD

    print(ways[0])


if __name__ == "__main__":
    main()