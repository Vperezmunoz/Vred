"""Build the offline VRED Python API index used by vredapi.py.

Reads the Sphinx sources that ship with a VRED installation
(``<VRED>\\doc\\_sources``) and writes a compact index plus cleaned
per-owner documentation blocks into ``data/``.

Usage:
    py build_index.py                 # auto-detect newest VREDPro install
    py build_index.py <doc/_sources>  # explicit source directory
"""

import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

DEFAULT_ROOTS = [
    r"C:\Program Files\Autodesk",
    r"C:\Program Files\Autodesk GmbH",
]


def find_sources():
    candidates = []
    for root in DEFAULT_ROOTS:
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            src = os.path.join(root, name, "doc", "_sources")
            if os.path.isdir(src) and "VRED" in name.upper():
                candidates.append((name, src))
    if not candidates:
        return None, None
    candidates.sort(key=lambda pair: _version_key(pair[0]))
    return candidates[-1]


def _version_key(name):
    return [int(part) for part in re.findall(r"\d+", name)] or [0]


# --- reStructuredText cleanup -------------------------------------------------

ROLE = re.compile(r":[a-zA-Z:]+:`([^`]*)`")
LINE_BLOCK = re.compile(r"^\s*\|\s?")


def strip_role(match):
    text = match.group(1)
    # ":ref:`display text <target>`" -> "display text"
    if "<" in text and text.rstrip().endswith(">"):
        text = text[: text.index("<")]
    return text.strip().lstrip("/")


def clean(text):
    text = ROLE.sub(strip_role, text)
    text = text.replace("``", "`")
    return text


def clean_line(line):
    line = clean(line)
    line = LINE_BLOCK.sub("", line)
    if line.strip() in ("..", ".. raw:: html"):
        return None
    if line.strip().startswith(".. _"):
        return None
    if line.strip().startswith(".. index::"):
        return None
    if re.match(r"^\s*\.\. code-block::\s*\w*", line):
        return "```"
    if re.match(r"^\s*\.\. (note|warning|seealso|deprecated)::", line):
        return re.sub(r"^\s*\.\. (\w+)::", lambda m: m.group(1).upper() + ":", line)
    return line


# --- directive parsing --------------------------------------------------------

DIRECTIVE = re.compile(
    r"^(?P<indent>\s*)\.\.\s+(?:py:)?(?P<kind>class|method|function|staticmethod|"
    r"attribute|data|module)::\s*(?P<sig>.+?)\s*$"
)
SUMMARY_RETURN = re.compile(r"^\s*:rtype:\s*(.+?)\s*$")


def parse_file(path, module_hint=None):
    """Return (owners, members) parsed from one .rst.txt file."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()

    owners = []          # (name, kind, summary)
    members = []         # dict per member
    stack = []           # (indent, class name)
    current = None
    body = []

    def flush():
        if current is None:
            return
        current["summary"] = first_sentence(body) or return_text(body)
        current["rtype"] = find_rtype(body) or current.get("inline_rtype", "")
        members.append(current)

    for index, line in enumerate(lines):
        match = DIRECTIVE.match(line)
        if not match:
            if current is not None:
                body.append(line)
            continue

        flush()
        current, body = None, []

        indent = len(match.group("indent").expandtabs(4))
        kind = match.group("kind")
        sig = clean(match.group("sig")).strip()

        if kind in ("class", "module"):
            while stack and stack[-1][0] >= indent:
                stack.pop()
            name = sig.split("(")[0].strip()
            full = ".".join([entry[1] for entry in stack] + [name]) if stack else name
            stack.append((indent, name))
            window = lines[index + 1:index + 12]
            inherits = ""
            for candidate in window:
                match_base = re.search(r"\(Inherits\s+(.+?)\)", clean(candidate))
                if match_base:
                    inherits = match_base.group(1).strip()
                    break
            summary = first_sentence([l for l in window if "(Inherits" not in l])
            owners.append((full, kind, summary + ((" [inherits %s]" % inherits) if inherits else "")))
            continue

        name_part = sig.split("(")[0]
        if "." in name_part:
            # v2 members carry their own qualification: "vrNodeService.findNode(...)"
            owner = name_part.rsplit(".", 1)[0]
            name = sig[len(owner) + 1:]
        else:
            enclosing = [entry[1] for entry in stack if entry[0] < indent]
            if enclosing:
                owner = ".".join(enclosing)
            elif stack:
                owner = stack[-1][1]        # v1 style: class and members share indent 0
            else:
                owner = module_hint or ""
            name = sig
        # Some v1 entries carry the return type inside the directive:
        # "createMaterial(type) -> vrMaterialPtr".
        inline_rtype = ""
        arrow = re.split(r"\s*(?:->|→)\s*", name)
        if len(arrow) == 2:
            name, inline_rtype = arrow[0].strip(), arrow[1].strip()

        current = {
            "owner": owner,
            "kind": kind,
            "sig": name,
            "inline_rtype": inline_rtype,
            "line": index,
        }
        body = []

    flush()
    return owners, members


SECTIONS = {"Summary", "Functions", "Attributes", "Classes", "Enums", "Functions:"}


def first_sentence(lines):
    for line in lines:
        if line.strip() in SECTIONS:
            return ""
        text = clean(line).strip().lstrip("| ").strip()
        if not text or text.startswith("..") or text.startswith(":"):
            continue
        if set(text) <= set("-=~^"):
            continue
        return re.sub(r"\s+", " ", text)[:160]
    return ""


def return_text(lines):
    """Some entries have no prose at all, only a ``:return:`` line."""
    for line in lines:
        match = re.match(r"^\s*:return:\s*(.+?)\s*$", clean(line))
        if match:
            return "returns " + match.group(1)[:150]
    return ""


def find_rtype(lines):
    for line in lines:
        match = SUMMARY_RETURN.match(clean(line))
        if match:
            return match.group(1).strip()
    return ""


# --- output -------------------------------------------------------------------

def write_block(name, path, module_hint=None):
    with open(path, encoding="utf-8", errors="replace") as handle:
        raw = handle.read().splitlines()
    out = []
    for line in raw:
        cleaned = clean_line(line)
        if cleaned is None:
            continue
        out.append(cleaned.rstrip())
    while out and not out[0].strip():
        out.pop(0)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if module_hint:
        text = "MODULE %s (legacy v1 API)\n\n%s" % (module_hint, text)
    target = os.path.join(DATA, "blocks", name + ".txt")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(text)


HIGHLIGHT = re.compile(r'<div class="highlight"><pre>(.*?)</pre>', re.S)
LINENOS = re.compile(r'<span class="linenos">.*?</span>', re.S)
TAG = re.compile(r"<[^>]+>")
TITLE_TAG = re.compile(r"<h1>(.*?)<", re.S)


def extract_example_html(path, target):
    """Examples are rendered with ``literalinclude``; the code only exists in
    the built HTML, not in the .rst sources shipped alongside it."""
    import html as html_module

    with open(path, encoding="utf-8", errors="replace") as handle:
        page = handle.read()
    blocks = HIGHLIGHT.findall(page)
    if not blocks:
        return None
    chunks = []
    for block in blocks:
        block = LINENOS.sub("", block)
        chunks.append(html_module.unescape(TAG.sub("", block)).strip("\n"))
    code = "\n\n".join(chunks).strip()
    if not code:
        return None
    title_match = TITLE_TAG.search(page)
    title = html_module.unescape(TAG.sub("", title_match.group(1))).strip() if title_match else ""
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("# %s\n# source: %s\n\n%s\n" % (title or os.path.basename(target),
                                                     os.path.basename(path), code))
    return title


CODE_BLOCK = re.compile(r"^\s*\.\.\s+code-block::\s*python\s*$")


def extract_example(path, target):
    with open(path, encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()
    title = ""
    for index, line in enumerate(lines):
        if line.strip() and index + 1 < len(lines) and set(lines[index + 1].strip()) <= set("-=~") \
                and lines[index + 1].strip():
            title = line.strip()
            break

    chunks, collecting, indent = [], False, 0
    for line in lines:
        if CODE_BLOCK.match(line):
            collecting, indent = True, None
            chunks.append("")
            continue
        if not collecting:
            continue
        if not line.strip():
            chunks.append("")
            continue
        current = len(line) - len(line.lstrip())
        if indent is None:
            indent = current
        if current < indent:
            collecting = False
            continue
        chunks.append(line[indent:])

    code = "\n".join(chunks).strip()
    if not code:
        return None
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("# %s\n# source: %s\n\n%s\n" % (title or os.path.basename(target),
                                                     os.path.basename(path), code))
    return title


def main():
    if len(sys.argv) > 1:
        version, sources = "custom", sys.argv[1]
    else:
        version, sources = find_sources()
    if not sources or not os.path.isdir(sources):
        sys.exit("VRED doc/_sources not found. Pass the path explicitly.")

    print("source: %s" % sources)
    for sub in ("blocks", "examples"):
        path = os.path.join(DATA, sub)
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)

    classes, members = [], []
    block_of = {}   # owner name -> block file that documents it

    v2_files = sorted(f for f in os.listdir(sources) if f.startswith("class_"))
    for filename in v2_files:
        path = os.path.join(sources, filename)
        name = filename[len("class_"):-len(".rst.txt")]
        owners, found = parse_file(path)
        for owner_name, kind, summary in owners:
            classes.append((kind, owner_name, "v2", summary))
            block_of[owner_name] = name
        for member in found:
            block_of.setdefault(member["owner"], name)
        members.extend(found)
        write_block(name, path)

    v1_dir = os.path.join(sources, "v1documentation")
    if os.path.isdir(v1_dir):
        for filename in sorted(os.listdir(v1_dir)):
            if not filename.startswith("module_"):
                continue
            path = os.path.join(v1_dir, filename)
            name = filename[len("module_"):-len(".rst.txt")]
            owners, found = parse_file(path, module_hint=name)
            seen = {owner[0] for owner in owners}
            if name not in seen:
                classes.append(("module", name, "v1", first_sentence(open(
                    path, encoding="utf-8", errors="replace").read().splitlines()[3:20])))
            for owner_name, kind, summary in owners:
                classes.append((kind, owner_name, "v1", summary))
                block_of.setdefault(owner_name, name)
            for member in found:
                member["owner"] = member["owner"] or name
                member["api"] = "v1"
                block_of.setdefault(member["owner"], name)
            members.extend(found)
            write_block(name, path, module_hint=name)

    example_rows = []
    html_examples = os.path.join(os.path.dirname(sources), "examples")
    if os.path.isdir(html_examples):
        for folder, _dirs, files in os.walk(html_examples):
            group = os.path.relpath(folder, html_examples).replace("\\", "/")
            for filename in sorted(files):
                if not filename.endswith(".html"):
                    continue
                name = filename[:-len(".html")]
                if group not in (".", ""):
                    name = group.replace("/", "_") + "_" + name
                target = os.path.join(DATA, "examples", name + ".py")
                title = extract_example_html(os.path.join(folder, filename), target)
                if title is not None:
                    example_rows.append((name, title))

    examples_dir = os.path.join(sources, "examples")
    if os.path.isdir(examples_dir) and not example_rows:
        for filename in sorted(os.listdir(examples_dir)):
            if not filename.endswith(".rst.txt"):
                continue
            name = filename[:-len(".rst.txt")]
            target = os.path.join(DATA, "examples", name + ".py")
            title = extract_example(os.path.join(examples_dir, filename), target)
            if title is not None:
                example_rows.append((name, title))

    for extra in ("v2-overview", "scenegraphs", "webinterface",
                  "CommandLineParameters", "EnvironmentVariables_VRED"):
        path = os.path.join(sources, extra + ".rst.txt")
        if os.path.isfile(path):
            write_block(extra, path)

    enum_owners = {member["owner"] for member in members if member["kind"] == "data"}
    with open(os.path.join(DATA, "classes.tsv"), "w", encoding="utf-8") as handle:
        for kind, name, api, summary in sorted(set(classes), key=lambda row: row[1].lower()):
            if name in enum_owners:
                kind = "enum"
            elif name.endswith("Service"):
                kind = "service"
            handle.write("%s\t%s\t%s\t%s\n" % (name, kind, api, summary))

    with open(os.path.join(DATA, "members.tsv"), "w", encoding="utf-8") as handle:
        for member in members:
            handle.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (
                member["owner"], member["sig"], member["kind"],
                member.get("api", "v2"), member.get("rtype", ""),
                member.get("summary", "")))

    with open(os.path.join(DATA, "owners.tsv"), "w", encoding="utf-8") as handle:
        for owner in sorted(block_of, key=str.lower):
            handle.write("%s\t%s\n" % (owner, block_of[owner]))

    with open(os.path.join(DATA, "examples.tsv"), "w", encoding="utf-8") as handle:
        for name, title in example_rows:
            handle.write("%s\t%s\n" % (name, title))

    meta = {
        "vred": version,
        "sources": sources,
        "classes": len(set(classes)),
        "members": len(members),
        "examples": len(example_rows),
    }
    with open(os.path.join(DATA, "meta.json"), "w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
