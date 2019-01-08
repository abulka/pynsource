# permutations


def getpermutations(lzt):
    result = []
    for i in range(0, len(lzt)):
        for j in range(i + 1, len(lzt)):
            result.append((lzt[i], lzt[j]))
    return result


if __name__ == "__main__":
    print(getpermutations(["a"]))
    print(getpermutations(["a", "b"]))
    print(getpermutations(["a", "b", "c", "d"]))
    print(getpermutations(["a", "b", "c", "d", "e"]))
