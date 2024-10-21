import argparse
from process.io.in_dat import InDat

# EDIT -  better formatting on the help message
parser = argparse.ArgumentParser(
    prog='process_in.py',
    description='Process the input files for the plasma simulation',
)

parser.add_argument(
    '--maj_rad',
    type=float,
    help='Major radius of the plasma',
    required=True
)
parser.add_argument(
    '--triang',
    type=float,
    help='Triangularity of the plasma',
    required=True
)
parser.add_argument(
    '--elong',
    type=str,
    help='Elongation of the plasma',
    required=True
)

args = parser.parse_args()

in_dat = InDat(filename='DEFAULT_IN.DAT')

in_dat.add_parameter('rmajor', float(args.maj_rad))
in_dat.add_parameter('triang', float(args.triang))
in_dat.add_parameter('kappa', float(args.elong))


in_dat.write_in_dat(output_filename='RUN_IN.DAT')
