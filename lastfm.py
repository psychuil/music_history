from bs4 import BeautifulSoup
import sys, requests, threading, argparse
import pandas as pd
from collections import defaultdict

parser = argparse.ArgumentParser(description='Fetches user listening history from last.fm')
parser.add_argument('--user', default='psychuil')
parser.add_argument('--years', default='2005-2021')
parser.add_argument('--filename', default=f'lastFM')
# https://towardsdatascience.com/bar-chart-race-in-python-with-matplotlib-8e687a5c8a41


def getLastFmDF(user, years, months):
    threadList = []
    results = {}
    fetchDict = defaultdict(list)
    for year in years:
        fetchDict[year] = defaultdict(int)
        for month in months:
            fetchDict[year][month] = 0

    def getLastFmData(user, year, month):
        df = pd.DataFrame(columns=['id','year', 'month', 'artist', 'count'])
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
                            'year': year,
                            'month': f'{month:02d}',
                            'artist': row.attrs['title'],
                            'count': int(
                                count.contents[3].text.replace('\n', ' ').replace('  ', '').replace(' scrobbles', ''))
                        }, ignore_index=True)
            except:
                pass
        return df

    def appendToDf(user, year, month):
        newData = getLastFmData(user, year, month)
        results[f'{year}{month}'] = newData
        fetchDict[year][month] = 1
        drawProgress(year)

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
            yearString = f'({year})'
            for month in fetchDict[year]:
                monthStatus = '  ' if fetchDict[year][month] != 1 else f'{month:02d}'
                yearString = f'{yearString} {monthStatus}'
            yearStrings[year] = yearString
        sys.stdout.write(f'\r[{countProg():02d}%] {yearStrings[yearToGet]}')
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
    args = parser.parse_args()
    years = args.years.split('-')
    years = range(int(years[0]),int(years[1]))
    print(f'Fetching data for {args.user} for {list(years)}')
    myTasteDF = getLastFmDF(args.user, years, range(1, 13))
    myTasteDF.sort_values(by=['id', 'count'])
    print(myTasteDF)
    myTasteDF.to_csv(f'{args.filename}_{args.user}.csv')
