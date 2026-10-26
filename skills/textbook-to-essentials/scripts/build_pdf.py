"""Compile a UTF-8 LaTeX essentials document; requires an installed TeX engine."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys


def choose_engine(requested='auto', compiler=None):
    if compiler:
        if requested == 'auto':
            raise ValueError('--compiler requires an explicit --engine')
        executable = shutil.which(compiler)
        if not executable:
            raise ValueError(f'Compiler not found: {compiler}')
        return requested, executable
    candidates = ['latexmk', 'xelatex', 'tectonic'] if requested == 'auto' else [requested]
    for name in candidates:
        executable = shutil.which(name)
        if executable and (name != 'latexmk' or shutil.which('xelatex')):
            return name, executable
    raise ValueError('No usable compiler. Install XeLaTeX (and optionally latexmk), '
                     'or Tectonic; alternatively compile with XeLaTeX on Overleaf.')


def log_problems(log):
    checks = {
        'missing-glyph': r'Missing character:',
        'undefined-reference': r'(?:Reference|Citation) .+ undefined|There were undefined references',
        'horizontal-overflow': r'Overfull \\hbox',
        'vertical-overflow': r'Overfull \\vbox',
        'tex-error': r'^! |^.*:\d+: (?:LaTeX|Package .+) Error',
    }
    return [kind for kind, pattern in checks.items() if re.search(pattern, log, re.M)]


def build(source, requested='auto', compiler=None):
    source = Path(source).resolve()
    if not source.is_file() or source.suffix.lower() != '.tex':
        raise ValueError(f'Expected an existing .tex file: {source}')
    source.read_text(encoding='utf-8')
    engine, executable = choose_engine(requested, compiler)
    build_dir = source.parent / 'build' / source.stem
    build_dir.mkdir(parents=True, exist_ok=True)
    pdf = build_dir / (source.stem + '.pdf')
    log_path = build_dir / (source.stem + '.log')
    # Do not mistake an old PDF/log for success after a failed compilation.
    for old in (pdf, log_path):
        if old.exists():
            old.unlink()
    if engine == 'latexmk':
        commands = [[executable, '-xelatex', '-interaction=nonstopmode', '-halt-on-error',
                     '-file-line-error', '-outdir=' + str(build_dir), source.name]]
    elif engine == 'xelatex':
        commands = [[executable, '-interaction=nonstopmode', '-halt-on-error',
                     '-file-line-error', '-output-directory=' + str(build_dir), source.name]] * 2
    else:
        commands = [[executable, '--keep-logs', '--keep-intermediates',
                     '--outdir', str(build_dir), source.name]]
    output = ''
    for command in commands:
        result = subprocess.run(command, cwd=source.parent, capture_output=True,
                                encoding='utf-8', errors='replace', timeout=600)
        output = result.stdout + '\n' + result.stderr
        if result.returncode:
            raise RuntimeError('Compilation failed:\n' + output[-12000:])
    log = log_path.read_text(encoding='utf-8', errors='replace') if log_path.exists() else output
    if not pdf.is_file() or pdf.stat().st_size < 100 or not pdf.read_bytes().startswith(b'%PDF-'):
        raise RuntimeError('Compiler did not produce a valid PDF file.')
    problems = log_problems(log)
    if problems:
        raise RuntimeError('PDF needs repair before delivery: ' + ', '.join(problems)
                           + '\nLog: ' + str(log_path))
    destination = source.with_suffix('.pdf')
    shutil.copy2(pdf, destination)
    return destination, engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--engine', choices=['auto', 'latexmk', 'xelatex', 'tectonic'], default='auto')
    parser.add_argument('--compiler', help='Explicit compiler executable path')
    args = parser.parse_args()
    try:
        pdf, engine = build(args.source, args.engine, args.compiler)
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f'Built with {engine}: {pdf}')
    print('Log checks passed. Render and visually review every PDF page before delivery.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
