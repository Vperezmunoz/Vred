"""Offline lookup for the Autodesk VRED Python API.

Queries a prebuilt index of VRED's shipped Sphinx documentation so that only
the handful of lines that answer a question are printed.

    py vredapi.py find <regex> [--api v1|v2] [--kind method|data|attribute] [-n 40]
    py vredapi.py class <Owner> [regex]      # summary + every member
    py vredapi.py show <Owner.member>        # full entry: params, return, notes
    py vredapi.py classes [regex]            # list services / types / enums
    py vredapi.py enum <EnumOwner>           # enum values with their meaning
    py vredapi.py examples [regex]           # list shipped example scripts
    py vredapi.py example <name>             # print one example script
    py vredapi.py grep <regex>               # search example source code
    py vredapi.py doc <page>                 # v2-overview, scenegraphs, webinterface, ...
    py vredapi.py meta                       # which VRED build the index came from
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# The docs contain arrows and other non-cp1252 characters; a Windows console
# defaults to cp1252 and would raise on them.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def rows(filename):
    path = os.path.join(DATA, filename)
    if not os.path.isfile(path):
        sys.exit("index missing: %s - run 'py build_index.py' first" % path)
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line:
                yield line.split("\t")


def compile_pattern(text):
    try:
        return re.compile(text, re.IGNORECASE)
    except re.error as error:
        sys.exit("bad regex: %s" % error)


def truncate(text, width):
    text = text or ""
    return text if len(text) <= width else text[: width - 3] + "..."


def format_member(row, width=90):
    owner, sig, kind, api, rtype, summary = (row + [""] * 6)[:6]
    head = "%s.%s" % (owner, sig)
    if rtype:
        head += " -> " + rtype
    if api == "v1":
        head += "  [v1]"
    return head + ("\n    " + truncate(summary, width) if summary else "")


def cmd_find(args):
    pattern = compile_pattern(args.pattern)
    hits = 0
    for row in rows("members.tsv"):
        owner, sig, kind, api = row[0], row[1], row[2], row[3]
        if args.api and api != args.api:
            continue
        if args.kind and kind != args.kind:
            continue
        target = "%s.%s" % (owner, sig)
        if not pattern.search(target if not args.all_text else "\t".join(row)):
            continue
        print(format_member(row))
        hits += 1
        if hits >= args.limit:
            print("... limit %d reached; refine the pattern" % args.limit)
            return
    if not hits:
        print("no match")


def cmd_class(args):
    name = args.name
    pattern = compile_pattern(args.pattern) if args.pattern else None
    shown = False
    for row in rows("classes.tsv"):
        if row[0].lower() == name.lower():
            print("%s  (%s, %s)\n  %s\n" % (row[0], row[1], row[2], row[3]))
            name = row[0]
            shown = True
            break
    if not shown:
        near = [row[0] for row in rows("classes.tsv") if name.lower() in row[0].lower()]
        if near:
            print("no exact match. did you mean: %s" % ", ".join(near[:12]))
            return
    count = 0
    for row in rows("members.tsv"):
        if row[0] != name:
            continue
        if pattern and not pattern.search(row[1]):
            continue
        print(format_member(row))
        count += 1
    nested = [row[0] for row in rows("classes.tsv")
              if row[0].startswith(name + ".")]
    if nested:
        print("\nnested: %s" % ", ".join(nested))
    if not count and not nested:
        print("no members")


def block_path(owner):
    for row in rows("owners.tsv"):
        if row[0].lower() == owner.lower():
            return os.path.join(DATA, "blocks", row[1] + ".txt")
    return None


DIRECTIVE = re.compile(r"^(\s*)\.\.\s+(?:py:)?(class|method|function|staticmethod|"
                       r"attribute|data|module)::\s*(.+?)\s*$")


def cmd_show(args):
    query = args.target
    if "." not in query:
        return cmd_class(argparse.Namespace(name=query, pattern=None))

    # Split on the last dot first, then walk left for nested owners.
    candidates = []
    parts = query.split(".")
    for split in range(len(parts) - 1, 0, -1):
        candidates.append((".".join(parts[:split]), ".".join(parts[split:])))

    for owner, member in candidates:
        path = block_path(owner)
        if not path or not os.path.isfile(path):
            continue
        text = extract_entry(path, owner, member)
        if text:
            print("# %s.%s   (%s)" % (owner, member, os.path.basename(path)[:-4]))
            print(text)
            return
    print("not found. try: py vredapi.py find %s" % re.escape(query.split(".")[-1]))


def extract_entry(path, owner, member):
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    wanted = member.split("(")[0]
    out, capture, base_indent = [], False, 0
    for line in lines:
        if capture and line.strip() in ("Summary", "Functions:", "Attributes:") \
                and not line.startswith(" "):
            break
        if capture and line and not line.startswith(" ") and set(line.strip()) <= set("=-~") \
                and len(line.strip()) > 2:
            out.pop() if out else None
            break
        match = DIRECTIVE.match(line)
        if match:
            indent = len(match.group(1).expandtabs(4))
            sig = match.group(3)
            name = sig.split("(")[0].split(".")[-1]
            if capture:
                if indent <= base_indent:
                    break
                out.append(match.group(1) + sig)
                continue
            if name == wanted:
                capture, base_indent = True, indent
                out.append(sig)
            continue
        if capture:
            out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def cmd_classes(args):
    pattern = compile_pattern(args.pattern) if args.pattern else None
    for row in rows("classes.tsv"):
        name, kind, api, summary = (row + [""] * 4)[:4]
        if args.kind and kind != args.kind:
            continue
        if args.api and api != args.api:
            continue
        if pattern and not pattern.search(name + " " + summary):
            continue
        print("%-46s %-8s %-3s %s" % (name, kind, api, truncate(summary, 80)))


def cmd_enum(args):
    name = args.name
    values = [row for row in rows("members.tsv") if row[0].lower() == name.lower()
              and row[2] == "data"]
    if not values:
        # Accept the short form ("TextureSlotType") when it is unambiguous.
        owners = sorted({row[0] for row in rows("members.tsv")
                         if row[2] == "data" and row[0].lower().endswith("." + name.lower())})
        if len(owners) == 1:
            values = [row for row in rows("members.tsv") if row[0] == owners[0]]
        elif owners:
            print("ambiguous: %s" % ", ".join(owners[:12]))
            return
    if not values:
        matches = [row[0] for row in rows("classes.tsv")
                   if row[1] == "enum" and name.lower() in row[0].lower()]
        print("no enum values for %s.%s" % (name,
              (" candidates: " + ", ".join(matches[:12])) if matches else ""))
        return
    owner = values[0][0]
    print("%s:" % owner)
    for row in values:
        print("  %s.%s%s" % (owner, row[1], ("  - " + truncate(row[5], 80)) if len(row) > 5 and row[5] else ""))


def cmd_examples(args):
    pattern = compile_pattern(args.pattern) if args.pattern else None
    for row in rows("examples.tsv"):
        name, title = (row + [""] * 2)[:2]
        if pattern and not pattern.search(name + " " + title):
            continue
        print("%-40s %s" % (name, title))


def cmd_example(args):
    path = os.path.join(DATA, "examples", args.name + ".py")
    if not os.path.isfile(path):
        near = [row[0] for row in rows("examples.tsv") if args.name.lower() in row[0].lower()]
        sys.exit("no such example.%s" % ((" try: " + ", ".join(near[:10])) if near else ""))
    with open(path, encoding="utf-8") as handle:
        sys.stdout.write(handle.read())


def cmd_grep(args):
    pattern = compile_pattern(args.pattern)
    folder = os.path.join(DATA, "examples")
    hits = 0
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if pattern.search(line):
                    print("%s:%d: %s" % (filename[:-3], number, line.rstrip()))
                    hits += 1
                    if hits >= args.limit:
                        print("... limit %d reached" % args.limit)
                        return
    if not hits:
        print("no match")


def cmd_doc(args):
    path = os.path.join(DATA, "blocks", args.page + ".txt")
    if not os.path.isfile(path):
        available = sorted(name[:-4] for name in os.listdir(os.path.join(DATA, "blocks")))
        sys.exit("no such page. non-class pages: %s" % ", ".join(
            name for name in available if not name.startswith("vr")))
    with open(path, encoding="utf-8") as handle:
        sys.stdout.write(handle.read())


def cmd_meta(_args):
    with open(os.path.join(DATA, "meta.json"), encoding="utf-8") as handle:
        print(handle.read())


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("find", help="search member names")
    p.add_argument("pattern")
    p.add_argument("--api", choices=["v1", "v2"])
    p.add_argument("--kind", choices=["method", "function", "data", "attribute", "staticmethod"])
    p.add_argument("--all-text", action="store_true", help="also match summaries")
    p.add_argument("-n", "--limit", type=int, default=40)
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("class", help="list the members of a class or service")
    p.add_argument("name")
    p.add_argument("pattern", nargs="?")
    p.set_defaults(func=cmd_class)

    p = sub.add_parser("show", help="full documentation for one member")
    p.add_argument("target")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("classes", help="list classes")
    p.add_argument("pattern", nargs="?")
    p.add_argument("--kind", choices=["service", "class", "enum", "module"])
    p.add_argument("--api", choices=["v1", "v2"])
    p.set_defaults(func=cmd_classes)

    p = sub.add_parser("enum", help="values of an enum")
    p.add_argument("name")
    p.set_defaults(func=cmd_enum)

    p = sub.add_parser("examples", help="list shipped example scripts")
    p.add_argument("pattern", nargs="?")
    p.set_defaults(func=cmd_examples)

    p = sub.add_parser("example", help="print one example script")
    p.add_argument("name")
    p.set_defaults(func=cmd_example)

    p = sub.add_parser("grep", help="search inside example scripts")
    p.add_argument("pattern")
    p.add_argument("-n", "--limit", type=int, default=40)
    p.set_defaults(func=cmd_grep)

    p = sub.add_parser("doc", help="print a non-class documentation page")
    p.add_argument("page")
    p.set_defaults(func=cmd_doc)

    sub.add_parser("meta", help="index provenance").set_defaults(func=cmd_meta)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
