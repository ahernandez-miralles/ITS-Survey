#!/usr/bin/env python
import csv
import sys

from collections import Counter
from itertools import imap, izip, starmap, tee

DEFAULT_FILENAME = 'inconsistencies.csv'

def pairwise(iterable):
  '''From https://docs.python.org/2/library/itertools.html.
  s -> (s0,s1), (s1,s2), (s2, s3), ...
  '''
  a, b = tee(iterable)
  next(b, None)
  return izip(a, b) 

def signum(x):
  '''Returns the sign of |x|.
  '''
  if x > 0:
    return 1
  if x < 0:
    return -1
  return 0

def find_inconsistencies(cat_csv_filename, num_csv_filename):
  '''Given a categorical ranking of items and a corresponding numerical
  ranking of items, this function determines the number of inconsistencies
  in the rankings. Each row of the csv file represents the rankings that
  a subject made, and each column represents the ranking given to a specific
  item. Note that the categorical rankings are represented by numbers, where
  a smaller number indicates a higher precedence. In contrast, a larger number
  in the numerical ranking indicates a higher precedence. The order of the
  subjects in both ranking files is assumed to be the same.

  |cat_csv_filename|: The filename of the categorical ranking.
  |num_csv_filename|: The filename of the numerical ranking.

  Returns a list of the number of inconsistencies for each subject. The order
  of this list reflects the order of the subjects in the ranking files.
  '''
  with open(cat_csv_filename) as cat_csv, open(num_csv_filename) as num_csv:
    cat_reader = csv.reader(cat_csv)
    num_reader = csv.reader(num_csv)

    # Scores this subjects rankings, i.e. returns total # of inconsistencies.
    def score_subject(cat_row, num_row):
      cat_rankings = map(int, cat_row)
      num_rankings = sorted(enumerate(map(int, num_row)),
                            lambda x, y: cmp(y[1], x[1]))

      # Scores a pair of rankings. Two ordered numerical rankings
      # should have the same importance order in the categorical ranking.
      def score(ranking_pair):
        r1 = ranking_pair[0]
        r2 = ranking_pair[1]

        # Return 0 if order is good, 1 otherwise.
        return max(0, signum(cmp(cat_rankings[r1[0]], cat_rankings[r2[0]])))

      return reduce(lambda x, y: x + score(y), pairwise(num_rankings), 0)

    try:
      return starmap(score_subject, zip(cat_reader, num_reader))
    except csv.Error as e:
      sys.exit('file %s, line %d: %s' %
               (cat_csv_filename, cat_reader.line_num, e))

def report_inconsistencies(cat_csv_filename,
                           num_csv_filename,
                           out_csv_filename=DEFAULT_FILENAME):
  '''Finds inconsistencies and outputs the results to a csv file.
  Also displays certain statistics to stdout.

  |cat_csv_filename|: The filename of the categorical ranking.
  |num_csv_filename|: The filename of the numerical ranking.
  |out_csv_filename|: The filename of the output file.
  '''
  inconsistencies = tuple(find_inconsistencies(cat_csv_filename,
                                               num_csv_filename))
  avg = sum(inconsistencies) / float(len(inconsistencies))
  mode = Counter(inconsistencies).most_common(1)[0][0]

  print('Average # of inconsistencies: %d' % avg)
  print('Most common # of inconsistencies: %d' % mode)

  with open(out_csv_filename, 'w') as out_csv:
    writer = csv.writer(out_csv)
    writer.writerows(imap(lambda x: (x,), inconsistencies))

if __name__ == '__main__':
  if len(sys.argv) > 2:
    ranking1 = sys.argv[1]
    ranking2 = sys.argv[2]
    
    if len(sys.argv) == 4:
      report_inconsistencies(ranking1, ranking2, out_csv_filename=sys.argv[3])
    else:
      report_inconsistencies(ranking1, ranking2)
  else:
    print('Usage: %s <ranking 1 csv file> <ranking 2 csv file> [output file]')
