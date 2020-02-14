from bs4 import BeautifulSoup
import sys, requests, threading
import pandas as pd
from collections import defaultdict

MONTHS = range(1, 13)
YEARS = range(2005, 2021)
USER = 'psychuil'
# https://towardsdatascience.com/bar-chart-race-in-python-with-matplotlib-8e687a5c8a41


def getLastFmDF(user, years, months):
    threadList = []
    results = {}
    # history = pd.DataFrame(columns=['year', 'month', 'artist', 'count'])
    fetchDict = defaultdict(list)
    for year in years:
        fetchDict[year] = defaultdict(int)
        for month in months:
            fetchDict[year][month] = 0


    def getLastFmData(user, year, month):
        df = pd.DataFrame(columns=['month', 'artist', 'count'])
        res = requests.get(
            f'https://www.last.fm/user/{user}/library/artists?from={year}-{month:02d}-01&rangetype=1month')
        soup = BeautifulSoup(res.content, 'lxml')

        rows = soup.find_all("a", {"class": 'link-block-target'})
        counts = soup.find_all("a", {"class": 'chartlist-count-bar-link'})

        for row in rows:
            try:
                for count in counts:
                    if row.attrs['title'].replace(' ', '+') in count.attrs['href']:
                        df = df.append({
                            'id': f'{year}{month:02d}',
                            'year': int(year),
                            'month': f'{month:02d}',
                            'artist': row.attrs['title'],
                            'count': int(
                                count.contents[3].text.replace('\n', ' ').replace('  ', '').replace(' scrobbles', ''))
                        }, ignore_index=True)
            except:
                pass
        # print(f'Done with {month:02d}/{year}')
        fetchDict[year][month] = 1
        drawProgress(year)
        return df

    def appendToDf(user, year, month):
        newData = getLastFmData(user, year, month)
        results[f'{year}{month}'] = newData

    def countProg():
        count = 0
        sum = 0
        for year in fetchDict:
            for month in fetchDict[year]:
                count += 1
                if fetchDict[year][month] == 1:
                    sum += 1
        return int(sum / count * 100)

    def drawProgress(yearToGet):
        yearStrings = defaultdict(str)
        for year in fetchDict:
            yearString = f'[{countProg():02d}%] {year}'
            for month in fetchDict[year]:
                monthStatus = '✓' if fetchDict[year][month] == 1 else ' '
                yearString = f'{yearString} {month}{monthStatus}'
            yearStrings[year] = yearString
        sys.stdout.write(f'\r {yearStrings[yearToGet]}')
        sys.stdout.flush()




    finalDF = pd.DataFrame(columns=['id', 'year', 'month', 'artist', 'count'])
    for year in years:
        for month in months:
            threadList.append(threading.Thread(target=appendToDf, args=(user, year, month)))
    for thread in threadList:
        thread.start()
    for thread in threadList:
        thread.join()
    for month in results:
        finalDF = finalDF.append(results[month])
    print()
    return finalDF


if __name__ == '__main__':
    myTasteDF = getLastFmDF(USER, YEARS, MONTHS)

    myTasteDF.sort_values(by=['id', 'count'])
    print(myTasteDF)
    myTasteDF.to_csv(f'lastFM_{USER}.csv')
