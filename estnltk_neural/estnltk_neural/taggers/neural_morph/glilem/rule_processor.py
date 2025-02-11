# Originally adapted from the source code of UDPipe 2
# https://github.com/ufal/udpipe/blob/82a9bd82ae7e947897304177e0390b3f191b01cb/udpipe2_dataset.py
# Original source license heading:
#
# Copyright 2020 Institute of Formal and Applied Linguistics, Faculty of
# Mathematics and Physics, Charles University in Prague, Czech Republic.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Current version is from
# https://huggingface.co/spaces/adorkin/GliLem/blob/15ce1742d8f6bdb4fcce533d5b0fd904bf831c89/rule_processor.py


from typing import List, Tuple, Union


class RuleProcessor:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    @staticmethod
    def gen_lemma_rule(form: str, lemma: str, allow_copy: bool) -> str:
        form = form.lower()

        # change back to original maybe
        previous_case = -1
        lemma_casing = ""
        for i, c in enumerate(lemma):
            # prevent non-alphabetic characters from breaking spans in casing rules
            if not c.islower() and not c.isupper():  # wrong condition?
                if previous_case == -1:
                    case = "↓"
                else:
                    case = previous_case
            else:
                case = "↑" if c.lower() != c else "↓"
            if case != previous_case:
                lemma_casing += "{}{}{}".format(
                    "¦" if lemma_casing else "",
                    case,
                    i if i <= len(lemma) // 2 else i - len(lemma),
                )
            previous_case = case
        lemma = lemma.lower()

        best, best_form, best_lemma = 0, 0, 0
        for l in range(len(lemma)):
            for f in range(len(form)):
                cpl = 0
                while (
                    f + cpl < len(form)
                    and l + cpl < len(lemma)
                    and form[f + cpl] == lemma[l + cpl]
                ):
                    cpl += 1
                if cpl > best:
                    best = cpl
                    best_form = f
                    best_lemma = l

        rule = lemma_casing + ";"
        if not best:
            rule += "a" + lemma
        else:
            rule += "d{}¦{}".format(
                min_edit_script(form[:best_form], lemma[:best_lemma], allow_copy),
                min_edit_script(
                    form[best_form + best :], lemma[best_lemma + best :], allow_copy
                ),
            )
        return rule

    def apply_lemma_rule(self, form: str, lemma_rule: str) -> str:
        if ";" not in lemma_rule:
            raise ValueError("Invalid rule format: ';' not in rule")
        casing, rule = lemma_rule.split(";", 1)
        if rule.startswith("a"):
            lemma = rule[1:]
        else:
            if "¦" not in rule:
                raise ValueError("Invalid rule format: '¦' not in rule")
            form = form.lower()
            rules, rule_sources = rule[1:].split("¦"), []
            assert len(rules) == 2
            for rule in rules:
                source, i = 0, 0
                while i < len(rule):
                    if rule[i] == "→" or rule[i] == "-":
                        source += 1
                    else:
                        assert rule[i] == "+"
                        i += 1
                    i += 1
                rule_sources.append(source)

            try:
                lemma, form_offset = "", 0
                for i in range(2):
                    j, offset = 0, (0 if i == 0 else len(form) - rule_sources[1])
                    while j < len(rules[i]):
                        if rules[i][j] == "→":
                            lemma += form[offset]
                            offset += 1
                        elif rules[i][j] == "-":
                            offset += 1
                        else:
                            assert rules[i][j] == "+"
                            lemma += rules[i][j + 1]
                            j += 1
                        j += 1
                    if i == 0:
                        lemma += form[rule_sources[0] : len(form) - rule_sources[1]]
            except Exception as e:
                if self.verbose:
                    print(
                        f"Caught an error: `{type(e).__name__}` with form: `{form}` and rule: `{lemma_rule}`, message: `{e}`"
                    )
                lemma = form

        for rule in casing.split("¦"):
            # The lemma is lowercased initially
            if rule == "↓0":
                continue
            # Empty lemma might generate empty casing rule
            if not rule:
                continue
            case, offset = rule[0], int(rule[1:])
            lemma = lemma[:offset] + (
                lemma[offset:].upper() if case == "↑" else lemma[offset:].lower()
            )

        return lemma


def min_edit_script(source: str, target: str, allow_copy: bool) -> str:
    a: List[List[Tuple[int, Union[None, str]]]] = [
        [(len(source) + len(target) + 1, None)] * (len(target) + 1)
        for _ in range(len(source) + 1)
    ]

    for i in range(0, len(source) + 1):
        for j in range(0, len(target) + 1):
            if i == 0 and j == 0:
                a[i][j] = (0, "")
            else:
                if (
                    allow_copy
                    and i
                    and j
                    and source[i - 1] == target[j - 1]
                    and a[i - 1][j - 1][0] < a[i][j][0]
                ):
                    a[i][j] = (a[i - 1][j - 1][0], a[i - 1][j - 1][1] + "→")
                if i and a[i - 1][j][0] < a[i][j][0]:
                    a[i][j] = (a[i - 1][j][0] + 1, a[i - 1][j][1] + "-")
                if j and a[i][j - 1][0] < a[i][j][0]:
                    a[i][j] = (a[i][j - 1][0] + 1, a[i][j - 1][1] + "+" + target[j - 1])
    return a[-1][-1][1]
