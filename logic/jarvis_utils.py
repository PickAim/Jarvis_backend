import argparse


def create_parser(lst: list[(str, str)]):
    r = argparse.ArgumentParser()
    for tup in lst:
        r.add_argument(tup[0], tup[1])
    return r


def load_data(filename: str) -> list[float]:
    result = []
    with (open(filename, "r")) as file:
        lines = file.readlines()
        for line in lines:
            for cost in line.split(","):
                if cost != "" and cost != "\n":
                    result.append(float(cost))
    return result
