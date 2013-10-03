#!/usr/bin/env python

import gardenfreely

if __name__ == "__main__":
  import cProfile
  cProfile.run('gardenfreely.main()', 'gardenprof')
  import pstats
  p = pstats.Stats('gardenprof')
  p.sort_stats('cumulative').print_stats(10)