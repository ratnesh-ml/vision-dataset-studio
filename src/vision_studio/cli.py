import argparse
import json

from .core import audit_folder, make_sample_images, write_html, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(prog='vision-studio')
    sub = parser.add_subparsers(dest='command', required=True)
    sample = sub.add_parser('make-sample')
    sample.add_argument('folder')
    sample.add_argument('--count', type=int, default=12)
    audit = sub.add_parser('audit')
    audit.add_argument('folder')
    audit.add_argument('--output', default='reports/audit.json')
    audit.add_argument('--html', default='reports/audit.html')
    args = parser.parse_args(argv)

    if args.command == 'make-sample':
        make_sample_images(args.folder, args.count)
        print(f'created sample images in {args.folder}')
        return 0
    result = audit_folder(args.folder)
    write_json(result, args.output)
    write_html(result, args.html)
    summary = {'images': result['images'], 'flagged': result['flagged'], 'clean': result['clean'], 'output': args.output, 'html': args.html}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
