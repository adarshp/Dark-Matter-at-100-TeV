#!/usr/bin/env python

from BDTSignificanceCollector import BDTSignificanceCollector

def main():
    print("Collecting BDT significances")
    bdt_collector = BDTSignificanceCollector('bdt_significances.csv')
    bdt_collector.collect_significances()


if __name__ == '__main__':
    main()
