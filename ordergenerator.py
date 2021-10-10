from random import randint, choice, normalvariate
import sys


def generate_orders(num_iter, price_from, price_to):

    testfile = open(r'data\test-generated.csv', 'w')

    for orderid in range(num_iter):
        request = choice([0, 1])
        if orderid > 10 and request == 1:
            msg = ','.join(map(str, [request, randint(0, orderid - 1)]))
        else:
            # use int(100 * normalvariate(1, 0.2))
            msg = ','.join(map(str, [0, orderid, choice([0, 1]), randint(10, 100), randint(price_from, price_to)]))

        testfile.write(msg)
        testfile.write("\n")

    testfile.close()


if __name__ == '__main__':
    if len(sys.argv) == 4:
        num_iter, price_from, price_to = map(int, sys.argv[1:])
        generate_orders(num_iter, price_from, price_to)


