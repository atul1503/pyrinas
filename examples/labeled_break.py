def main():
    "outer"
    for i in range(10):
        "inner"
        for j in range(10):
            if i * j > 30:
                "outer"
                break
            print(i * j)