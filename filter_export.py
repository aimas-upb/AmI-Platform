from optparse import OptionParser
import os

def expand_filter_list(filter_list):
    """ Expands a filter list to a list of sorted unique values. """

    if len(filter_list) == 0:
        return []

    result = []

    filters = filter_list.split(',')
    for filter in filters:
        if '-' in filter:
            (start, _, stop) = filter.partition('-')
            start = int(start)
            stop = int(stop)
            result.extend(range(start, stop + 1))
        else:
            result.append(int(filter))

    # Filter lists are 1-based, while Python is 0-based, so
    # we need to subtract 1 from every filter
    result = [x - 1 for x in result]

    # Make sure we have unique values in the result and sort them
    return sorted(list(set(result)))

def parse_command_line_options():
    """ Parses the command line options and returns a dictionary. """
    parser = OptionParser()
    parser.add_option("-f", "--filters", dest="filters",
                      help="File containing filters for each CSV file (which rows to keep)")
    parser.add_option("-i", "--input", dest="input",
                      help="Input directory containing the CSV files to be filtered")
    parser.add_option("-o", "--output", dest="output",
                      help="Output directory containing the filtered CSV files")

    (options, args) = parser.parse_args()

    return options

def check_valid(options):
    if not hasattr(options, 'filters') or getattr(options, 'filters') is None:
        return False
    if not hasattr(options, 'input') or getattr(options, 'input') is None:
        return False
    if not hasattr(options, 'output') or getattr(options, 'output') is None:
        return False
    return True

def apply_filters(input_file, output_file, filters):
    """ Given an input file, apply the filters and write the results to the output file. """
    rows = expand_filter_list(filters)
    try:
        with open(input_file, 'rt') as input:

            # Perform row filtering of input file
            input_lines = input.readlines()
            output_lines = []
            for row in rows:
                output_lines.append(input_lines[row])

            # Write the output lines
            with open(output_file, 'wt') as output:
                for line in output_lines:
                    output.write(line)
            
            print("Successfully processed %s -> %s with filters %s" %
                  (input_file, output_file, filters))
            return True
    except:
        print("Error while processing %s -> %s with filters %s!" %
              (input_file, output_file, filters))
        import traceback
        traceback.print_exc()
        return False

def main():
    options = parse_command_line_options()
    if not check_valid(options):
        print "You didn't provide all arguments"
        return

    # Make sure that input & output dir have no trailing slash
    input_path = options.input
    if input_path.endswith('/'):
        input_path = input_path[:-1]
    output_path = options.output
    if output_path.endswith('/'):
        output_path = output_path[:-1]

    if not os.path.exists(output_path):
        print "Output directory %s doesn't exist. Creating it!" % output_path
        os.mkdir(output_path)

    with open(options.filters, 'rt') as filters_file:
        filters = filters_file.readlines()
        for filter in filters:
            if len(filter.strip()) == 0:
                continue

            (file_name, _, row_list) = filter.partition(':')
            file_name = file_name.strip()
            file_name = "export-%s.csv" % file_name.strip('"')
            row_list = row_list.strip()
            input_file = '%s/%s' % (input_path, file_name)
            output_file = '%s/%s' % (output_path, file_name)
            apply_filters(input_file, output_file, row_list)

if __name__ == '__main__':
    main()
