"""Build unaugmented canonical arrays from a completed full extraction campaign."""
from pathlib import Path
import sys
from .dataset import build_dataset


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(argv)
    try:
        manifest=build_dataset(campaign=args.campaign,output=args.output)
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(f'dataset rejected: {error}',file=sys.stderr)
        return 2
    print(f'completed {args.output}/data_manifest.json; '+str(manifest['eligibility']['partitions']))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
