import math
import os

def get_files():
    """ Return the list of CSV's in the current dir. """
    return [x for x in os.listdir('.') \
            if (not os.path.isdir(x)) and x.endswith('.csv')]

def get_values(name):
    """ Get all the parsed values from a given file. Returns an
    array of arrays of values (one array per each line). """

    result = []

    with open(name) as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        for line in lines:
            values = line.split(',')
            # Elliminate last (empty) result, cause each csv line ends with comma
            values = values[:-1]
            filtered_values = []
            for value in values:
                try:
                    next_value = float(value)
                    if not math.isnan(next_value):
                        filtered_values.append(next_value)
                except:
                    print "Found invalid value %s, skipping." % value
            result.append(filtered_values)
    return result

def mean(values):
    """ Given an array of values, return its mean. """
    if len(values) > 0:
        return sum(values) / len(values)
    else:
        return 0

def stddev(values):
    """ Given an array of values, return its standard deviation. """

    # Need abs() because python fools itself into believing
    # that the value under sqrt() is a very small negative value when
    # it loses precision.
    return math.sqrt(abs(mean([v * v for v in values]) -\
                         mean(values) * mean(values)))

def get_min_max(values, deviations = 2):
    """ Given an array of values, return min and max EXCLUDING outliers. """
    vmin = mean(values) - deviations * stddev(values)
    vmax = mean(values) + deviations * stddev(values)
    without_outliers = [v for v in values if v >= vmin and v <= vmax]
    outliers = [v for v in values if v < vmin or v > vmax]
    return (min(without_outliers), max(without_outliers), outliers)

if __name__ == '__main__':
    files = get_files()
    with open('result.txt', 'wt') as f:
        for file in files:
            raw_values = get_values(file)
            for idx, row in enumerate(raw_values):
                (row_min, row_max, outliers) = get_min_max(row)
                outliers_proc = 100.0 * len(outliers) / len(row)
                f.write('%s - %d -> min = %.2f, max = %.2f (outliers = %.2f%% - %r)\n' % 
                        (file, idx, row_min, row_max, outliers_proc, outliers))
