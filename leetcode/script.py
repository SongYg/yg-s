import sys


def gcd(a, b):
    for i in range(min(a, b), 0, -1):
        if a % i == 0 and b % i == 0:
            return i


def solution(n):
    sum_n = 0
    for x in range(2, n):
        num = n
        while num > 0:
            sum_n += num % x
            num = num // x
    return sum_n


if __name__ == "__main__":
    a = None
    b = None
    try:
        while True:
            line = input()
            if not line:
                break
            n = int(line)
            sum_n = solution(n)
            x = gcd(sum_n, n-2)
            print('{}/{}'.format(sum_n//x, (n-2)//x))
    except Exception as e:
        raise e
