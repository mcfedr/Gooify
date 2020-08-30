from actions import *
import argparse
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description='Gooify.')
parser.add_argument('action', nargs='?', help='action to perform (albums|artists|playlists)')
parser.add_argument('--add', action='store_true')
args = parser.parse_args()

if args.add:
    print('adding to spotify!')

if args.action == 'albums':
    print("albums!")
    albums(args.add)
elif args.action == 'artists':
    print("artists!")
    artists(args.add)
elif args.action == 'playlists':
    print("playlists!")
    playlists(args.add)
else:
    print('You must specify an action')
