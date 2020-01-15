import requests
from bs4 import BeautifulSoup
import pprint
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation
from IPython.display import HTML

MONTHS = range(1, 2)
YEARS = range(2005, 2009)
USER = 'psychuil'


# https://towardsdatascience.com/bar-chart-race-in-python-with-matplotlib-8e687a5c8a41

pp = pprint.PrettyPrinter(indent=4)




def getLastFmData(user, year, month):
    df = pd.DataFrame(columns=['month', 'artist', 'count'])
    res = requests.get(f'https://www.last.fm/user/{user}/library/artists?from={year}-{month:02d}-01&rangetype=1month')
    soup = BeautifulSoup(res.content, 'lxml')

    rows = soup.find_all("a", {"class": 'link-block-target'})
    counts = soup.find_all("a", {"class": 'chartlist-count-bar-link'})

    for row in rows:
        try:
            for count in counts:
                if row.attrs['title'].replace(' ','+') in count.attrs['href']:
                    df = df.append({
                        'month': f'{year}{month:02d}',
                        'artist': row.attrs['title'],
                        'count': int(count.contents[3].text.replace('\n', ' ').replace('  ', '').replace(' scrobbles',''))
                    }, ignore_index=True)
        except:
            pass
    print(f'Done with {month:02d}/{year}')
    return df


history = pd.DataFrame(columns=['year', 'month', 'artist', 'count'])

fig, ax = plt.subplots(figsize=(15, 8))


def draw_barchart(month):
    dff = (df.query(f"month=='{month}'")
           .sort_values(by='count', ascending=False)
           .head(20))
    ax.clear()
    dff = dff[::-1]
    # ax.barh(dff['name'], dff['value'], color=[colors[group_lk[x]] for x in dff['name']])
    dx = dff['count'].max()
    for i, (value, name) in enumerate(zip(dff['count'], dff['artist'])):
        ax.text(value - dx, i, name, size=14, weight=600, ha='right', va='bottom')
        # ax.text(value - dx, i - .25, group_lk[name], size=10, color='#444444', ha='right', va='baseline')
        ax.text(value + dx, i, f'{value:,.0f}', size=14, ha='left', va='center')

    ax.text(1, 0.4, year, transform=ax.transAxes, color='#777777', size=46, ha='right', weight=800)
    ax.text(0, 1.06, 'Plays per month (thousands)', transform=ax.transAxes, size=12, color='#777777')
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.xaxis.set_ticks_position('top')
    ax.tick_params(axis='x', colors='#777777', labelsize=12)

    ax.set_yticks([])
    ax.margins(0, 0.01)
    ax.grid(which='major', axis='x', linestyle='-')
    ax.set_axisbelow(True)
    ax.text(0, 1.12, 'The most music by month 2005-2019',
            transform=ax.transAxes, size=24, weight=600, ha='left')

    ax.text(1, 0, 'by @pratapvardhan; credit @jburnmurdoch', transform=ax.transAxes, ha='right',
            color='#777777', bbox=dict(facecolor='white', alpha=0.8, edgecolor='white'))
    plt.box(False)


df = pd.DataFrame(columns=['month', 'artist', 'count'])
for year in YEARS:
    for month in MONTHS:
        df = df.append(getLastFmData(USER, year, month))




# draw_barchart('200601')
animator = animation.FuncAnimation(fig, draw_barchart, frames=df['month'].drop_duplicates().values)
HTML(animator.to_jshtml())
