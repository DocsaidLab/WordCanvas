import pandas as pd
from capybara import dump_json, get_curdir, load_json

DIR = get_curdir(__file__)


def load_128table():
    if (fp := DIR / 'code128_table.json').is_file():
        table128 = load_json(fp)
    else:
        df = pd.read_html('https://en.wikipedia.org/wiki/Code_128',
                          encoding='utf-8', header=0)

        df2 = pd.DataFrame(df[2])
        df2 = df2.rename(columns={df2.columns[2]: '_128A',
                                  df2.columns[3]: '_128B',
                                  df2.columns[4]: '_128C',
                                  df2.columns[5]: 'Font_position_code',
                                  df2.columns[6]: 'Font_position_latin_1',
                                  df2.columns[7]: 'bar_pattern',
                                  df2.columns[8]: 'bar_widths', })
        df2 = df2.drop([0]).reset_index(drop=True)
        df2 = df2.drop(['Hex value'], axis=1)
        df2.iloc[0, 1:3] = ''
        df2.iloc[108, 1:4] = 'Stop_pattern'
        table128 = df2.to_dict()
        dump_json(table128, fp)

    return table128
