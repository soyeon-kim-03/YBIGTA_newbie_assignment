from lib import SegmentTree
import sys


"""
TODO:
- 일단 SegmentTree부터 구현하기
- main 구현하기
"""
MAX_TASTE = 1_000_000

def main() -> None:
    # 구현하세요!
    input_data = sys.stdin.readline
    n = int(input_data())

    tree: SegmentTree[int, int] = SegmentTree(
        MAX_TASTE,
        default=lambda: 0,
        f_conv=lambda x: x,
        f_merge=lambda a, b: a + b,
    )

    results = []
    for _ in range(n):
        query = list(map(int, input_data().split()))
        if query[0] == 1:
            b = query[1]
            taste = tree.find_kth(b)
            results.append(taste)
            tree.add(taste, -1)
        else:
            _, b, c = query
            tree.add(b, c)

    sys.stdout.write("\n".join(map(str, results)) + "\n")


if __name__ == "__main__":
    main()