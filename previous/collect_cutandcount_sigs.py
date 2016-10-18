#!/usr/bin/env python

from SignificanceCollector import SignificanceCollector

def main():
    print("Collecting cut-and-count significances")
    cut_and_count_collector = SignificanceCollector('cut_and_count_significances.csv')
    cut_and_count_collector.collect_significances()

if __name__ == '__main__':
    main()
