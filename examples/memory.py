def main():
    p: 'ptr[int]' = malloc(sizeof('int'))
    assign(p, 255)
    print(deref(p))
    free(p)