import pandas as pd
from docsaidkit import dump_json, get_curdir, load_json

DIR = get_curdir(__file__)

"""
In Code39 table, there are nine characters in a pattern marked with 'b' and 'w'
which means 'black' and 'white', and three of those are capital that means wider lines.
Height & width rate could be 1:2 to 1:3.
"""


def load_39table():
    if (fp := DIR / 'code39_table.json').is_file():
        table39 = load_json(fp)
    else:
        df = pd.read_html('http://taggedwiki.zubiaga.org/new_content/ad336847cd67ef045e2106d1a89f2af8',
                          encoding='utf-8', header=0)

        df2 = pd.DataFrame(df[2])
        df2 = df2.rename(columns={df2.columns[0]: 'character',
                                  df2.columns[2]: 'pattern', })
        df2.drop(columns=['Code Details.1'], index=0, inplace=True)
        df2.reset_index(drop=True, inplace=True)

        df2.loc[df2['character'] == '(space)', 'character'] = ' '

        table39 = df2.to_dict()
        dump_json(table39, fp)

    return table39


CODE39 = load_39table()
