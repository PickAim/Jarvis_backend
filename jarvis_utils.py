import argparse


def create_parser(lst: list[(str, str)]):
    r = argparse.ArgumentParser()
    for tup in lst:
        r.add_argument(tup[0], tup[1])
    return r
