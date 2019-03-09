#!/usr/bin/env python3

# Convert finer-data annotations to brat-flavored standoff.

import sys
import os

from collections import namedtuple
from argparse import ArgumentParser
from logging import warning

Token = namedtuple('Token', 'form tag1 tag2')
Textbound = namedtuple('Textbound', 'type start end text')


class FormatError(Exception):
    pass


def argparser():
    ap = ArgumentParser()
    ap.add_argument('-o', '--output', metavar='DIR', default=None,
                    help='Output directory (default STDOUT)')
    ap.add_argument('file', help='file in finer-data .csv')
    return ap


def read_finer_data(path):
    sentences = []
    current_sentence = []
    with open(path) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip()
            if l in ('<HEADLINE>', '<INGRESS>', '<BODY>'):
                continue    # skip untagged section markers
            if not l:
                if not current_sentence:
                    continue    # ignore extra empty lines
                sentences.append(current_sentence)
                current_sentence = []
            else:
                fields = l.split('\t')
                if len(fields) != 3:
                    raise FormatError('expected 3 TAB-separated fields, got {}'
                                      'on line {} in {}'.format(
                                          len(fields), ln, path))
                current_sentence.append(Token(*fields))
    if current_sentence:
        sentences.append(current_sentence)    # no trailing newline
    return sentences


def tags_to_textbounds(words, tags):
    sentence_text = ' '.join(words)
    textbounds = []
    offset = 0
    curr_type, curr_start = None, None
    for w, t in zip(words, tags):
        if t[0] in 'BO' and curr_type is not None:    # current ends
            end = offset - 1
            text = sentence_text[curr_start:end]
            textbounds.append(Textbound(curr_type, curr_start, end, text))
            curr_type, curr_start = None, None
        if t[0] == 'B':    # new starts
            curr_type, curr_start = t[2:], offset
        elif t[0] == 'I':
            if curr_type is None:
                warning('in sentence "{}"'.format(sentence_text))
                warning('tag {} without B tag for "{}"'.format(t, w))
                curr_type, curr_start = t[2:], offset    # start here
            if t[2:] != curr_type:
                print('in sentence {}'.format(sentence_text), file=sys.stderr)
                raise FormatError('{} continues as {}'.format(curr_type, t[2:]))
        elif t != 'O':
            raise FormatError('unexpected tag {}'.format(t))
        offset += len(w) + 1
    if curr_start is not None:
        end = offset - 1
        text = sentence_text[curr_start:end]
        textbounds.append(Textbound(curr_type, curr_start, end, text))
    return textbounds


def convert_to_textbounds(sentence):
    words = [t.form for t in sentence]
    text = ' '.join(words)
    t1 = [t.tag1 for t in sentence]
    t2 = [t.tag2 for t in sentence]
    return text, tags_to_textbounds(words, t1) + tags_to_textbounds(words, t2)


def write_sentence_standoff(index, txt, textbounds, args):
    annotations = []
    for i, tb in enumerate(textbounds, start=1):
        annotations.append('T{}\t{} {} {}\t{}'.format(
            i, tb.type, tb.start, tb.end, tb.text))
    ann = '\n'.join(annotations)

    if args.output is None:
        print(text)
        print(anntext)
    else:
        txt_out = os.path.join(args.output, 'sentence{0:05d}.txt'.format(index))
        ann_out = os.path.join(args.output, 'sentence{0:05d}.ann'.format(index))
        with open(txt_out, 'w') as out:
            out.write(txt)
        with open(ann_out, 'w') as out:
            out.write(ann)
            

def main(argv):
    args = argparser().parse_args(argv[1:])
    sentences = read_finer_data(args.file)
    for i, s in enumerate(sentences, start=1):
        text, textbounds = convert_to_textbounds(s)
        write_sentence_standoff(i, text, textbounds, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

